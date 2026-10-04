#!/usr/bin/env python3
"""Rebuild the electrical study with installed KiCad 10 and FreeCAD.

Generated files are editable. Rebuilding replaces them; edit design.py to
preserve a change across builds. Manufacturer documents are not downloaded.
"""
import copy
import csv
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SHARE = Path(os.environ.get('SPECCY_KICAD_SHARE', '/Applications/KiCad/KiCad.app/Contents/SharedSupport'))
KICAD_PYTHON = os.environ.get('SPECCY_KICAD_PYTHON', '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3')
FREECAD_PYTHON = os.environ.get('SPECCY_FREECAD_PYTHON', '/Applications/FreeCAD.app/Contents/Resources/bin/python')


class Atom(str):
    """An unquoted S-expression token."""


def parse(source):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', source))

    def read(token):
        if token != '(':
            if token == ')':
                raise ValueError('Unexpected closing parenthesis')
            return json.loads(token) if token.startswith('"') else Atom(token)
        result = []
        for token in tokens:
            if token == ')':
                return result
            result.append(read(token))
        raise ValueError('Unclosed S-expression')

    result = read(next(tokens))
    if next(tokens, None) is not None:
        raise ValueError('Trailing S-expression')
    return result


def emit(value, depth=0):
    if isinstance(value, list):
        if all(not isinstance(x, list) for x in value):
            return '(' + ' '.join(emit(x) for x in value) + ')'
        head = []
        while value and not isinstance(value[len(head)], list):
            head.append(value[len(head)])
            if len(head) == len(value):
                break
        rest = value[len(head):]
        return '(' + ' '.join(emit(x) for x in head) + ''.join('\n' + '  ' * (depth + 1) + emit(x, depth + 1) for x in rest) + ')'
    if isinstance(value, Atom):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(round(value, 6)) if isinstance(value, float) else str(value)


def node(head, *values):
    return [Atom(head), *values]


def children(tree, key):
    return [x for x in tree if isinstance(x, list) and x and x[0] == key]


def child(tree, key, default=None):
    return next(iter(children(tree, key)), default)


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'especcy/electronics/' + name))


_libraries = {}


def library_symbol(lib_id):
    library, name = lib_id.split(':')
    if library not in _libraries:
        _libraries[library] = {x[1]: x for x in children(parse((SHARE / 'symbols' / (library + '.kicad_sym')).read_text()), 'symbol')}
    symbols = _libraries[library]

    def flatten(name):
        symbol = copy.deepcopy(symbols[name])
        parent = child(symbol, 'extends')
        if parent:
            inherited = flatten(parent[1])
            own_properties = {x[1] for x in children(symbol, 'property')}
            inherited_name = inherited[1]
            for item in inherited[2:]:
                if item[0] == 'property' and item[1] in own_properties:
                    continue
                if item[0] == 'symbol':
                    item[1] = name + item[1][len(inherited_name):]
                if item[0] in ('symbol', 'property') or not child(symbol, item[0]):
                    symbol.append(item)
            symbol.remove(parent)
        return symbol

    result = flatten(name)
    result[1] = lib_id
    return result


def pins(symbol, unit=1):
    result = []
    for group in children(symbol, 'symbol'):
        group_unit, style = map(int, group[1].rsplit('_', 2)[1:])
        if group_unit in (0, unit) and style in (0, 1):
            result.extend(children(group, 'pin'))
    return result


def pin_numbers(pin):
    number = str(child(pin, 'number')[1])
    return number.strip('[]').split(',') if number.startswith('[') else [number]


def effects(size=1.0, justify=None, hide=False):
    values = [node('font', node('size', size, size))]
    if justify:
        values.append(node('justify', *(Atom(word) for word in justify.split())))
    if hide:
        values.append(node('hide', Atom('yes')))
    return node('effects', *values)


def symbols_for_project():
    from design import SYMBOLS
    result = {}
    for alias, lib_id in SYMBOLS.items():
        symbol = library_symbol(lib_id)
        old_name = lib_id.split(':')[1]
        symbol[1] = alias
        for group in children(symbol, 'symbol'):
            group[1] = alias + group[1][len(old_name):]
        for prop in children(symbol, 'property'):
            if prop[1] == 'Value':
                prop[2] = alias
            if prop[1] == 'Footprint':
                prop[2] = ''
            if prop[1] == 'ki_fp_filters':
                # The copied footprints use project aliases, not upstream names.
                prop[2] = ''
        result[alias] = symbol
    return result


def write_schematic(name, spec, symbols):
    root_uid = uid(name)
    used = {p['symbol'] for p in spec['parts']} | {'Flag'}
    embedded = []
    for alias in sorted(used):
        symbol = copy.deepcopy(symbols[alias])
        symbol[1] = 'Study:' + alias
        embedded.append(symbol)
    sheet = node('kicad_sch', node('version', 20250114), node('generator', 'eeschema'),
                 node('generator_version', '10.0'), node('uuid', root_uid),
                 node('paper', spec['paper']),
                 node('title_block', node('title', spec['title']), node('date', spec['date']),
                      node('rev', spec['revision']), node('company', 'Especcy'),
                      node('comment', 1, 'Design study; physical acceptance and fabrication release open')),
                 node('lib_symbols', *embedded))
    connected = set()

    def add_part(part):
        symbol = symbols[part['symbol']]
        placements = part['schematic']
        if isinstance(placements, tuple):
            placements = [(1, *placements)]
        for unit, x, y in placements:
            ident = uid(name + '/' + part['ref'] + '/' + str(unit))
            instance = node('symbol', node('lib_id', 'Study:' + part['symbol']),
                            node('at', x, y, 0), node('unit', unit),
                            node('exclude_from_sim', Atom('no')),
                            node('in_bom', Atom('no' if part['kind'] == 'flag' else 'yes')),
                            node('on_board', Atom('no' if part['kind'] == 'flag' else 'yes')),
                            node('dnp', Atom('no')), node('uuid', ident))
            # Keep display fields outside bodies/wires; leave sourcing fields hidden.
            ref_at, value_at = (x, y - 5.08), (x, y + 5.08)
            field_justify = None
            if part['symbol'] == 'ESP32':
                ref_at, value_at = (x - 10.16, y - 40.64), (x + 12.7, y - 40.64)
            elif part['symbol'] in ('R', 'C', 'Fuse'):
                ref_at, value_at = (x + 4.445, y - 1.27), (x + 4.445, y + 1.27)
                field_justify = 'left'
            elif part['symbol'] in ('LCD', 'Pogo', 'Adapter', 'PowerPort'):
                pin_y = [float(child(p, 'at')[2]) for p in pins(symbol, unit)]
                ref_at, value_at = (x, y - max(pin_y) - 5.08), (x, y - min(pin_y) + 7.62)
            elif part['symbol'] == 'Buffer':
                offset = 12.7 if unit == 3 else 2.54
                ref_at, value_at = (x + offset, y - 12.7), (x + offset, y + 10.16)
            elif part['symbol'] == 'Flag':
                value_at = (x + 3.81, y)
                field_justify = 'left'
            elif part['symbol'] in ('USB', 'LDO', 'Comparator', 'Reference'):
                pin_y = [float(child(p, 'at')[2]) for p in pins(symbol, unit)]
                ref_at, value_at = (x, y - max(pin_y) - 5.08), (x, y - min(pin_y) + 7.62)
            instance.extend([
                node('property', 'Reference', part['ref'], node('at', *ref_at, 0), effects(justify=field_justify)),
                node('property', 'Value', part['value'], node('at', *value_at, 0), effects(justify=field_justify)),
                node('property', 'Footprint', 'Study:' + part['footprint'] if part['footprint'] else '',
                     node('at', x, y, 0), effects(hide=True)),
                node('property', 'Datasheet', part['source'], node('at', x, y, 0), effects(hide=True)),
                node('property', 'MPN', part['mpn'], node('at', x, y, 0), effects(hide=True)),
                node('property', 'Manufacturer', part['manufacturer'], node('at', x, y, 0), effects(hide=True)),
                node('property', 'Kind', part['kind'], node('at', x, y, 0), effects(hide=True)),
                node('property', 'Design note', part['note'], node('at', x, y, 0), effects(hide=True)),
            ])
            for pin in pins(symbol, unit):
                numbers = pin_numbers(pin)
                assigned = [part['nets'][number] for number in numbers]
                if len(set(assigned)) != 1:
                    raise ValueError('Stacked pins must share a net: ' + part['ref'])
                net = assigned[0]
                px, py, angle = map(float, child(pin, 'at')[1:])
                start = (round(x + px, 6), round(y - py, 6))
                pin_id = str(child(pin, 'number')[1])
                instance.append(node('pin', pin_id, node('uuid', uid(ident + '/' + pin_id))))
                if net is None:
                    sheet.append(node('no_connect', node('at', *start), node('uuid', uid(ident + '/nc/' + pin_id))))
                elif (start, net) not in connected:
                    connected.add((start, net))
                    end = (round(start[0] - 2.54 * math.cos(math.radians(angle)), 6),
                           round(start[1] + 2.54 * math.sin(math.radians(angle)), 6))
                    sheet.append(node('wire', node('pts', node('xy', *start), node('xy', *end)),
                                      node('stroke', node('width', 0), node('type', Atom('default'))),
                                      node('uuid', uid(ident + '/wire/' + pin_id))))
                    label_angle = 90 if angle in (90, 270) else 0
                    label_justify = 'right bottom' if angle in (0, 90) else 'left bottom'
                    sheet.append(node('label', net, node('at', *end, label_angle),
                                      effects(0.9, label_justify), node('uuid', uid(ident + '/label/' + pin_id))))
            instance.append(node('instances', node('project', name,
                node('path', '/' + root_uid, node('reference', part['ref']), node('unit', unit)))))
            sheet.append(instance)

    for part in spec['parts']:
        add_part(part)
    from design import part
    for index, (net, x, y) in enumerate(spec['flags'], 1):
        add_part(part('#FLG' + str(index), 'Flag', 'PWR_FLAG', '', '', '',
                      {1: net}, (x, y), kind='flag', note='External power source for ERC; no physical component.'))
    for x, y, text in spec['notes']:
        sheet.append(node('text', text, node('at', x, y, 0), effects(1.1, 'left'), node('uuid', uid(name + '/note/' + text))))
    sheet.append(node('embedded_fonts', Atom('no')))
    (ROOT / (name + '.kicad_sch')).write_text(emit(sheet) + '\n')


def write_projects(symbols):
    from design import SCHEMATICS, DATE, REVISION
    lib = node('kicad_symbol_lib', node('version', 20251024), node('generator', 'kicad_symbol_editor'),
               node('generator_version', '10.0'), *symbols.values())
    (ROOT / 'Study.kicad_sym').write_text(emit(lib) + '\n')
    (ROOT / 'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Study") (type "KiCad") (uri "${KIPRJMOD}/Study.kicad_sym") (options "") (descr "Project symbol snapshot; see NOTICE")))\n')
    (ROOT / 'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Study") (type "KiCad") (uri "${KIPRJMOD}/Study.pretty") (options "") (descr "Project footprint snapshot; see NOTICE")))\n')
    for name, spec in SCHEMATICS.items():
        spec = dict(spec, date=DATE, revision=REVISION)
        write_schematic(name, spec, symbols)
        project = json.loads((SHARE / 'template/kicad.kicad_pro').read_text())
        project['meta']['filename'] = name + '.kicad_pro'
        project['sheets'] = [[uid(name), spec['title']]]
        project['text_variables'] = {'DESIGN_STATUS': 'UNROUTED STUDY - NOT FOR FABRICATION'}
        project['erc'] = dict(erc_exclusions=[], rule_severities={
            key: 'warning' for key in ('single_global_label', 'four_way_junction',
                                      'simulation_model_issue', 'footprint_filter')})
        project['net_settings']['classes'] = [dict(name='Default', clearance=0.15, track_width=0.2,
            via_diameter=0.6, via_drill=0.3, microvia_diameter=0.3, microvia_drill=0.1,
            diff_pair_width=0.2, diff_pair_gap=0.25, diff_pair_via_gap=0.25, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)', wire_width=6, bus_width=12)]
        (ROOT / (name + '.kicad_pro')).write_text(json.dumps(project, indent=2) + '\n')


def cad_outline():
    sys.path.append(str(Path(FREECAD_PYTHON).resolve().parents[1] / 'lib'))
    import FreeCAD as App
    import Part
    doc = App.openDocument(str(REPO / 'hardware/cad/models/speccy_micro.FCStd'))
    shape = doc.getObject('CarrierPCB').Shape
    face = next(f for f in shape.Faces if abs(f.CenterOfMass.z - 4.8) < 1e-6 and abs(f.normalAt(0, 0).z) > 0.99)
    edges = []
    for edge in face.OuterWire.Edges:
        points = [edge.valueAt(t) for t in (edge.FirstParameter, (edge.FirstParameter + edge.LastParameter) / 2, edge.LastParameter)]
        edges.append(dict(kind='arc' if isinstance(edge.Curve, Part.Circle) else 'line',
                          points=[[round(p.x, 7), round(38 - p.y, 7)] for p in points]))
    report = dict(source='hardware/cad/models/speccy_micro.FCStd:CarrierPCB',
                  coordinate_transform='KiCad X = CAD X; KiCad Y = 38 - CAD Y; front PCB surface CAD Z=5.6',
                  edges=edges, volume_mm3=shape.Volume,
                  envelope_mm=[shape.BoundBox.XLength, shape.BoundBox.YLength, shape.BoundBox.ZLength])
    (ROOT / 'reports/outline.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'models').mkdir(exist_ok=True)
    switch = Part.makeBox(3.0, 2.6, 0.45, App.Vector(-1.5, -1.3, 0))
    switch = switch.fuse(Part.makeCylinder(0.4, 0.2, App.Vector(0, 0, 0.45)))
    switch.exportStep(str(ROOT / 'models/te-switch-nominal.step'))
    # Nominal shell envelope only: the installed GCT footprint has no model.
    # STEP uses Y opposite to footprint coordinates. No connector detail claim.
    usb = Part.makeBox(7.4, 5.55, 2.35, App.Vector(-3.7, -3.95, 0))
    usb.exportStep(str(ROOT / 'models/usb3076-nominal.step'))
    App.closeDocument(doc.Name)


def native_footprints():
    import pcbnew as pcb
    import wx
    from design import FOOTPRINTS
    app = wx.App(False)
    dest = ROOT / 'Study.pretty'
    dest.mkdir(exist_ok=True)
    writer = pcb.PCB_IO_MGR.FindPlugin(pcb.PCB_IO_MGR.KICAD_SEXP)
    for name, source in FOOTPRINTS.items():
        library, source_name = source.split(':')
        footprint = pcb.FootprintLoad(str(SHARE / 'footprints' / (library + '.pretty')), source_name)
        if footprint is None:
            raise RuntimeError('Missing installed footprint: ' + source)
        footprint.SetFPID(pcb.LIB_ID('Study', name))
        if name == 'USB':
            footprint.Models().clear()
            model = pcb.FP_3DMODEL()
            model.m_Filename = '${KIPRJMOD}/models/usb3076-nominal.step'
            footprint.Models().push_back(model)
        if name == 'ESP32':
            # Retain the thermal-pad array but use 0.30mm drilled holes,
            # matching the provisional board minimum instead of 0.20mm.
            for pad in footprint.Pads():
                if pad.GetAttribute() == pcb.PAD_ATTRIB_PTH:
                    pad.SetDrillSize(pcb.VECTOR2I(pcb.FromMM(0.3), pcb.FromMM(0.3)))
            for graphic in footprint.GraphicalItems():
                if graphic.GetLayer() == pcb.F_SilkS and graphic.GetShape() == pcb.SHAPE_T_POLY:
                    graphic.SetLayer(pcb.F_Fab)
        writer.FootprintSave(str(dest), footprint)

    def custom(name, pad_specs, width, height, comment):
        fp = pcb.FOOTPRINT(None)
        fp.SetFPID(pcb.LIB_ID('Study', name))
        fp.SetAttributes(pcb.FP_SMD)
        fp.SetLibDescription(comment)
        for number, x, y, sx, sy in pad_specs:
            pad = pcb.PAD(fp)
            pad.SetNumber(str(number))
            pad.SetAttribute(pcb.PAD_ATTRIB_SMD)
            pad.SetShape(pcb.PAD_SHAPE_RECT)
            pad.SetPosition(pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y)))
            pad.SetSize(pcb.VECTOR2I(pcb.FromMM(sx), pcb.FromMM(sy)))
            layers = pcb.LSET()
            for layer in ([pcb.F_Cu, pcb.F_Mask] if 'Pads' in name else
                          [pcb.F_Cu, pcb.F_Paste, pcb.F_Mask]):
                layers.AddLayer(layer)
            pad.SetLayerSet(layers)
            fp.Add(pad)
        for layer, extra in [(pcb.F_Fab, 0), (pcb.F_CrtYd, 0.25)]:
            item = pcb.PCB_SHAPE(fp)
            item.SetShape(pcb.SHAPE_T_RECT)
            item.SetStart(pcb.VECTOR2I(pcb.FromMM(-width / 2 - extra), pcb.FromMM(-height / 2 - extra)))
            item.SetEnd(pcb.VECTOR2I(pcb.FromMM(width / 2 + extra), pcb.FromMM(height / 2 + extra)))
            item.SetLayer(layer)
            item.SetWidth(pcb.FromMM(0.05 if layer == pcb.F_CrtYd else 0.1))
            fp.Add(item)
        if name == 'TESwitch':
            zone = pcb.ZONE(fp)
            zone.SetLayer(pcb.F_Cu)
            zone.SetIsRuleArea(True)
            zone.SetDoNotAllowPads(True)
            zone.SetDoNotAllowVias(True)
            zone.SetDoNotAllowTracks(True)
            zone.SetDoNotAllowZoneFills(True)
            zone.SetDoNotAllowFootprints(False)
            zone.Outline().NewOutline()
            for x, y in [(-0.8, -1.3), (0.8, -1.3), (0.8, 1.3), (-0.8, 1.3)]:
                zone.Outline().Append(pcb.FromMM(x), pcb.FromMM(y))
            fp.Add(zone)
            model = pcb.FP_3DMODEL()
            model.m_Filename = '${KIPRJMOD}/models/te-switch-nominal.step'
            fp.Models().push_back(model)
        writer.FootprintSave(str(dest), fp)

    custom('TESwitch', [(n, x, y, 0.65, 0.7) for n, y in [(1, -0.95), (2, 0.95)] for x in [-1.475, 1.475]],
           3.6, 2.6, 'TE 2337228 drawing B. T1/T2=pin1; T3/T4=pin2. No copper/vias under central 1.60 x 2.60 area.')
    custom('PogoPads', [(n + 1, -3.75 + n * 1.5, 0, 1.05, 1.5) for n in range(6)],
           8.55, 1.5, 'Six underside contacts, 1.50mm pitch. No paste. Pin1 left in underside view, right in front projection.')
    custom('LCDPads', [(n + 1, 0, n * 1.3 - 4.55, 1.2, 0.85) for n in range(8)],
           1.2, 9.95, 'Eight solder wire pads, no paste. Carrier pin1 VCC, pin8 BL; see manufacturer schematic and sample revision.')


def native_board():
    import pcbnew as pcb
    import wx
    import xml.etree.ElementTree as ET
    from design import CARRIER
    app = wx.App(False)
    board = pcb.BOARD()
    board.SetCopperLayerCount(2)
    board.GetDesignSettings().SetBoardThickness(pcb.FromMM(0.8))
    board.GetDesignSettings().m_MinClearance = pcb.FromMM(0.15)
    board.GetDesignSettings().m_CopperEdgeClearance = pcb.FromMM(0.2)
    xml = ET.parse(ROOT / 'reports/carrier-netlist.xml').getroot()
    net_names = sorted(n.get('name') for n in xml.find('nets'))
    pad_nets = {(p.get('ref'), p.get('pin')): n.get('name') for n in xml.find('nets') for p in n}
    nets = {}
    for number, name in enumerate(net_names, 1):
        net = pcb.NETINFO_ITEM(board, name, number)
        board.Add(net)
        nets[name] = net
    for part in CARRIER:
        fp = pcb.FootprintLoad(str(ROOT / 'Study.pretty'), part['footprint'])
        fp.SetReference(part['ref'])
        fp.SetValue(part['value'])
        fp.SetFPID(pcb.LIB_ID('Study', part['footprint']))
        fp.GetField(pcb.FIELD_T_DATASHEET).SetText(part['source'])
        fp.SetPath(pcb.KIID_PATH('/' + uid('carrier') + '/' + uid('carrier/' + part['ref'] + '/1')))
        x, y, side, angle = part['placement']
        fp.SetPosition(pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(38 - y)))
        fp.SetOrientationDegrees(angle)
        board.Add(fp)
        if side == 'B':
            fp.Flip(fp.GetPosition(), pcb.FLIP_DIRECTION_LEFT_RIGHT)
        for pad in fp.Pads():
            number = pad.GetNumber()
            if number not in part['nets']:
                raise ValueError('Unexpected footprint pad ' + part['ref'] + ':' + number)
            pad.SetNet(nets[pad_nets[(part['ref'], number)]])
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        for key, value in [('MPN', part['mpn']), ('Manufacturer', part['manufacturer']),
                           ('Kind', part['kind']), ('Design note', part['note'])]:
            field = pcb.PCB_FIELD(fp, pcb.FIELD_T_USER, key)
            field.SetText(value)
            field.SetVisible(False)
            fp.Add(field)
    outline = json.loads((ROOT / 'reports/outline.json').read_text())
    for edge in outline['edges']:
        points = [pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y)) for x, y in edge['points']]
        item = pcb.PCB_SHAPE(board)
        if edge['kind'] == 'arc':
            item.SetShape(pcb.SHAPE_T_ARC)
            item.SetArcGeometry(*points)
        else:
            item.SetShape(pcb.SHAPE_T_SEGMENT)
            item.SetStart(points[0]); item.SetEnd(points[2])
        item.SetLayer(pcb.Edge_Cuts)
        item.SetWidth(pcb.FromMM(0.05))
        board.Add(item)
    pcb.SaveBoard(str(ROOT / 'carrier.kicad_pcb'), board)


def run(args):
    result = subprocess.run([str(x) for x in args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(str(x) for x in args) + '\n' + result.stdout + result.stderr)
    if result.stdout.strip():
        print(result.stdout.strip())


def write_boms():
    from design import SCHEMATICS
    keys = ['ref', 'quantity', 'value', 'mpn', 'manufacturer', 'footprint', 'kind', 'source', 'note']
    for name, spec in SCHEMATICS.items():
        with (ROOT / (name + '-bom.csv')).open('w', newline='') as f:
            writer = csv.DictWriter(f, keys)
            writer.writeheader()
            for part in spec['parts']:
                writer.writerow({**{k: part[k] for k in keys if k != 'quantity'}, 'quantity': 1})
    with (ROOT / 'assembly-bom.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerow(dict(ref='LCD1', quantity=1, value='0.85inch LCD Module / GC9107 / 128x128',
            mpn='26117', manufacturer='Waveshare', footprint='19 x 22.5mm module', kind='assembly_module',
            source='https://www.waveshare.com/0.85inch-lcd-module.htm',
            note='Included MX1.25 connector removed; eight wires. Depth and physical pad order unmeasured. Wire, case, fasteners and probes are not qualified BOM items.'))


def write_previews():
    from html import escape
    from design import CARRIER
    outline = json.loads((ROOT / 'reports/outline.json').read_text())
    pads = json.loads((ROOT / 'reports/board-checks.json').read_text())['pads']
    for side, name in [('F', 'front'), ('B', 'underside')]:
        def point(x, y):
            return (x if side == 'F' else 24 - x, y)
        paths = []
        for edge in outline['edges']:
            start, mid, end = [point(*p) for p in edge['points']]
            path = 'M %g %g ' % start
            if edge['kind'] == 'line':
                path += 'L %g %g' % end
            else:
                ax, ay = start; bx, by = mid; cx, cy = end
                det = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
                ux = ((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/det
                uy = ((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/det
                radius = math.hypot(ax-ux, ay-uy)
                cross = (bx-ax)*(cy-by) - (by-ay)*(cx-bx)
                path += 'A %g %g 0 0 %d %g %g' % (radius, radius, int(cross > 0), cx, cy)
            paths.append(path)
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 26 40" role="img">',
               '<title>Carrier %s placement, USB at bottom</title>' % name,
               '<rect x="0" y="0" width="24" height="38" rx="3" fill="#f7faf9" stroke="#c9d1d6" stroke-width=".1"/>',
               '<path d="%s" fill="none" stroke="#214936" stroke-width=".15"/>' % ' '.join(paths)]
        for part in CARRIER:
            x, cy, placed_side, angle = part['placement']
            y = 38 - cy
            if part['ref'] == 'J1':
                y += 1.175
            x, y = point(x, y)
            w, h, _ = part['body']
            if angle % 180 == 90:
                w, h = h, w
            if w:
                same = placed_side == side
                svg.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s" fill-opacity="%g" stroke="#495a62" stroke-width=".08" %s/>' %
                    (x-w/2, y-h/2, w, h, '#e0e7ec' if same else 'none', 1 if same else .4, '' if same else 'stroke-dasharray=".4 .25"'))
                if same:
                    label_x = x - 1.15 if part['ref'] in ('C3', 'C4', 'R1') else x
                    svg.append('<text x="%g" y="%g" text-anchor="middle" font-family="sans-serif" font-size=".65" fill="#172d3c">%s</text>' % (label_x, y+.2, escape(part['ref'])))
        for pad in pads:
            if pad['side'] != side:
                continue
            x, cy = pad['cad_xy_mm']
            x, y = point(x, 38-cy)
            svg.append('<circle cx="%g" cy="%g" r=".16" fill="#c69a37"/>' % (x, y))
            if pad['ref'] == 'J3':
                svg.append('<rect x="%g" y="%g" width="1.05" height="1.5" fill="#e4bb61" stroke="#967329" stroke-width=".05"/><text x="%g" y="%g" text-anchor="middle" font-family="sans-serif" font-size=".6">%s</text>' % (x-.525,y-.75,x,y+.2,pad['pin']))
            elif pad['ref'] == 'J2':
                svg.append('<rect x="%g" y="%g" width="1.2" height=".85" fill="#e4bb61" stroke="#967329" stroke-width=".05"/><text x="%g" y="%g" text-anchor="middle" font-family="sans-serif" font-size=".6">%s</text>' % (x-.6,y-.425,x-1.1,y+.2,pad['pin']))
        if side == 'F':
            svg.append('<text x="20" y="16.6" text-anchor="middle" font-family="sans-serif" font-size=".65">J2</text>')
        svg.append('</svg>')
        (ROOT / 'previews' / ('placement-' + name + '.svg')).write_text('\n'.join(svg) + '\n')


def build():
    from design import SCHEMATICS
    for directory in ('reports', 'previews', '.cache'):
        (ROOT / directory).mkdir(exist_ok=True)
    write_projects(symbols_for_project())
    write_boms()
    run([FREECAD_PYTHON, __file__, '--outline'])
    run([KICAD_PYTHON, __file__, '--footprints'])
    for name in SCHEMATICS:
        run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'reports/' + name + '-netlist.xml', name + '.kicad_sch'])
        run(['kicad-cli', 'sch', 'export', 'svg', '-o', 'previews', name + '.kicad_sch'])
        run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations',
             '-o', 'reports/' + name + '-erc.json', name + '.kicad_sch'])
    run([KICAD_PYTHON, __file__, '--board'])
    run(['kicad-cli', 'pcb', 'export', 'step', '--force', '--subst-models', '--user-origin', '0x38mm',
         '-o', 'previews/carrier.step', 'carrier.kicad_pcb'])
    run(['kicad-cli', 'pcb', 'export', 'step', '--force', '--board-only', '--user-origin', '0x38mm',
         '-o', '.cache/carrier-board.step', 'carrier.kicad_pcb'])
    run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity',
         '-o', 'reports/carrier-drc.json', 'carrier.kicad_pcb'])
    run([sys.executable, ROOT / 'check.py'])
    run([KICAD_PYTHON, ROOT / 'check.py', '--board'])
    run([FREECAD_PYTHON, ROOT / 'check.py', '--fit'])
    write_previews()
    print('ELECTRICAL_STUDY_OK - physical and fabrication gates remain open')


if __name__ == '__main__':
    if sys.argv[1:2] == ['symbols']:
        for lib_id in sys.argv[2:]:
            symbol = library_symbol(lib_id)
            print(lib_id, [(child(p, 'number')[1], child(p, 'name')[1], str(p[1]), child(p, 'at')[1:]) for u in range(1, 4) for p in pins(symbol, u)])
    elif sys.argv[1:2] == ['--outline']:
        cad_outline()
    elif sys.argv[1:2] == ['--board']:
        native_board()
    elif sys.argv[1:2] == ['--footprints']:
        native_footprints()
    else:
        build()
