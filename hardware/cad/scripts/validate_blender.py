"""Run on the saved .blend to check the delivered native model and previews."""
from pathlib import Path
import json
import struct
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'models' / 'assembly_meshes.json').read_text())
collection = bpy.data.collections['01 Components / exact FreeCAD meshes']
expected = {part['name'] for part in manifest['components']}
assert {obj.name for obj in collection.objects} == expected
assert len(bpy.data.scenes) == 4
assert bpy.context.scene.name == '01 / Assembled'
points = [obj.matrix_world @ v.co for obj in collection.objects for v in obj.data.vertices]
envelope = [round((max(v[i] for v in points) - min(v[i] for v in points)) * 1000, 4) for i in range(3)]
assert envelope == [24.0, 38.0, 12.0], envelope
image = bpy.data.images['screen_128.png']
assert tuple(image.size) == (128, 128)
assert image.packed_file is not None
for name in ['assembled', 'exploded', 'size_comparison', 'programming_access']:
    path = ROOT / 'renders' / (name + '.png')
    header = path.read_bytes()[:24]
    assert header[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', header[16:24]) == (1800, 1500)
    assert path.stat().st_size > 30000
glb = (ROOT / 'models' / 'speccy_micro.glb').read_bytes()
assert glb[:4] == b'glTF' and struct.unpack('<I', glb[4:8])[0] == 2
checks = {'native_blender_version': bpy.app.version_string,
          'components': len(expected), 'scenes': 4, 'packed_screen': True,
          'assembled_envelope_mm': envelope, 'render_previews': 4,
          'glb_header_valid': True, 'pass': True}
(ROOT / 'models' / 'blender_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
print('NATIVE_BLEND_REOPEN_OK', json.dumps(checks))
