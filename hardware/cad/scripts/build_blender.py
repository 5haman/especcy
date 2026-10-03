"""Import the exact FreeCAD tessellation, save Blender views, and render previews."""
from pathlib import Path
import json
import math
import struct
import zlib
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'models' / 'assembly_meshes.json').read_text())
S = 0.001  # CAD mm -> Blender metres
gpu = False
if sys.platform == 'darwin':
    preferences = bpy.context.preferences.addons['cycles'].preferences
    preferences.compute_device_type = 'METAL'
    preferences.get_devices()
    gpu = any(device.type == 'METAL' for device in preferences.devices)
    for device in preferences.devices:
        device.use = device.type == 'METAL'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for scene in list(bpy.data.scenes):
    if scene != bpy.context.scene:
        bpy.data.scenes.remove(scene)

def png_rgb(path, pixels, width, height):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''.join(b'\0' + bytes(pixels[y]) for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))

# Illustrative 256×192 game picture, reduced exactly 2:1 to 128×96.
palette = [(8, 15, 24), (225, 231, 227), (248, 220, 28), (20, 203, 209), (210, 25, 167)]
def original_pixel(x, y):
    if y >= 178:
        return palette[1 if (x // 8 + y // 8) % 2 else 0]
    for a, b, h in [(10, 72, 62), (104, 163, 98), (193, 245, 139), (34, 97, 149)]:
        if a <= x < b and h <= y < h + 8:
            return palette[3 if (x // 8) % 2 else 1]
    if 124 <= x <= 133 and 151 <= y <= 160:
        return palette[2]
    if 122 <= x <= 135 and 161 <= y <= 172:
        return palette[1]
    if ((x * 17 + y * 23) % 503) == 0:
        return palette[4]
    return palette[0]

pixels = []
for y in range(128):
    row = []
    for x in range(128):
        if 16 <= y < 112:
            samples = [original_pixel(x * 2 + dx, (y - 16) * 2 + dy) for dx in range(2) for dy in range(2)]
            rgb = tuple(sum(p[i] for p in samples) // 4 for i in range(3))
        else:
            rgb = (3, 5, 8)
        if 120 <= y <= 123 and 8 <= x < 120:
            rgb = [(225, 32, 32), (241, 218, 21), (31, 205, 70), (31, 150, 231)][min(3, (x - 8) // 28)]
        row.extend(rgb)
    pixels.append(row)
glyphs = {'4': ['10010','10010','10010','11111','00010','00010','00010'],
          '8': ['01110','10001','10001','01110','10001','10001','01110'],
          'K': ['10001','10010','10100','11000','10100','10010','10001']}
for i, char in enumerate('48K'):
    for y, line in enumerate(glyphs[char]):
        for x, value in enumerate(line):
            if value == '1':
                offset = (55 + i * 6 + x) * 3
                pixels[4 + y][offset:offset + 3] = [220, 234, 225]
texture_path = ROOT / 'renders' / 'screen_128.png'
png_rgb(texture_path, pixels, 128, 128)

materials = {}
def material(name, color, metallic=0, roughness=0.45, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*color, 1)
        bsdf.inputs['Emission Strength'].default_value = emission
    return mat

for part in DATA['components']:
    key = part['material']
    if key not in materials:
        materials[key] = material(key, part['color'], 0.8 if key in ('metal', 'gold') else 0,
                                  0.30 if key == 'metal' else 0.45)
white = material('Lettering', (0.76, 0.85, 0.89), emission=0.8)
muted = material('Caption', (0.32, 0.46, 0.52), emission=0.8)
accent = material('Dimensions teal', (0.1, 0.88, 0.79), emission=0.8)
screen = materials['screen']
bsdf = screen.node_tree.nodes.get('Principled BSDF')
tex = screen.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(str(texture_path))
tex.image.pack()
tex.interpolation = 'Closest'
screen.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
screen.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
bsdf.inputs['Emission Strength'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = 0.24

def setup_scene(scene, title):
    scene.name = title
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'MILLIMETERS'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.device = 'GPU' if gpu else 'CPU'
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1500
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.world = bpy.data.worlds.new(title + ' studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.025, 0.038, 0.050, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
    return scene

assembled = setup_scene(bpy.context.scene, '01 / Assembled')
components = bpy.data.collections.new('01 Components / exact FreeCAD meshes')
assembled.collection.children.link(components)
originals = []
for part in DATA['components']:
    mesh = bpy.data.meshes.new(part['name'] + ' / CAD mesh')
    mesh.from_pydata([[v * S for v in p] for p in part['vertices']], [], part['faces'])
    mesh.update()
    obj = bpy.data.objects.new(part['name'], mesh)
    components.objects.link(obj)
    obj.data.materials.append(materials[part['material']])
    obj['component'] = part['label']
    obj['exploded_layer'] = part['layer']
    obj['source'] = 'FreeCAD / assembly_meshes.json / millimetres converted to metres'
    if part['name'] == 'LCDActive':
        uv = mesh.uv_layers.new(name='Panel pixels')
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                point = mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv = ((point.x / S - 4.395) / 15.21, (point.y / S - 19.445) / 15.21)
    if part['category'] in ('hardware', 'case'):
        bevel = obj.modifiers.new('Small presentation edge bevel / CAD unchanged', 'BEVEL')
        bevel.width, bevel.segments = (0.09 if part['category'] == 'case' else 0.035) * S, 2
        bevel.limit_method = 'ANGLE'
    originals.append(obj)

def cube(collection, name, dimensions, location, mat, bevel=0):
    verts = [(x * dimensions[0] / 2, y * dimensions[1] / 2, z * dimensions[2] / 2)
             for x, y, z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    faces = [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [tuple(reversed(face)) for face in faces])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    mesh.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge radius', 'BEVEL')
        mod.width, mod.segments = bevel, 3
    return obj

def text(collection, name, content, size, position, mat=white, align='LEFT', parent=None):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body, curve.size, curve.align_x = content, size, align
    curve.extrude = 0
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.parent, obj.location = parent, position
    curve.materials.append(mat)
    return obj

def tube(collection, name, points, radius, mat, parent=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions, curve.bevel_depth, curve.bevel_resolution = '3D', radius, 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.parent = parent
    curve.materials.append(mat)
    return obj

decoration = bpy.data.collections.new('02 Surface labels / presentation only')
assembled.collection.children.link(decoration)
text(decoration, 'Front logo', 'SPECCY', 1.2 * S, (12*S, 15.8*S, 11.62*S), align='CENTER')
for b in DATA['parameters']['buttons']:
    label = {'Up':'^','Down':'v','Left':'<','Right':'>','Fire':'A','Menu':'M'}[b['name']]
    text(decoration, 'Button legend ' + b['name'], label, 1.4*S,
         (b['x']*S, (b['y']-0.5)*S, 12.015*S), materials['black'], align='CENTER')
for i, rgb in enumerate([(0.85,0.035,0.04),(0.92,0.76,0.015),(0.04,0.65,0.16),(0.02,0.42,0.88)]):
    stripe = cube(decoration, 'Spectrum stripe ' + str(i), (0.8*S, 1.6*S, 0.015*S),
                  ((16.8+i*1.0)*S, 36.0*S, 11.615*S), material('Spectrum '+str(i), rgb))
    stripe.rotation_euler.z = -0.25

def studio(scene, target, position, ortho, ground=True):
    collection = bpy.data.collections.new(scene.name + ' / Studio and captions')
    scene.collection.children.link(collection)
    cam = bpy.data.objects.new(scene.name + ' Camera', bpy.data.cameras.new(scene.name + ' Camera'))
    collection.objects.link(cam)
    cam.location = Vector(position) * S
    cam.rotation_euler = (Vector(target)*S - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type, cam.data.ortho_scale = 'ORTHO', ortho*S
    cam.data.clip_start, cam.data.clip_end = 0.0001, 10
    scene.camera = cam
    for name, pos, power, size in [('Key', (30,-70,150), 7, 90), ('Fill', (-90,20,70), 3, 80), ('Rim', (55,105,110), 9, 75)]:
        lamp = bpy.data.lights.new(scene.name + name, 'AREA')
        lamp.energy, lamp.shape, lamp.size = power * 0.02, 'DISK', size*S
        obj = bpy.data.objects.new(lamp.name, lamp)
        collection.objects.link(obj)
        obj.location = Vector(pos)*S
        obj.rotation_euler = (Vector(target)*S-obj.location).to_track_quat('-Z','Y').to_euler()
    if ground:
        mat = material(scene.name+' ground', (0.035,0.052,0.063), roughness=0.65)
        cube(collection, 'Studio ground / not part of device', (260*S,260*S,0.2*S), (0,0,-0.3*S), mat)
    return cam, collection

def caption(scene, collection, camera, title, subtitle, footer):
    horizontal = scene.camera.data.ortho_scale
    vertical = horizontal * scene.render.resolution_y / scene.render.resolution_x
    # Text is in a camera-facing plane. It remains legible at any model view angle.
    text(collection, 'Title', title, 2.5*S, (-horizontal/2+4*S, vertical/2-5*S, -0.14), parent=camera)
    text(collection, 'Subtitle', subtitle, 1.25*S, (-horizontal/2+4*S, vertical/2-8*S, -0.14), muted, parent=camera)
    text(collection, 'Footer', footer, 1.15*S, (-horizontal/2+4*S, -vertical/2+3.8*S, -0.14), muted, parent=camera)

cam, studio_coll = studio(assembled, (12,20,6), (73,-91,140), 64)
caption(assembled, studio_coll, cam, 'SPECCY / MICRO',
        '24 x 38 x 12 mm  /  ESP32-WROOM-32E  /  USB power',
        '0.85-inch screen / six buttons / custom PCB / estimated packaging target')
text(studio_coll, 'Size badge', '24 x 38 x 12 mm', 1.9*S, (-24.5*S,-17.8*S,-0.14), accent, parent=cam)

# Editable alternate scenes share the same exact CAD meshes.
def duplicate_parts(scene, name, offset=(0,0,0), exploded=False, with_decoration=True):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    for original in list(originals) + (list(decoration.objects) if with_decoration else []):
        obj = original.copy()
        obj.data = original.data
        collection.objects.link(obj)
        obj.location += Vector(offset)*S
        if exploded:
            obj.location.z += original.get('exploded_layer', 5) * 12*S
    return collection

exploded = setup_scene(bpy.data.scenes.new('Exploded'), '02 / Exploded')
duplicate_parts(exploded, 'Exploded / CAD components', exploded=True, with_decoration=False)
cam2, coll2 = studio(exploded, (12,19,34), (114,-168,196), 112)
caption(exploded, coll2, cam2, 'THE COMPLETE STACK', 'Six layers / same CAD solids / USB cable excluded',
        '24 x 38 x 12 mm assembled / depths and component packages require sample measurements')
cam2.matrix_world = cam2.matrix_basis
labels = [
    ((16,18,71.6), '06  Front shell', '1.2 mm roof / screen and button openings'),
    ((18,5.4,60), '05  Six button plungers', 'four directions / action / menu'),
    ((15,14.3,44.1), '04  0.85-inch LCD', '128 x 128 / connector removed / soldered wires'),
    ((20,20,29.6), '03  Custom carrier PCB', 'switches / 3.3 V power / external UART pads'),
    ((20,20,16.8), '02  ESP32 module', '18 x 25.5 x 3.1 mm / fitted below carrier'),
    ((23.4,19,6.4), '01  Rear shell', 'Micro-B power opening / programming access')]
for position, title, sub in labels:
    point = cam2.matrix_world.inverted() @ (Vector(position)*S)
    tx = 20*S
    ty = point.y
    tube(coll2, title+' leader', [(point.x,ty,-0.14),(tx-2*S,ty,-0.14)], 0.025*S, accent, cam2)
    text(coll2, title, title, 1.7*S, (tx,ty+0.7*S,-0.14), white, parent=cam2)
    text(coll2, sub, sub, 0.95*S, (tx,ty-1.0*S,-0.14), muted, parent=cam2)

comparison = setup_scene(bpy.data.scenes.new('Comparison'), '03 / Size comparison')
duplicate_parts(comparison, 'Compact device', offset=(-35,0,0))
reference = bpy.data.collections.new('DevKitC / reference PCB footprint only')
comparison.collection.children.link(reference)
cube(reference, 'DevKitC reference / PCB footprint only', (27.94*S,48.26*S,1.29*S),
     ((8+27.94/2)*S,19*S,0.645*S), material('DevKit reference PCB', (0.025,0.19,0.18)), 0.6*S)
for side in [9.7,34.24]:
    for i in range(19):
        cube(reference, 'Reference pad', (1.3*S,1.3*S,0.02*S),
             (side*S,(-3.86+i*2.54)*S,1.305*S), materials['gold'])
text(reference, 'Reference board title', 'DEVKITC V4', 2.1*S, (21.97*S,23*S,1.32*S), align='CENTER')
text(reference, 'Reference board note', 'PCB FOOTPRINT ONLY', 1.1*S, (21.97*S,19*S,1.32*S), muted, align='CENTER')
cam3, coll3 = studio(comparison, (0,19,5), (0,19,155), 86)
caption(comparison, coll3, cam3, 'HOW MUCH SPACE IT SAVES',
        'Same scale / custom device case compared with the development PCB',
        'Custom device includes its case / DevKitC outline excludes its case, headers and antenna overhang')
text(coll3, 'Compact dimensions', '24 x 38 mm / COMPLETE CASE', 1.2*S, (-23*S,-26*S,-0.14), accent, align='CENTER', parent=cam3)
text(coll3, 'Reference dimensions', '27.94 x 48.26 mm / PCB ONLY', 1.2*S, (22*S,-26*S,-0.14), white, align='CENTER', parent=cam3)

back = setup_scene(bpy.data.scenes.new('Back'), '04 / Programming access')
duplicate_parts(back, 'Back / exact CAD components', with_decoration=False)
cam4, coll4 = studio(back, (12,19,5), (72,-80,-130), 64, ground=False)
for lamp in [o for o in coll4.objects if o.type == 'LIGHT']:
    lamp.location.z *= -1
    lamp.rotation_euler = (Vector((12,19,5))*S-lamp.location).to_track_quat('-Z','Y').to_euler()
caption(back, coll4, cam4, 'POWER AND PROGRAMMING',
        'Micro-B supplies 5 V / six exposed pads connect to an external USB-UART adapter',
        'USB data is not implemented / no battery / games stored in flash / radio disabled')

readme = bpy.data.texts.new('READ ME / design limits')
readme.write('SPECCY MICRO — packaging study\n24 x 38 x 12 mm including caps.\n\n'
             + '\n'.join(DATA['parameters']['assumptions'])
             + '\n\nSCENES: assembled, exploded, PCB size comparison, programming access.\n'
             + 'Exact FreeCAD tessellation; small render-only bevels and decorative labels.\n')

# Export just the assembled hardware as a portable GLB, with embedded screen texture.
bpy.context.window.scene = assembled
bpy.ops.object.select_all(action='DESELECT')
for obj in originals:
    obj.select_set(True)
bpy.context.view_layer.objects.active = originals[0]
bpy.ops.export_scene.gltf(filepath=str(ROOT / 'models' / 'speccy_micro.glb'),
                          export_format='GLB', use_selection=True, export_apply=True)

preview = '--preview' in sys.argv
views = [(assembled,'assembled.png'), (exploded,'exploded.png'),
         (comparison,'size_comparison.png'), (back,'programming_access.png')]
selected_views = (views[:1] if preview else views[1:2] if '--exploded' in sys.argv
                  else views[1:] if '--remaining' in sys.argv else views)
for scene, filename in selected_views:
    bpy.context.window.scene = scene
    if preview:
        scene.render.resolution_percentage = 50
        scene.cycles.samples = 16
        filename = 'lighting_preview.png'
    scene.render.filepath = str(ROOT / 'renders' / filename)
    bpy.ops.render.render(write_still=True)
    if preview:
        scene.render.resolution_percentage = 100
        scene.cycles.samples = 48

bpy.context.window.scene = assembled
for scene in bpy.data.scenes:
    scene.cycles.device = 'CPU'  # native file renders without a machine-specific GPU preference
bpy.ops.object.select_all(action='DESELECT')
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_perspective = 'CAMERA'
        area.spaces.active.clip_start = 0.0001
        area.spaces.active.shading.color_type = 'MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'models' / 'speccy_micro.blend'))
print('BLENDER_OK', json.dumps({'components': len(originals), 'scenes': len(bpy.data.scenes), 'renders': len(selected_views), 'gpu': gpu}))
