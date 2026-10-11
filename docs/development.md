# Development and artifact guide

The workflow builds CAD/presentation files, 48K bench firmware and the KiCad electrical study. The [firmware guide](../firmware/README.md) covers software builds. The [electrical guide](../hardware/electronics/README.md) covers circuits, BOMs, native checks and fit/thermal gates. There is no routed PCB. On every push and pull request, [GitHub Actions](../.github/workflows/ci.yml) runs the host tests with GCC and Clang, the ESP32 diagnostic build, the electrical checks, the Markdown link check and the CAD package build.

## Repository map

| Location | Role |
| --- | --- |
| `README.md`, `docs/` | Project entry point, requirements, evidence and development guidance; `docs/check_links.py` checks relative links and anchors |
| `LICENSE`, `LICENSE-HARDWARE`, `LICENSE-DOCS` | GPL-3.0, CERN-OHL-S-2.0 and CC BY-SA 4.0 texts; the root README maps each path |
| `.github/workflows/ci.yml` | Continuous integration for software, electrical, documentation and packaging checks |
| `firmware/` | Portable runtime, ESP32 driver, host runner, content tools and tests |
| `hardware/electronics/` | KiCad carrier/fixture schematics, unrouted board, exact BOMs, generator, checks and previews |
| `hardware/cad/README.md` | Original packaging notes and build instructions |
| `hardware/cad/parameters.json` | Nominal selections, dimensions and assumptions |
| `hardware/cad/scripts/build_freecad.py` | Native geometry, mechanical checks, STEP/STL and mesh manifest |
| `hardware/cad/scripts/build_blender.py` | Presentation, screen artwork, GLB and rendered views |
| `hardware/cad/scripts/validate_blender.py` | Saved-model and preview validation |
| `hardware/cad/scripts/check_exports.py` | STEP validity/envelope and STL closure/volume report |
| `hardware/cad/scripts/package.py` | Reproducible CAD archive in `dist/` |
| `hardware/cad/models/` | Native/exchange assemblies, manifest and check reports |
| `hardware/cad/meshes/` | Two case halves and six button meshes |
| `hardware/cad/renders/` | Generated images |

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

4. Check the exported files:

   ```sh
   /Applications/FreeCAD.app/Contents/Resources/bin/python hardware/cad/scripts/check_exports.py
   ```

   Success prints `EXPORT_CHECKS_OK` and rewrites `models/export_checks.json`. It reads the STEP assembly and the eight STL files; it does not rebuild geometry.

5. After committing the changes, build the downloadable archive:

   ```sh
   python3 hardware/cad/scripts/package.py
   ```

   Success prints `CAD_PACKAGE_OK` with the entry count and SHA256. The archive contains the tracked `hardware/cad` files and the three license files. Entries are sorted and share one timestamp, so the same commit gives the same bytes. The script refuses uncommitted CAD changes unless `--allow-dirty` is given.

The Blender builder also recognizes `--preview`, `--exploded` and `--remaining` after Blender's `--` separator. These modes render subsets and still save other presentation outputs. Use the default full run before judging a complete render delivery; stale previews can survive a partial run.

## Generated outputs and inherited artifacts

| Output | Generator | Review concern |
| --- | --- | --- |
| FCStd, STEP, eight STLs, manifest, mechanical report | FreeCAD builder | Shape validity, units, nominal size, explicit placements and check exclusions |
| BLEND, GLB, screen artwork, four PNG views | Blender builder | mm→m conversion, presentation-only bevels/labels and artwork disclaimer |
| Blender check report | Blender validator | Writes only after assertions pass |
| `export_checks.json` | `check_exports.py` | STEP validity and envelope; STL closure and volume |
| `dist/speccy_micro_package.zip` | `package.py` | Not committed; attached to GitHub releases |

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
| `package.py` refuses to run | Commit the CAD or license changes first, or pass `--allow-dirty` for a local preview |
| A mesh fits digitally but a part does not fit physically | Exact part revision, tolerance stack, motion, wire routing and process limits |

## Documentation maintenance

Keep the catalogue as the obligation source. Update the source register when research changes. Preserve requirement IDs and separate candidate approval from implementation status. A passing test is not a substitute for a missing product decision.

Run `python3 docs/check_links.py` to check every relative link and heading anchor in the tracked Markdown files. CI runs the same check.

Before finishing a documentation change, check relative file links and heading anchors, unique requirement IDs, source/decision/test references, Markdown structure and whitespace. Preserve the original CAD notes as historical source evidence unless a task explicitly updates them.
