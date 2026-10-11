"""Check the STEP assembly and print meshes, then write models/export_checks.json.

Run with FreeCAD's bundled Python after build_freecad.py. No GUI is needed.
The check reads exported files only; it does not rebuild or change geometry.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
FREECAD_LIB = Path('/Applications/FreeCAD.app/Contents/Resources/lib')
if FREECAD_LIB.exists():
    sys.path.append(str(FREECAD_LIB))
import FreeCAD  # noqa: F401  # Must load before its Part and Mesh modules.
import Mesh
import Part

ENVELOPE_MM = [24.0, 38.0, 12.0]

step = Part.read(str(ROOT / 'models' / 'speccy_micro_assembly.step'))
bb = step.BoundBox
checks = {'step_envelope_mm': [round(bb.XLength, 4), round(bb.YLength, 4), round(bb.ZLength, 4)],
          'step_valid': step.isValid(), 'stl_files': {}}
for path in sorted((ROOT / 'meshes').glob('*.stl')):
    mesh = Mesh.Mesh(str(path))
    checks['stl_files'][path.name] = {'closed': mesh.isSolid(), 'volume_mm3': round(mesh.Volume, 3)}
checks['pass'] = (checks['step_valid'] and checks['step_envelope_mm'] == ENVELOPE_MM
                  and len(checks['stl_files']) == 8
                  and all(stl['closed'] and stl['volume_mm3'] > 0 for stl in checks['stl_files'].values()))
(ROOT / 'models' / 'export_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
if not checks['pass']:
    print(json.dumps(checks, indent=2))
    raise SystemExit('Export checks failed')
print('EXPORT_CHECKS_OK', json.dumps({'stl_files': len(checks['stl_files']), 'envelope_mm': checks['step_envelope_mm']}))
