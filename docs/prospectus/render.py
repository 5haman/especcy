"""Render the prospectus from the saved CAD presentation, without changing it.

Run with Blender: blender --background --python docs/prospectus/render.py
"""
from pathlib import Path
import json
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / "hardware/cad/models/speccy_micro.blend"))

gpu = False
if sys.platform == "darwin":
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "METAL"
    preferences.get_devices()
    for device in preferences.devices:
        device.use = device.type == "METAL"
        gpu |= device.use

views = [
    ("hero", "01 / Assembled", (12, 19, 6), (72, -87, 138), 52, 1600, 1800),
    ("front", "01 / Assembled", (12, 19, 6), (12, 19, 150), 46, 1400, 1800),
    ("exploded", "02 / Exploded", (12, 19, 38), (106, -148, 175), 103, 1400, 2000),
    ("back", "04 / Programming access", (12, 19, 5), (68, -76, -126), 52, 1600, 1600),
]
manifest = {"source": "hardware/cad/models/speccy_micro.blend", "geometry_changed": False, "views": {}}

for name, scene_name, target_mm, camera_mm, scale_mm, width, height in views:
    scene = bpy.data.scenes[scene_name]
    bpy.context.window.scene = scene
    studio = next(c for c in scene.collection.children if "Studio and captions" in c.name)
    for obj in studio.objects:
        obj.hide_render = obj.type not in ("CAMERA", "LIGHT")
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU" if gpu else "CPU"
    scene.cycles.samples = 80
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    target = Vector(target_mm) * 0.001
    camera = scene.camera
    camera.location = Vector(camera_mm) * 0.001
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = scale_mm * 0.001
    # Re-light the exact solids for a clear studio presentation.
    for obj in studio.objects:
        if obj.type == "LIGHT":
            obj.data.energy *= 1.35
            obj.data.size *= 0.75
    bpy.context.view_layer.update()
    points = []
    for obj in scene.objects:
        if obj.type == "MESH" and not obj.hide_render:
            points.extend(obj.matrix_world @ Vector(v) for v in obj.bound_box)
    for _ in range(20):
        projected = [world_to_camera_view(scene, camera, p) for p in points]
        if all(0.055 < p.x < 0.945 and 0.055 < p.y < 0.945 for p in projected):
            break
        camera.data.ortho_scale *= 1.035
        bpy.context.view_layer.update()
    else:
        raise RuntimeError(f"Could not frame every CAD component in {name}")
    path = OUT / f"{name}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    # Project documented control centers for exact PDF leader placement.
    anchors = {}
    if name == "front":
        params = json.loads((ROOT / "hardware/cad/parameters.json").read_text())
        for button in params["buttons"]:
            point = Vector((button["x"], button["y"], 12.02)) * 0.001
            p = world_to_camera_view(scene, camera, point)
            anchors[button["name"]] = [p.x, 1 - p.y]
        p = world_to_camera_view(scene, camera, Vector((12, 27.05, 11.1)) * 0.001)
        anchors["Screen"] = [p.x, 1 - p.y]
    if name == "exploded":
        for title, coords in [
            ("Front shell", (16, 18, 71.6)),
            ("Button plungers", (18, 5.4, 60)),
            ("LCD", (15, 14.3, 44.1)),
            ("Carrier", (20, 20, 29.6)),
            ("ESP32", (20, 20, 16.8)),
            ("Rear shell", (23.4, 19, 6.4)),
        ]:
            p = world_to_camera_view(scene, camera, Vector(coords) * 0.001)
            anchors[title] = [p.x, 1 - p.y]
    manifest["views"][name] = {
        "file": f"assets/{name}.png", "width": width, "height": height,
        "scene": scene_name, "anchors": anchors,
    }
    print(f"PROSPECTUS_RENDER_OK {name}", flush=True)

(OUT / "renders.json").write_text(json.dumps(manifest, indent=2) + "\n")
# Deliberately do not save the source .blend or export any CAD files.
print("PROSPECTUS_RENDERS_COMPLETE", flush=True)
