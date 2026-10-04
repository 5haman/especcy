#!/usr/bin/env python3
"""Check exported electrical artifacts against the firmware and existing CAD.

The known USB/switch fit conflict is reported, never excluded from KiCad DRC.
These checks do not simulate the circuit or replace physical qualification.
"""
import copy
import csv
import itertools
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from design import CARRIER, FIXTURE, SCHEMATICS

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def save(name, report):
    (ROOT / 'reports' / name).write_text(json.dumps(report, indent=2) + '\n')


def netlist(name):
    return ET.parse(ROOT / 'reports' / (name + '-netlist.xml')).getroot()


def assignments(xml):
    return {(p.get('ref'), p.get('pin')): n.get('name').lstrip('/')
            for n in xml.find('nets') for p in n}


def validate(xml, parts):
    components = {p.get('ref'): p for p in xml.find('components')}
    require(set(components) == {p['ref'] for p in parts}, 'Component inventory differs')
    nets = assignments(xml)
    for part in parts:
        ref = part['ref']
        component = components[ref]
        fields = {f.get('name'): f.text or '' for f in component.find('fields')}
        require(component.findtext('footprint') == 'Study:' + part['footprint'], ref + ' footprint differs')
        require(fields['MPN'] == part['mpn'], ref + ' MPN differs')
        for pin, expected in part['nets'].items():
            actual = nets.get((ref, pin), '')
            require(actual.startswith('unconnected-') if expected is None else actual == expected,
                    ref + ':' + pin + ' expected ' + str(expected) + ', found ' + actual)
    return nets


def firmware_check(xml):
    nets = assignments(xml)
    functions = {int(p.get('pin')): p.get('pinfunction', '')
                 for n in xml.find('nets') for p in n if p.get('ref') == 'U1'}
    gpio = {int(m.group(1)): nets[('U1', str(pin))] for pin, function in functions.items()
            if (m := re.search(r'(?:^|/)IO(\d+)', function))}
    main = (REPO / 'firmware/main/main.cpp').read_text()
    header = (REPO / 'firmware/common/spectrum.h').read_text()
    pins = [int(x) for x in re.findall(r'GPIO_NUM_(\d+)', re.search(r'inputs\[\].*?\{(.*?)\}', main).group(1))]
    buttons = re.findall(r'(\w+)\s*=\s*(\d+)', re.search(r'enum Button.*?\{(.*?)\}', header).group(1))
    require(len(pins) == len(buttons) == 6, 'Six controls required')
    for name, bit in buttons:
        index = int(math.log2(int(bit)))
        require(gpio[pins[index]] == 'BTN_' + name.upper(), name + ' firmware/netlist mismatch')
    lcd = (REPO / 'firmware/main/lcd.cpp').read_text()
    for name in ('DC', 'RST', 'BL'):
        pin = int(re.search(name + r'\s*=\s*GPIO_NUM_(\d+)', lcd).group(1))
        require(gpio[pin] == 'LCD_' + name, name + ' firmware/netlist mismatch')
    for setting, name in [('mosi', 'DIN'), ('sclk', 'CLK'), ('spics', 'CS')]:
        pin = int(re.search(setting + r'_io_num\s*=\s*(\d+)', lcd).group(1))
        require(gpio[pin] == 'LCD_' + name, setting + ' firmware/netlist mismatch')
    require('GPIO_PULLUP_ENABLE' in main and '!gpio_get_level(inputs[i])' in main,
            'Active-low internal pull-up contract changed')
    return dict(buttons={name: pins[int(math.log2(int(bit)))] for name, bit in buttons},
                lcd={net: pin for pin, net in gpio.items() if net.startswith('LCD_')})


def fixture_calculations():
    def threshold(state, rs=523000, rb=1000000, rr=10000, rf=1000000,
                  reference=2.048, output_high=3.3, bias=0, offset=0):
        out = output_high if state == 'enable' else 0
        plus = (reference / rr + out / rf) / (1 / rr + 1 / rf)
        internal_hys = .0035 if state == 'enable' else -.0035
        return (plus + internal_hys + offset + bias * (rs * rb / (rs + rb) + rr * rf / (rr + rf))) * (1 + rs / rb)
    limits = {}
    for state in ('enable', 'disable'):
        values = [threshold(state, 523000 * rs, 1000000 * rb, 10000 * rr, 1000000 * rf,
                            2.048 * reference, output, bias, offset)
                  for rs, rb, rr, rf, reference, output, bias, offset in itertools.product(
                      (0.99, 1.01), (0.99, 1.01), (0.99, 1.01), (0.99, 1.01),
                      (0.99, 1.01), (3.135, 3.465), (-20e-9, 20e-9), (-.013, .013))]
        limits[state] = [round(min(values), 4), round(max(values), 4)]
    # Output saturation can raise the disable point; bound it separately.
    limits['disable'][1] += round(.35 * 10000 / 1010000 * 1.523, 4)
    return dict(nominal_enable_v=round(threshold('enable'), 4),
                nominal_disable_v=round(threshold('disable'), 4),
                conservative_threshold_ranges_v=limits,
                sense_current_at_3v3_ua=round(3.3 / 1523000 * 1e6, 3),
                fixture_off_input_tolerance_v=7,
                assumptions='1% resistors; local 3.3V +/-5%; reference +/-1% allowance for initial error/drift/current over -40..85C; comparator +/-8mV offset plus 2..17mV internal hysteresis; +/-20nA input bias is a bench allowance (only typical 2pA specified); disable output 0..0.35V allowance (datasheet limit tested at 5V). Arithmetic bounds, not guaranteed thresholds or simulation.',
                bench_gate='Confirm thresholds, hysteresis, both UART directions, power-off leakage and brownout with the selected adapter and buffer.')


def static_checks():
    result = dict(status='pass', checks=[], fabrication_ready=False)
    for name, spec in SCHEMATICS.items():
        validate(netlist(name), spec['parts'])
        erc = json.loads((ROOT / 'reports' / (name + '-erc.json')).read_text())
        require(not erc['ignored_checks'], name + ' has disabled ERC rules')
        require(not any(s['violations'] for s in erc['sheets']), name + ' ERC violations')
        with (ROOT / (name + '-bom.csv')).open() as f:
            rows = list(csv.DictReader(f))
            bom = {p['ref']: p for p in rows}
        require(len(rows) == len(bom), name + ' duplicate BOM references')
        require(set(bom) == {p['ref'] for p in spec['parts']}, name + ' BOM inventory')
        for part in spec['parts']:
            require(all(bom[part['ref']][key] == part[key] for key in
                        ('value', 'mpn', 'manufacturer', 'footprint', 'kind', 'source', 'note')),
                    name + ' BOM field mismatch ' + part['ref'])
            require(bom[part['ref']]['quantity'] == '1', name + ' BOM quantity')
        result['checks'].append(name + ': native netlist, pin/NC/MPN/BOM parity, zero ERC violations and disabled rules')
    carrier = netlist('carrier')
    result['firmware'] = firmware_check(carrier)
    parameters = json.loads((REPO / 'hardware/cad/parameters.json').read_text())
    require(next(p for p in CARRIER if p['ref'] == 'U1')['mpn'] == parameters['esp32']['part'], 'Selected WROOM changed')
    with (ROOT / 'assembly-bom.csv').open() as f:
        assembly = list(csv.DictReader(f))
    require(len(assembly) == 1 and assembly[0]['mpn'] == '26117' and assembly[0]['quantity'] == '1'
            and '26117' in parameters['lcd']['part'], 'Selected LCD assembly BOM changed')
    fixture = netlist('fixture')
    sense = next(n for n in fixture.find('nets') if n.get('name').lstrip('/') == 'SENSE_3V3')
    require({(p.get('ref'), p.get('pin')) for p in sense} == {('J1', '2'), ('R2', '1')},
            'Sense pad has a direct supply or unintended connection')
    # Mutation checks show that cross-artifact validation rejects a wrong GPIO,
    # a swapped LCD line and an accidental adapter VCC connection.
    for name, ref, pin, net in [('carrier', 'U1', '11', 'BTN_DOWN'),
                               ('carrier', 'J2', '3', 'LCD_CLK'),
                               ('fixture', 'J2', '1', 'FX_3V3')]:
        xml = copy.deepcopy(netlist(name))
        source = next(n for n in xml.find('nets') if any(p.get('ref') == ref and p.get('pin') == pin for p in n))
        p = next(p for p in source if p.get('ref') == ref and p.get('pin') == pin)
        source.remove(p)
        next(n for n in xml.find('nets') if n.get('name').lstrip('/') == net).append(p)
        try:
            validate(xml, SCHEMATICS[name]['parts'])
        except AssertionError:
            continue
        raise AssertionError('Miswire probe was accepted: ' + ref + ':' + pin)
    result['checks'].append('Three intentional GPIO/LCD/adapter-power miswires rejected')
    drc = json.loads((ROOT / 'reports/carrier-drc.json').read_text())
    require(not drc['schematic_parity'], 'Native board/schematic parity errors')
    # Keep the actual mechanical conflict visible. Any additional placement
    # violation fails this handoff, including a moved or different USB conflict.
    known = drc['violations']
    require(len(known) == 1 and known[0]['type'] == 'pth_inside_courtyard'
            and {i['description'] for i in known[0]['items']} ==
                {'PTH pad SH [/GND] of J1', 'Footprint SW2'}, 'Unexpected placement DRC findings')
    require(not any(v.get('excluded', False) for v in known), 'DRC exclusion hides fit conflict')
    result['drc'] = dict(placement_conflicts=known, unrouted_connections=len(drc['unconnected_items']),
                         schematic_parity_issues=0, disposition='USB shell stake / Down switch fit gate remains OPEN. Unconnected items are expected on this unrouted board. No fabrication release.')
    save('electrical-checks.json', result)
    theta = {'DBV_EVM_reference': 100.8, 'DBV_JEDEC_reference': 231.1}
    scenarios = [dict(vin_v=vin, load_ma=load, ambient_c=ambient,
                      ldo_loss_w=round((vin - 3.3) * load / 1000, 4),
                      reference_tj_c={name: round(ambient + (vin - 3.3) * load / 1000 * value, 1)
                                      for name, value in theta.items()})
                 for vin, load, ambient in itertools.product((4.75, 5, 5.25), (100, 250, 560, 1000), (25, 40))]
    save('power-budget.json', dict(status='thermal acceptance OPEN',
        recommended_max_tj_c=125, theta_reference_c_per_w=theta,
        budget_ma={'ESP32_supply_capability_guidance': 500, 'LCD_FAQ_max': 60, 'total': 560},
        scenarios=scenarios, fuse_hold_ma_at_c={'23': 750, '40': 630, '50': 570, '60': 530, '70': 420, '85': 350},
        tvs=dict(working_peak_v=5.0, minimum_breakdown_v=6.0, max_clamp_at_1a_v=9.8,
                 disposition='Not LDO overvoltage protection. The 5.25V thermal scenario exceeds the selected TVS working-peak rating; restrict the prototype source to <=5.0V or reselect protection before qualification. ESD performance untested.'),
        assumptions='Supply capability budget is not measured consumption. Vin is voltage at the LDO after fuse/cable losses. Reference thermal boards do not establish this tiny carrier/enclosure thermal resistance. Excludes ESP32/display/PPTC self-heating.',
        release_gate='Measure startup, display-on and sustained Dizzy current, input/3V3 transients and junction estimate in the enclosure at agreed ambient. Meet all recommended limits with margin; do not rely on thermal shutdown. Fuse derating must also pass. If it fails, revisit the selected LDO strategy explicitly.'))
    save('fixture-analysis.json', fixture_calculations())
    print('ELECTRICAL_CHECKS_OK: two ERC-clean circuits; firmware/BOM/netlist parity; known fit gate retained')


def board_checks():
    import pcbnew as pcb
    import wx
    app = wx.App(False)
    board = pcb.LoadBoard(str(ROOT / 'carrier.kicad_pcb'))
    require(board.GetCopperLayerCount() == 2 and abs(pcb.ToMM(board.GetDesignSettings().GetBoardThickness()) - .8) < 1e-6, 'Board stack differs')
    require(not list(board.GetTracks()), 'Placement board unexpectedly routed')
    expected_edges = json.loads((ROOT / 'reports/outline.json').read_text())['edges']
    actual_edges = list(board.GetDrawings())
    require(len(actual_edges) == len(expected_edges), 'Carrier outline edge count')
    for expected in expected_edges:
        points = expected['points']
        def matches(edge):
            start = [pcb.ToMM(edge.GetStart().x), pcb.ToMM(edge.GetStart().y)]
            end = [pcb.ToMM(edge.GetEnd().x), pcb.ToMM(edge.GetEnd().y)]
            same = any(all(abs(a - b) < 2e-6 for actual, target in
                           zip((start, end), endpoints) for a, b in zip(actual, target))
                       for endpoints in ((points[0], points[2]), (points[2], points[0])))
            if expected['kind'] == 'arc':
                mid = edge.GetArcMid()
                same = same and abs(pcb.ToMM(mid.x) - points[1][0]) < 2e-6 and abs(pcb.ToMM(mid.y) - points[1][1]) < 2e-6
            return same
        require(any(matches(edge) for edge in actual_edges), 'Native CAD outline geometry differs')
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    require(set(footprints) == {p['ref'] for p in CARRIER}, 'Board inventory differs')
    nets = assignments(netlist('carrier'))
    pads = []
    for part in CARRIER:
        f = footprints[part['ref']]
        x, y, side, angle = part['placement']
        require(abs(pcb.ToMM(f.GetPosition().x) - x) < 1e-5 and
                abs(38 - pcb.ToMM(f.GetPosition().y) - y) < 1e-5, part['ref'] + ' position differs')
        require(f.GetLayer() == (pcb.F_Cu if side == 'F' else pcb.B_Cu), part['ref'] + ' side differs')
        for p in f.Pads():
            number = p.GetNumber()
            require(p.GetNetname().lstrip('/') == nets[(part['ref'], number)], part['ref'] + ':' + number + ' pad net differs')
            pads.append(dict(ref=part['ref'], pin=number, net=p.GetNetname().lstrip('/'),
                cad_xy_mm=[round(pcb.ToMM(p.GetPosition().x), 5), round(38 - pcb.ToMM(p.GetPosition().y), 5)],
                size_mm=[pcb.ToMM(p.GetSize().x), pcb.ToMM(p.GetSize().y)], side=side))
    pogo = sorted((p for p in pads if p['ref'] == 'J3'), key=lambda p: int(p['pin']))
    require([p['cad_xy_mm'][0] for p in pogo] == [15.75, 14.25, 12.75, 11.25, 9.75, 8.25], 'Pogo underside orientation differs')
    require(all(6.9 < p['cad_xy_mm'][0] - .525 and p['cad_xy_mm'][0] + .525 < 17.1
                and 7 < p['cad_xy_mm'][1] - .75 and p['cad_xy_mm'][1] + .75 < 9.8 for p in pogo), 'Pogo opening access')
    save('board-checks.json', dict(status='pass', copper_layers=2, thickness_mm=.8, footprints=len(footprints),
        tracks=0, pad_net_parity=True, native_outline_parity=True, pads=pads, pogo_view='Front projection CAD X decreases from pad1 to pad6; underside with USB at bottom shows pad1 at left.'))
    print('NATIVE_BOARD_CHECKS_OK: 21 footprints, exact pad nets, two layers, no routes, pogo access')


def fit_checks():
    from build import FREECAD_PYTHON
    sys.path.append(str(Path(FREECAD_PYTHON).resolve().parents[1] / 'lib'))
    import FreeCAD as App
    import Part
    doc = App.openDocument(str(REPO / 'hardware/cad/models/speccy_micro.FCStd'))
    native = doc.getObject('CarrierPCB').Shape
    board = Part.read(str(ROOT / '.cache/carrier-board.step'))
    preview = Part.read(str(ROOT / 'previews/carrier.step'))
    require(board.isValid() and preview.isValid(), 'STEP parse/shape validity')
    core_thickness = board.BoundBox.ZLength
    # KiCad exports the dielectric body without the two copper/mask stacks.
    dz = 4.8 + (.8 - core_thickness) / 2 - board.BoundBox.ZMin
    board.translate(App.Vector(0, 0, dz))
    preview.translate(App.Vector(0, 0, dz))
    require(abs(board.BoundBox.XLength - native.BoundBox.XLength) < 1e-5 and
            abs(board.BoundBox.YLength - native.BoundBox.YLength) < 1e-5 and
            0 < core_thickness <= .8, 'Carrier STEP envelope differs')
    # Coincident STEP/native curves produce unstable OCC boolean results.
    # Compare the actual board drawing separately, then check STEP containment
    # at a 0.5mm XY grid. Expected drill/slot holes may remove interior points.
    samples = 0
    for ix, iy in itertools.product(range(49), range(77)):
        point = App.Vector(ix / 2, iy / 2, 5.2)
        if board.isInside(point, 1e-5, False):
            require(native.isInside(point, 1e-5, True), 'STEP XY extends outside native carrier')
            samples += 1
    obstacles = [doc.getObject(name) for name in ('LowerWithBosses', 'UpperFinished', 'LCDPCB')]
    obstacles += [o for o in doc.Objects if o.Name.startswith('LCDBackIC')]
    findings = []
    for part in CARRIER:
        if not any(part['body']):
            continue
        x, y, side, angle = part['placement']
        width, length, height = part['body']
        if angle % 180 == 90:
            width, length = length, width
        if part['ref'] == 'J1':
            y -= 1.175  # GCT body centre relative to footprint datum
        z = 5.6 if side == 'F' else 4.8 - height
        body = Part.makeBox(width, length, height, App.Vector(x - width / 2, y - length / 2, z))
        for obstacle in obstacles:
            common = body.common(obstacle.Shape).Volume
            distance = body.distToShape(obstacle.Shape)[0] if obstacle.Name == 'LCDPCB' or common > 1e-6 else None
            if common > 1e-6 or (distance is not None and distance < .3):
                findings.append(dict(ref=part['ref'], against=obstacle.Name,
                    overlap_mm3=round(common, 6), clearance_mm=round(distance, 4) if distance is not None else None))
    save('fit-checks.json', dict(status='physical acceptance OPEN',
        carrier_step_valid=True, component_step_valid=True, component_step_solids=len(preview.Solids),
        step_to_cad_z_translation_mm=round(dz, 6), carrier_envelope_mm=[20.8, 34.8, .8],
        dielectric_core_thickness_mm=round(core_thickness, 6),
        actual_outline_xy_mm=[round(native.BoundBox.XLength, 6), round(native.BoundBox.YLength, 6)],
        contained_step_grid_points=samples,
        conservative_body_findings=findings,
        open_gates=[
            'TE recommended pressing tip diameter 1.00mm and alignment <=0.20mm; existing stem diameter 1.80mm.',
            'Switch nominal top Z6.25 vs stem bottom Z6.30 leaves 0.05mm. Drawing general tolerance gives possible top Z6.45: 0.15mm preload/interference; travel nominal 0.15mm.',
            'GCT 1.00mm nominal shell stakes pass through 0.80mm carrier: nominal protrusion 0.20mm, up to 0.40mm with the drawing general +/-0.20mm tolerance before PCB tolerance. One stake lies inside Down switch courtyard; check physical contact/assembly.',
            'USB maximum envelope reaches the opening right edge (zero nominal lateral margin); cable/overmold access and socket tolerances unqualified.',
            'Pogo centres move from legacy Y8.45 to Y8.25, within the same underside opening; mirrored numbering now defined electrically.',
            'LCD revision, connector-removal depth, physical pad order and eight-wire solder access/bend radius need samples.',
            'Passives use conservative family envelopes; selected-part DC bias, package tolerance, hand assembly and supplier availability need qualification.',
            'Nominal USB/switch STEP shapes are local envelope approximations. Other models come from KiCad; preview is not vendor-certified assembly evidence.',
            'Antenna cutout follows unchanged CAD; full RF clearance is not preserved. Keep radios disabled.'],
        acceptance='No enclosure edits, routing, Gerbers, procurement or fabrication release. Resolve recorded gates before any claim of physical fit.'))
    App.closeDocument(doc.Name)
    print('STEP_FIT_CHECKS_OK: original outline preserved, native STEP reopens; physical conflicts recorded')


if __name__ == '__main__':
    if sys.argv[1:] == ['--board']:
        board_checks()
    elif sys.argv[1:] == ['--fit']:
        fit_checks()
    else:
        static_checks()
