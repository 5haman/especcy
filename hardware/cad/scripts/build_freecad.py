"""Build the native CAD, STEP/STL exports, and a shared Blender mesh manifest.

Run with FreeCAD's bundled Python; it provides the native OpenCascade kernel.
All geometry is in millimetres. GUI runs offscreen only to save view properties.
"""
from pathlib import Path
import json
import math
import os
import sys
import faulthandler
faulthandler.enable()

ROOT = Path(__file__).resolve().parents[1]
FREECAD_LIB = Path('/Applications/FreeCAD.app/Contents/Resources/lib')
if FREECAD_LIB.exists():
    sys.path.append(str(FREECAD_LIB))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import FreeCAD as App
import FreeCADGui as Gui
import Part
import Mesh
import MeshPart

Gui.showMainWindow()
Gui.getMainWindow().hide()
Gui.getMainWindow().setUpdatesEnabled(False)
P = json.loads((ROOT / 'parameters.json').read_text())
doc = App.newDocument('SpeccyMicro')
doc.Label = 'Speccy micro — 24 × 38 × 12 mm packaging study'
sheet = doc.addObject('Spreadsheet::Sheet', 'Dimensions')
sheet.Label = 'Dimensions (mm) / case primitives use expressions'
values = {'CaseWidth': 24, 'CaseLength': 38, 'CaseHeight': 11.6, 'CaseWall': 1.2, 'CaseSeam': 6.4,
          'CaseRadius': 3, 'LCDWidth': 19, 'LCDLength': 22.5,
          'ESPWidth': 18, 'ESPLength': 25.5, 'ESPHeight': 3.1}
for row, (alias, value) in enumerate(values.items(), 1):
    sheet.set(f'A{row}', alias)
    sheet.set(f'B{row}', f'{value} mm')
    sheet.setAlias(f'B{row}', alias)
sheet.setColumnWidth('A', 160)

assembly = doc.addObject('App::Part', 'Assembly')
assembly.Label = 'Assembled / USB powered / radio disabled'
helpers = assembly.newObject('App::DocumentObjectGroup', 'Construction')
helpers.Label = 'Editable case primitives and boolean tools'
items = []
colors = {
    'case': (0.045, 0.058, 0.070), 'pcb': (0.03, 0.28, 0.23),
    'lcdpcb': (0.035, 0.14, 0.32), 'metal': (0.62, 0.68, 0.72),
    'gold': (0.92, 0.64, 0.16), 'black': (0.025, 0.03, 0.037),
    'screen': (0.045, 0.16, 0.18), 'button': (0.73, 0.80, 0.80),
    'fire': (0.96, 0.26, 0.17), 'menu': (0.08, 0.68, 0.64),
    'ceramic': (0.54, 0.37, 0.20), 'wire': (0.72, 0.22, 0.12),
}

def color(obj, rgb):
    obj.ViewObject.ShapeColor = rgb
    obj.ViewObject.LineColor = tuple(v * 0.4 for v in rgb)
    obj.ViewObject.DisplayMode = 'Flat Lines'

def feature(name, label, shape, material, layer, category='hardware'):
    obj = doc.addObject('Part::Feature', name)
    obj.Label, obj.Shape = label, shape
    color(obj, colors[material])
    obj.addProperty('App::PropertyString', 'ComponentRole', 'Packaging')
    obj.ComponentRole = category
    obj.addProperty('App::PropertyString', 'DimensionStatus', 'Packaging')
    obj.DimensionStatus = 'See parameters.json: sourced XY / estimated detail'
    assembly.addObject(obj)
    items.append({'obj': obj, 'material': material, 'layer': layer, 'category': category})
    return obj

def box_shape(w, l, h, x, y, z):
    return Part.makeBox(w, l, h, App.Vector(x, y, z))

def primitive(name, w, l, h, x, y, z, expr=None):
    obj = doc.addObject('Part::Box', name)
    obj.Length, obj.Width, obj.Height = w, l, h
    obj.Placement.Base = App.Vector(x, y, z)
    for prop, expression in (expr or {}).items():
        obj.setExpression(prop, expression)
    helpers.addObject(obj)
    doc.recompute()
    return obj

def rounded(name, w, l, h, x, y, z, radius, expr=None):
    base = primitive(name + 'Box', w, l, h, x, y, z, expr)
    edges = [i for i, edge in enumerate(base.Shape.Edges, 1)
             if edge.BoundBox.ZLength > h * 0.99]
    fillet = doc.addObject('Part::Fillet', name)
    fillet.Base = base
    fillet.Edges = [(i, radius, radius) for i in edges]
    helpers.addObject(fillet)
    doc.recompute()
    if fillet.Shape.isNull() or not fillet.Shape.isValid():
        raise RuntimeError('Invalid rounded primitive: ' + name)
    return fillet

def cut(name, base, tool):
    obj = doc.addObject('Part::Cut', name)
    obj.Base, obj.Tool = base, tool
    helpers.addObject(obj)
    doc.recompute()
    return obj

def tool_feature(name, shape):
    obj = doc.addObject('Part::Feature', name)
    obj.Shape = shape
    helpers.addObject(obj)
    return obj

# Two hollow shell halves. Native dimensions and boolean history remain editable.
print('STAGE case shells', flush=True)
lower_outer = rounded('LowerOutside', 24, 38, 6.4, 0, 0, 0, 3,
    {'Length': 'Dimensions.CaseWidth', 'Width': 'Dimensions.CaseLength', 'Height': 'Dimensions.CaseSeam'})
lower_void = rounded('LowerCavity', 21.6, 35.6, 6.2, 1.2, 1.2, 1.2, 1.8,
    {'Length': 'Dimensions.CaseWidth - 2 * Dimensions.CaseWall',
     'Width': 'Dimensions.CaseLength - 2 * Dimensions.CaseWall',
     'Height': 'Dimensions.CaseSeam', 'Placement.Base.z': 'Dimensions.CaseWall'})
lower = cut('LowerHollow', lower_outer, lower_void)
upper_outer = rounded('UpperOutside', 24, 38, 5.2, 0, 0, 6.4, 3,
    {'Length': 'Dimensions.CaseWidth', 'Width': 'Dimensions.CaseLength',
     'Height': 'Dimensions.CaseHeight - Dimensions.CaseSeam', 'Placement.Base.z': 'Dimensions.CaseSeam'})
upper_void = rounded('UpperCavity', 21.8, 35.8, 4.3, 1.1, 1.1, 6.1, 1.9,
    {'Length': 'Dimensions.CaseWidth - 2.2 mm', 'Width': 'Dimensions.CaseLength - 2.2 mm',
     'Height': 'Dimensions.CaseHeight - Dimensions.CaseSeam - Dimensions.CaseWall + 0.3 mm',
     'Placement.Base.z': 'Dimensions.CaseSeam - 0.3 mm'})
upper = cut('UpperHollow', upper_outer, upper_void)
window = rounded('ScreenWindow', 15.81, 15.81, 3, 4.095, 19.145, 9.8, 0.45)
upper = cut('UpperWindowCut', upper, window)
usb_void = primitive('USBOpening', 8.3, 3, 3.3, 7.85, -0.5, 1.9)
lower = cut('LowerUSBCut', lower, usb_void)
pad_void = rounded('ProgrammingAccess', 10.2, 2.8, 1.5, 6.9, 7.0, -0.1, 0.5)
lower = cut('LowerPogoCut', lower, pad_void)

# Two M1.4 assembly screws; carrier corners are relieved around the bosses.
print('STAGE case fasteners', flush=True)
screw_centers = [(2.6, 2.7), (21.4, 2.7)]
bottom_bosses = []
top_bosses = []
for x, y in screw_centers:
    boss = Part.makeCylinder(1.45, 5.2, App.Vector(x, y, 1.2))
    boss = boss.cut(Part.makeCylinder(0.55, 4.4, App.Vector(x, y, 2.0)))
    bottom_bosses.append(boss)
    neck = Part.makeCylinder(1.45, 4.0, App.Vector(x, y, 6.4))
    neck = neck.cut(Part.makeCylinder(0.8, 6.0, App.Vector(x, y, 6.1)))
    top_bosses.append(neck)

# Narrow wall ledges support the boards without increasing the outer envelope.
bottom_bosses += [box_shape(0.9, 18.0, 0.8, x, 10.0, 4.0) for x in [1.2, 21.9]]
top_bosses += [box_shape(1.9, 14.0, 0.5, x, 20.0, 6.8) for x in [1.1, 21.0]]

bottom_union = tool_feature('LowerBossSolid', Part.makeCompound(bottom_bosses))
lower_fuse = doc.addObject('Part::Fuse', 'LowerWithBosses')
lower_fuse.Base, lower_fuse.Tool = lower, bottom_union
helpers.addObject(lower_fuse)
top_union = tool_feature('UpperBossSolid', Part.makeCompound(top_bosses))
upper_fuse = doc.addObject('Part::Fuse', 'UpperWithBosses')
upper_fuse.Base, upper_fuse.Tool = upper, top_union
helpers.addObject(upper_fuse)
doc.recompute()
holes = [Part.makeCylinder(1.96, 3, App.Vector(b['x'], b['y'], 9.5)) for b in P['buttons']]
holes += [Part.makeCylinder(0.8, 6.0, App.Vector(x, y, 6.1)) for x, y in screw_centers]
holes += [Part.makeCylinder(1.5, 0.9, App.Vector(x, y, 11.0)) for x, y in screw_centers]
upper_holes = tool_feature('UpperButtonAndScrewTools', Part.makeCompound(holes))
upper_final = cut('UpperFinished', upper_fuse, upper_holes)
doc.recompute()

for obj, name, material, layer in [(lower_fuse, 'CaseBase', 'case', 0),
                                 (upper_final, 'CaseLid', 'case', 5)]:
    obj.Label = name.replace('Case', 'Case / ') + ' — editable boolean shell'
    obj.addProperty('App::PropertyString', 'ComponentRole', 'Packaging')
    obj.ComponentRole = 'case'
    assembly.addObject(obj)
    color(obj, colors[material])
    items.append({'obj': obj, 'material': material, 'layer': layer, 'category': 'case'})

# Custom carrier: underside WROOM, power socket, and programming contacts.
print('STAGE carrier and ESP32', flush=True)
c = P['carrier']
carrier = box_shape(c['width'], c['length'], c['thickness'], c['x'], c['y'], c['z'])
carrier = carrier.makeFillet(1.5, [edge for edge in carrier.Edges
                                if edge.BoundBox.ZLength > c['thickness'] * 0.99])
carrier = carrier.cut(box_shape(18.4, 7.4, 1.0, 2.8, 29.1, 4.7))
for x, y in screw_centers:
    carrier = carrier.cut(Part.makeCylinder(1.7, 1.2, App.Vector(x, y, 4.6)))
feature('CarrierPCB', 'Custom carrier / 20.8 × 34.8 × 0.8', carrier, 'pcb', 2)
e = P['esp32']
module_board = box_shape(18, 25.5, 0.8, 3, 10.1, 4.0)
feature('ESPSubstrate', 'ESP32-WROOM-32E / sourced 18 × 25.5 × 3.1 envelope', module_board, 'pcb', 1)
shield = box_shape(17.4, 18.4, 2.3, 3.3, 10.4, 1.7)
feature('ESPShield', 'ESP32 shield / underside', shield, 'metal', 1)
for side in [3.02, 20.58]:
    pads = [box_shape(0.4, 0.72, 0.04, side, 11.1 + i * 1.25, 4.76) for i in range(14)]
    feature('ESPPads' + ('L' if side < 10 else 'R'), 'WROOM castellated contact indication', Part.makeCompound(pads), 'gold', 1, 'detail')
traces = []
for i in range(5):
    traces.append(box_shape(10.2, 0.3, 0.04, 6.2, 30.0 + i * 0.85, 3.96))
    traces.append(box_shape(0.3, 0.85, 0.04, 6.2 if i % 2 else 16.1, 30.0 + i * 0.85, 3.96))
feature('AntennaTrace', 'Antenna indication / radio OFF in this packaging', Part.makeCompound(traces), 'gold', 1, 'detail')

u = P['usb']
usb = box_shape(7.5, 5.9, 2.5, 8.25, 0.8, 2.3)
usb = usb.cut(box_shape(6.2, 3.0, 1.7, 8.9, 0.6, 2.7))
feature('USBPower', 'Micro-B / power only / generic envelope', usb, 'metal', 2)
feature('USBTongue', 'USB socket tongue', box_shape(4.4, 2.2, 0.6, 9.8, 1.0, 3.2), 'black', 2, 'detail')
pad_shapes = [box_shape(1.05, 1.5, 0.04, 7.725 + i * 1.5, 7.7, 4.76) for i in range(6)]
feature('ProgrammingPads', 'GND / 3V3 / TX / RX / EN / BOOT — external UART', Part.makeCompound(pad_shapes), 'gold', 2, 'detail')

# Front-side low-profile controls and small power circuit envelopes.
print('STAGE controls and power', flush=True)
for b in P['buttons']:
    x, y, name = b['x'], b['y'], b['name']
    switch = box_shape(3.0, 2.6, 0.5, x - 1.5, y - 1.3, 5.6)
    switch = switch.fuse(Part.makeCylinder(0.65, 0.15, App.Vector(x, y, 6.1)))
    feature('Switch' + name, name + ' tactile / generic 3 × 2.6 × 0.65', switch, 'metal', 2)
    stem = Part.makeCylinder(0.9, 3.8, App.Vector(x, y, 6.3))
    collar = Part.makeCylinder(2.2, 0.5, App.Vector(x, y, 9.7))
    cap = Part.makeCylinder(1.75, 2.0, App.Vector(x, y, 10.0))
    shape = stem.fuse(collar).fuse(cap)
    mat = 'fire' if name == 'Fire' else 'menu' if name == 'Menu' else 'button'
    feature('Button' + name, name + ' / captured plunger / 3.5 mm cap', shape, mat, 4)

feature('Regulator', '3.3 V LDO / SOT-23-5 package envelope', box_shape(2.9, 1.6, 1.15, 10.95, 11.8, 5.6), 'black', 2)
for i, (x, y) in enumerate([(14.7, 12.2), (16.5, 12.2), (3.6, 4.5)]):
    feature('Capacitor' + str(i), '0603 decoupling / generic', box_shape(1.6, 0.8, 0.8, x, y, 5.6), 'ceramic', 2)
for i, x in enumerate([10.4, 12.6]):
    feature('Pullup' + str(i), 'EN / BOOT pullup / generic 0402', box_shape(1.0, 0.5, 0.5, x, 9.3, 5.6), 'black', 2)

# Manufacturer-sized display carrier, with connector removed for the compact variant.
print('STAGE display', flush=True)
l = P['lcd']
lcd_board = box_shape(19, 22.5, 0.8, 2.5, 14.3, 7.3)
for x in [5.25, 18.0]:
    lcd_board = lcd_board.cut(Part.makeCylinder(0.8, 1.0, App.Vector(x, 17.0, 7.2)))
feature('LCDPCB', 'Waveshare 0.85 LCD / sourced 19 × 22.5 footprint', lcd_board, 'lcdpcb', 3)
panel = box_shape(18.0, 18.0, 2.0, 3.0, 18.05, 8.1)
feature('LCDPanel', 'LCD glass/backlight / estimated 2.0 mm depth', panel, 'black', 3)
gasket = box_shape(18.0, 18.0, 0.3, 3.0, 18.05, 10.1)
gasket = gasket.cut(box_shape(15.81, 15.81, 0.5, 4.095, 19.145, 10.0))
feature('LCDFoam', '0.3 mm adhesive foam gasket / panel retention', gasket, 'black', 3)
feature('LCDActive', '15.21 × 15.21 active area / 128 × 128',
        box_shape(15.21, 15.21, 0.01, 4.395, 19.445, 10.1), 'screen', 3, 'detail')
for i, (x, y, w, h) in enumerate([(5.1, 21.2, 2.8, 1.4), (15.0, 23.0, 2.8, 1.4), (5.2, 29.5, 2.8, 1.4)]):
    feature('LCDBackIC' + str(i), 'LCD rear component / height estimate 1.2 mm',
            box_shape(w, h, 1.2, x, y, 6.1), 'black', 3)
pad_solid = Part.makeCompound([box_shape(0.65, 1.1, 0.05, 3.7 + i * 1.25, 14.6, 7.25) for i in range(8)])
feature('LCDWirePads', 'MX1.25 removed / eight soldered interconnect pads', pad_solid, 'gold', 3, 'detail')

# Short illustrative soldered wires; route clear of the button plungers.
print('STAGE wires', flush=True)
for i in range(8):
    x = 4.0 + i * 1.25
    path = Part.Wire(Part.makePolygon([App.Vector(x, 15.0, 7.2), App.Vector(x, 13.8, 6.5), App.Vector(x, 13.6, 5.7)]).Edges)
    tangent = App.Vector(0, -1.2, -0.7)
    profile = Part.Wire([Part.makeCircle(0.08, App.Vector(x, 15.0, 7.2), tangent)])
    wire = path.makePipeShell([profile], True, False)
    feature('Wire' + str(i), 'LCD interconnect / illustrative route', wire, 'wire', 3, 'detail')

# Assembly screws are simplified; threads are not represented.
for i, (x, y) in enumerate(screw_centers):
    shaft = Part.makeCylinder(0.7, 8.7, App.Vector(x, y, 2.3))
    head = Part.makeCylinder(1.3, 0.55, App.Vector(x, y, 11.0))
    head = head.cut(box_shape(1.7, 0.25, 0.3, x - 0.85, y - 0.125, 11.35))
    feature('Screw' + str(i), 'M1.4 case screw / estimated package', shaft.fuse(head), 'metal', 5, 'fastener')

notes = doc.addObject('App::FeaturePython', 'DesignNotes')
notes.Label = 'READ FIRST / packaging assumptions and sources'
notes.addProperty('App::PropertyStringList', 'Assumptions')
notes.Assumptions = P['assumptions']
notes.addProperty('App::PropertyStringList', 'Sources')
notes.Sources = [s['url'] + ' — ' + s['verified'] for s in P['sources']]
notes.addProperty('App::PropertyString', 'Envelope')
notes.Envelope = '24 × 38 × 12 mm including button caps / USB cable excluded'
notes.addProperty('App::PropertyString', 'DisplayTradeoff')
notes.DisplayTradeoff = '256×192 → 128×96; game controls only; not a full keyboard'
doc.recompute()

final_names = {item['obj'].Name for item in items}
for obj in helpers.Group:
    if obj.Name not in final_names:
        obj.Visibility = False
for item in items:
    item['obj'].Visibility = True
sheet.Visibility = False
for obj in doc.Objects:
    if obj.TypeId in ('App::Origin', 'App::Line', 'App::Plane'):
        obj.Visibility = False

# Native dimensions and strict collision checks on all primary hard envelopes.
print('STAGE mechanical preflight', flush=True)
checks = {'units': 'mm', 'native_freecad_version': '.'.join(App.Version()[:3]),
          'invalid_solids': [], 'collisions': [], 'clearances': {}, 'part_count': len(items)}
for item in items:
    obj = item['obj']
    if obj.Shape.isNull() or not obj.Shape.isValid() or obj.Shape.Volume <= 0:
        checks['invalid_solids'].append(obj.Name)
primary = [it['obj'] for it in items if it['category'] in ('hardware', 'case')]
# The case halves stay in the pairwise check; touching faces have no common volume.
contact_pairs = {frozenset(('ESPShield', 'ESPSubstrate')),
                 frozenset(('LCDPCB', 'LCDPanel'))}
for i, a in enumerate(primary):
    for b in primary[i + 1:]:
        if frozenset((a.Name, b.Name)) in contact_pairs:
            continue
        if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):
            continue
        overlap = a.Shape.common(b.Shape).Volume
        if overlap > 1e-5:
            checks['collisions'].append({'parts': [a.Name, b.Name], 'volume_mm3': round(overlap, 6)})
for a, b, key in [('ESPShield', 'LowerWithBosses', 'module_to_case_floor'),
                  ('CarrierPCB', 'LCDPCB', 'carrier_to_lcd_pcb'),
                  ('LCDPanel', 'UpperFinished', 'lcd_to_roof'),
                  ('Regulator', 'LCDPCB', 'regulator_to_display')]:
    checks['clearances'][key] = round(doc.getObject(a).Shape.distToShape(doc.getObject(b).Shape)[0], 3)
compound = Part.makeCompound([it['obj'].Shape for it in items])
bb = compound.BoundBox
checks['assembled_envelope_mm'] = [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)]
checks['case_wall_mm'] = 1.2
checks['button_hole_radial_gap_mm'] = 0.21
checks['lcd_window_edge_gap_mm'] = 0.30
checks['electrical_validation'] = 'not performed: custom carrier is not routed'
checks['print_validation'] = 'not performed: LCD depths and purchased component packages need measurement'
checks['pass'] = not checks['invalid_solids'] and not checks['collisions'] and checks['assembled_envelope_mm'] == [24.0, 38.0, 12.0]
(ROOT / 'models' / 'mechanical_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
if not checks['pass']:
    print(json.dumps(checks, indent=2))
    raise RuntimeError('Mechanical preflight failed; fix before delivering.')

if Gui.activeDocument() is not None:
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(ROOT / 'models' / 'speccy_micro.FCStd'))
step_path = ROOT / 'models' / 'speccy_micro_assembly.step'
Part.export([it['obj'] for it in items], str(step_path))
step_path.write_text('\n'.join(line.rstrip() for line in step_path.read_text().splitlines()) + '\n')

manifest = {'units': 'mm', 'parameters': P, 'components': []}
for item in items:
    obj = item['obj']
    mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.08,
                                 AngularDeflection=0.2, Relative=False)
    verts, faces = mesh.Topology
    manifest['components'].append({'name': obj.Name, 'label': obj.Label,
        'material': item['material'], 'color': colors[item['material']],
        'layer': item['layer'], 'category': item['category'],
        'vertices': [[v.x, v.y, v.z] for v in verts], 'faces': [list(f) for f in faces]})
    if obj.Name in ('LowerWithBosses', 'UpperFinished'):
        print_shape = obj.Shape.copy()
        if obj.Name == 'UpperFinished':
            print_shape.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 180)
            print_shape.translate(App.Vector(0, 38, 11.6))
        print_mesh = MeshPart.meshFromShape(Shape=print_shape, LinearDeflection=0.05,
                                          AngularDeflection=0.15, Relative=False)
        print_mesh.write(str(ROOT / 'meshes' / ('case_base.stl' if obj.Name == 'LowerWithBosses' else 'case_lid.stl')))
for name in ['Up', 'Down', 'Left', 'Right', 'Fire', 'Menu']:
    shape = doc.getObject('Button' + name).Shape.copy()
    bbox = shape.BoundBox
    shape.translate(App.Vector(-bbox.XMin, -bbox.YMin, -bbox.ZMin))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.04, AngularDeflection=0.15, Relative=False)
    mesh.write(str(ROOT / 'meshes' / ('button_' + name.lower() + '.stl')))
(ROOT / 'models' / 'assembly_meshes.json').write_text(json.dumps(manifest, separators=(',', ':')))
App.closeDocument(doc.Name)
reopened = App.openDocument(str(ROOT / 'models' / 'speccy_micro.FCStd'))
assert all(reopened.getObject(name) is not None for name in final_names)
assert reopened.getObject('UpperFinished').Shape.isValid()
assert reopened.getObject('LowerWithBosses').Shape.isValid()
print('FREECAD_OK', json.dumps({'parts': len(items), 'envelope_mm': checks['assembled_envelope_mm'], 'collisions': 0}))
App.closeDocument(reopened.Name)
sys.stdout.flush()
sys.stderr.flush()
# macOS offscreen FreeCADGui can crash while unloading its OpenGL widgets.
# All saves and assertions above must succeed before bypassing GUI teardown.
os._exit(0)
