# Speccy micro product prospectus

[Open the eight-page PDF](speccy-micro-prospectus.pdf) · [View all pages](preview.jpg) · [PDF checks](checks.json)

A landscape, 16:10 product prospectus with photorealistic concept visuals based on the existing CAD, selectable text, embedded fonts, chapter bookmarks and internal navigation. The page numbers are links. The cover and closing page also have navigation buttons.

The narrative follows the idea, scale, controls, picture, layers, system, recorded evidence and next prototype step. The built-in imagegen tool refined the CAD reference images with realistic plastic grain, LCD glass, metal details and studio lighting. These are concept visuals; the editable CAD remains the engineering reference. Screens retain the original illustrative artwork. No ROM, game screenshot or game content is included. Dimensions and hardware selections retain the existing product baseline; software/static evidence is distinguished from physical acceptance.

| Photorealistic asset | View |
| --- | --- |
| [hero-photo.png](assets/hero-photo.png) | Three-quarter exterior; cover and closing page |
| [front-photo.png](assets/front-photo.png) | Front view; size and controls spreads |
| [exploded-photo.png](assets/exploded-photo.png) | Six-layer internal stack |
| [back-photo.png](assets/back-photo.png) | Underside with six programming contacts |

[Final prompt set and provenance](photoreal-prompts.json) records the built-in tool, edit targets, material reference, prompts, underside contact-count correction and two reviewed exploded-view callout positions. The original CAD renders remain alongside the selected edits. The PDF fits each edited product into its original CAD frame using visible alpha bounds, without modifying the PNGs.

## Rebuild the PDF

From the repository root, with [uv](https://docs.astral.sh/uv/) installed:

```sh
uv run docs/prospectus/build.py
```

The script declares its pinned Python dependencies. It creates the PDF, `checks.json`, `preview.jpg`, and ignored page PNGs in `previews/`. Rebuilding uses the selected local photorealistic assets and their CAD frames; it requires no image-generation call, browser or CAD application. On macOS it embeds the installed Arial and DIN Alternate fonts. Elsewhere it uses ReportLab's bundled Bitstream Vera fonts; `--font-dir /path/to/fonts` can select the original font files. Fonts are not redistributed separately.

The checks verify eight pages at 960 × 600 points, eight bookmark destinations, valid internal navigation, embedded used fonts, selectable text, required product/status statements, page bounds and non-overlapping text boxes. They also guard the selected dimensions, processor, display and control count, require transparent RGBA photo assets, and check that the six product-image pages use the selected image dimensions. `checks.json` records hashes for the four selected images. `preview.jpg` and the page PNGs are rendered from the finished PDF for visual review. The PDF uses fixed metadata for repeatable builds from the same assets and fonts.

## Rebuild the CAD reference renders

With Blender installed:

```sh
blender --background --python docs/prospectus/render.py
uv run docs/prospectus/build.py
```

`render.py` opens `hardware/cad/models/speccy_micro.blend`, hides presentation captions/ground, adjusts cameras and lights, and renders four transparent PNGs into `assets/`. It records projected control/layer anchors in `assets/renders.json`. It does not save the source model or change/export geometry. The checked version is Blender 5.2.2 LTS.

This command rebuilds the CAD references, not the AI material/lighting edits. If the source design changes, refresh and review the photorealistic edits with the recorded prompts before rebuilding the PDF. Image generation is not deterministic; the selected PNGs preserve this edition.

## Content sources

| Pages | Repository evidence |
| --- | --- |
| 1–2: idea and scale | [Product brief](../product-brief.md), [CAD parameters](../../hardware/cad/parameters.json) |
| 3–4: controls and display | [Firmware guide](../../firmware/README.md), [product brief](../product-brief.md) |
| 5–6: layers and system | [CAD notes](../../hardware/cad/README.md), [electrical guide](../../hardware/electronics/README.md) |
| 7: recorded evidence and open tests | [Verification](../verification.md), [roadmap](../roadmap.md), [electrical guide](../../hardware/electronics/README.md) |
| 8: next step and release limits | [Product brief](../product-brief.md), [decisions](../decisions.md) |

The evidence page summarizes the recorded baseline; creating this PDF does not rerun firmware suites or qualify hardware. Distribution rights for the underlying CAD/documentation remain unresolved in D-013, and the prospectus grants no new license or release approval. The deliverable is tracked as `op-se7.4`; the photorealistic refresh is `op-se7.4.2`.
