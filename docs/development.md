# Development and artifact guide

The workflow builds CAD/presentation files and the 48K bench firmware. The [firmware guide](../firmware/README.md) gives native CTest commands, pinned ESP-IDF setup, diagnostic/Dizzy builds and content preparation. There is no PCB tool project or continuous-integration service.

## Repository map

| Location | Role |
| --- | --- |
| `README.md`, `docs/` | Project entry point, requirements, evidence and development guidance |
| `firmware/` | Portable runtime, ESP32 driver, host runner, content tools and tests |
| `hardware/cad/README.md` | Original packaging notes and build instructions |
| `hardware/cad/parameters.json` | Nominal selections, dimensions and assumptions |
| `hardware/cad/scripts/build_freecad.py` | Native geometry, mechanical checks, STEP/STL and mesh manifest |
| `hardware/cad/scripts/build_blender.py` | Presentation, screen artwork, GLB and rendered views |
| `hardware/cad/scripts/validate_blender.py` | Saved-model and preview validation |
| `hardware/cad/models/` | Native/exchange assemblies, manifest and check reports |
| `hardware/cad/meshes/` | Two case halves and six button meshes |
| `hardware/cad/renders/`, `hardware/cad/reference/` | Generated images and an inherited manufacturer outline |

## Prerequisites

The inspected environment has **FreeCAD 1.1.4** and **Blender 5.2.2 LTS** on macOS. Commands use the installed application paths below. The FreeCAD builder explicitly appends `/Applications/FreeCAD.app/Contents/Resources/lib` and needs FreeCAD's bundled Python and GUI libraries.

Other platforms or installation paths have not been tested. Review that library path and GUI setup when porting. Stock Python alone does not provide FreeCAD/OpenCascade or Blender's `bpy` module.

Run the CAD commands below from the repository root. Host firmware commands also use the root; IDF commands use `firmware/`. Preserve the working tree before CAD regeneration: the scripts overwrite model, mesh, report and render artifacts.

## Rebuild sequence

1. Generate native solids, the mechanical report, STEP/STL and the mesh manifest:

   ```sh
   QT_QPA_PLATFORM=offscreen /Applications/FreeCAD.app/Contents/Resources/bin/python -u hardware/cad/scripts/build_freecad.py
   ```

   The builder hides the FreeCAD GUI, checks geometry and reopens saved case solids. A successful run prints `FREECAD_OK`. After saves and assertions, it calls `os._exit(0)` to bypass a documented offscreen OpenGL teardown fault.

2. Generate the Blender assembly, GLB, artwork and four renders:

   ```sh
   /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python hardware/cad/scripts/build_blender.py
   ```

   This consumes the manifest from step 1. A successful run prints `BLENDER_OK`. Rendering selects Metal on supported macOS hardware, then saves scenes configured for CPU rendering.

3. Check the saved presentation:

   ```sh
   /Applications/Blender.app/Contents/MacOS/Blender --background hardware/cad/models/speccy_micro.blend --python hardware/cad/scripts/validate_blender.py
   ```

   Success prints `NATIVE_BLEND_REOPEN_OK` and writes `models/blender_checks.json`. This checks saved data and preview metadata; it does not rerender every view.

The Blender builder also recognizes `--preview`, `--exploded` and `--remaining` after Blender's `--` separator. These modes render subsets and still save other presentation outputs. Use the default full run before judging a complete render delivery; stale previews can survive a partial run.

## Generated outputs and inherited artifacts

| Output | Generator | Review concern |
| --- | --- | --- |
| FCStd, STEP, eight STLs, manifest, mechanical report | FreeCAD builder | Shape validity, units, nominal size, explicit placements and check exclusions |
| BLEND, GLB, screen artwork, four PNG views | Blender builder | mm→m conversion, presentation-only bevels/labels and artwork disclaimer |
| Blender check report | Blender validator | Writes only after assertions pass |
| `export_checks.json` | No generator tracked | Treat as stored evidence; refresh only from a recorded independent export check |
| `speccy_micro_package.zip` | No packager tracked | Existing 27-file CAD bundle; rebuild commands do not update it |

The lid STL is flipped with the outer face on the print bed. Each plunger is translated to an origin at its bounding-box minimum. STL files are in mm; their positions are print-export positions, not assembly placement instructions.

## Changing dimensions or parts

1. Identify affected requirement IDs and the evidence behind the change. Preserve selected constraints unless a decision changes them.
2. Update `parameters.json` and inspect explicit geometry constants, spreadsheet initialization, openings, fasteners, ledges, wires and buttons in the FreeCAD builder.
3. Inspect labels, decorative placements and size comparison in the Blender builder. Changes to the saved spreadsheet alone do not survive a scripted rebuild.
4. Regenerate affected artifacts and run the relevant validators. Review collision scope and physical-fit gaps rather than relying only on `pass: true`.
5. Review source and binary changes together. Update hardware dimensions, requirements, traceability and evidence status. Do not copy an old check report onto a new geometry revision.

No artifact rebuild is needed for an ordinary prose-only correction. The checks run for this documentation task are recorded in [verification](verification.md).

## Troubleshooting

| Symptom | First inspection |
| --- | --- |
| `FreeCAD`/`FreeCADGui` import fails | Bundled interpreter and the script's library path |
| Geometry builder raises `Mechanical preflight failed` | `mechanical_checks.json`: invalid names, colliding pairs and envelope |
| New parameter value has no visible effect | Whether the affected shape uses a constant rather than that JSON value |
| Blender lacks a component or has wrong scale | Manifest freshness, component names and `S = 0.001` conversion |
| Saved Blender validator fails on preview dimensions | Whether all full-size views were regenerated |
| Archive differs from current CAD files | ZIP is not regenerated by either builder; compare entries with their sources |
| A mesh fits digitally but a part does not fit physically | Exact part revision, tolerance stack, motion, wire routing and process limits |

## Documentation maintenance

Keep the catalogue as the obligation source. Update the source register when research changes. Preserve requirement IDs and separate candidate approval from implementation status. A passing test is not a substitute for a missing product decision.

For this author's installed requirements skill, the literal scan command is:

```sh
python3 /Users/shaman/.codex/skills/make-requirements-great/scripts/scan_weasel_words.py hardware/cad/README.md hardware/cad/parameters.json docs/requirements.md
```

The scanner belongs to the author's local skill installation, not this repository. Contributors without it can inspect wording manually, but should state that exact literal coverage was not verified. This command is not a portable project dependency.

Before finishing a documentation change, check relative file links and heading anchors, unique requirement IDs, source/decision/test references, Markdown structure and whitespace. Preserve the original CAD notes as historical source evidence unless a task explicitly updates them.
