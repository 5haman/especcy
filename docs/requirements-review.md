# Requirements quality review

This review records the original documentation baseline. U2 subsequently selected and implemented the scoped firmware decisions listed in the [decision register](decisions.md). Current software/physical evidence is in [verification](verification.md) and [traceability](traceability.md); the historical counts and findings below are retained.

The existing sources are credible as a packaging study. They do not constitute an accepted specification for a functioning product. The suite preserves that maturity and exposes the choices required to create a delivery baseline.

Review boundary: L1–L8, selected external sources W1–W7, and the new 38-item catalogue. Business goals are inferred candidates; stakeholder needs and solution constraints are explicitly separated. Ownership, feasibility and completeness have not received stakeholder validation.

## Literal ambiguity scan

Before deeper analysis, the author's local `scan_weasel_words.py` tool (not part of this repository) scanned `hardware/cad/README.md` and `hardware/cad/parameters.json`. It reported one candidate in the README and none in the parameters.

| Source | Exact match | Disposition |
| --- | --- | --- |
| L1 line 59, column 20 | “does not establish **adequate** RF clearance from the display.” | Not a vague promise. The sentence expressly withholds evidence and the preceding sentence requires radios off. Preserve the limitation; do not invent a clearance threshold for CON-005 |

The final scan of `docs/requirements.md` reported **zero matches**. A zero-hit result does not prove requirements quality: undefined compatibility, behavior and acceptance authority still require the decisions below.

## Supported findings

These findings distinguish source/documentation defects from choices legitimately deferred beyond a packaging study. No hardware implementation fix is included in this documentation task.

| ID | Source or affected requirement | Exact wording or evidence | Characteristic and consequence | Correction or decision |
| --- | --- | --- | --- | --- |
| F-001 | L1 lines 4–5; CON-001, BR-001 | “the ESP32-WROOM-32E core discussed in this conversation” | Traceable/correct: the referenced conversation is not supplied, so original rationale and approval cannot be recovered from that citation | Preserve the named module, cite available files and label inferred purpose. D-001 resolves authority; no historical approval invented. Resolved 2026-10-11 under U4: L1 line 4 now names the module selected for this study, with line numbering unchanged |
| F-002 | Whole requirement set; BR-001/BR-002 and all delivery candidates | No accountable requirement owner or acceptance authority is named in L1/L2 | Owned: the expanded catalogue cannot become an accepted delivery baseline without someone accountable for scope decisions | Catalogue declares “owner not supplied”; D-001 records the decision. This is not a demand for a personal name |
| F-003 | L6 `export_checks.json`; L8 ZIP; CAD-002/CAD-003 evidence | Stored `"pass": true` export report and packaged outputs exist; no tracked script writes `export_checks.json` or produces the archive | Traceable/modifiable: the listed rebuild commands cannot reproduce all supplied evidence and packaging as a single documented pipeline | Development guide separates generated outputs from inherited reports/archive. Current STEP/STL/archive checks were run independently. Resolved 2026-10-11 under U4: `check_exports.py` reproduces the stored report byte for byte, and `package.py` builds and verifies the archive |

The collision exemption name mismatch described in [verification](verification.md) was a source-code observation. It never produced a failing result and was not evidence of a physical collision. On 2026-10-11 the dead entry was removed; the check result is unchanged.

## Requirement-level pending decisions

| Requirement group | Wording that needs a later definition | Why this is pending rather than a fabricated defect | Decision |
| --- | --- | --- | --- |
| BR-001/BR-002 | “explore a compact handheld experience”; “decision about further prototyping” | Business outcomes can be assessed without defining APIs or frame rates, but inferred purpose needs confirmation | D-001/D-004 |
| USR-001/USR-002 | “supported game”; “view its reduced Spectrum picture” | User intent is understandable; compatibility and user assessment are not supplied | D-004/D-006/D-010 |
| FW-003 | “a device menu” | Sufficient to identify a packaging control's purpose; insufficient for executable firmware acceptance | D-006 |
| FW-004/DAT-001 | “ROM and one game snapshot” | Storage intent is sourced; selected content, formats and startup/update flow are undecided | D-004/D-009 |
| FW-005 | “a defined failure outcome” | Explicit candidate coverage placeholder. It is not ready for implementation until an outcome is selected | D-015 |
| MEC-001/QUA-002 | “nominal” dimensions and “print tolerances” | The source openly describes a model, not production tolerances | D-011/D-014 |
| QUA-003 | “check thermal behavior” | A study prerequisite is clear; operational workload and acceptance limits belong to the next design stage | D-010 |

## Findings about the set

**Consistency and uniqueness.** The selected module, display, six controls, power-only USB, external programming and excluded features agree across L1/L2. Parent user needs and their mechanical/firmware decompositions are retained rather than merged. The `48K` artwork does not resolve D-004. Manufacturer guidance is identified as research input, not silently converted into an approved product target.

**Currentness and conformance.** The suite matches the only tracked implementation commit reviewed. No agreed requirements template or prior IDs were supplied. Stable IDs and status labels were introduced to make this larger requested suite maintainable. Age alone was not used to reject a source.

**Traceability and modifiability.** Every catalogue row has an upstream source or explicit derivation and a downstream verification route. Missing future firmware links remain visible. Geometry and metadata use duplicated constants, so changing parameters alone is a drift risk, described in R-008.

**Feasibility.** Current native geometry is supported by tool checks. Electrical operation, emulation performance, game compatibility, thermal behavior, ergonomics, assembly yield and production cost remain unverified. None is declared impossible or assured.

**Coverage.** The suite covers purpose, intended users, mechanical/electrical constraints, logical interfaces, future runtime/data behavior, CAD artifacts and validation. It cannot close compatibility, performance, reliability, accessibility/usability, recovery, licensing or manufacture without D-001–D-015. Missing cloud/account CRUD requirements are not a gap for this evidenced offline scope.

## Corrections made in the suite

The root README now states product maturity and links the full evidence chain. Requirements preserve the selected products and dimensions. The suite distinguishes artwork from emulator output, native geometry checks from physical acceptance, and manufacturer facts from unapproved design proposals. It also distinguishes nominal wall values from local geometry and records the limits of generated reports.

No approved threshold, deadline, role, permission, dependency or manufacturing process was invented. The original questions are split between [current decisions](decisions.md#original-decision-questions) and [later decomposition](decisions.md#decisions-to-be-taken-during-decomposition).

## Documentation verification record

Checks completed on **2026-10-03**:

| Check | Result |
| --- | --- |
| Local paths and heading anchors | 70 relative links checked across 16 Markdown files; no missing targets or invalid checked anchors |
| Catalogue identity and traceability | 38 unique requirements; exactly 38 matching traceability rows; each catalogue row has a source and verification reference |
| Cross-references | All referenced requirement, verification, current/later decision, design-record, finding and risk IDs resolve; 16 verification scenarios |
| Literal scan | Original README: one justified exception above; parameters: zero matches; authored catalogue: zero matches |
| Markdown parsing | All 16 files parse; 44 tables; code fences are balanced |
| Safari reading check | Documentation index links to the catalogue; all 38 requirement rows render; a 390 px viewport keeps text within the page and tables scroll within their own width |
| Architecture diagrams | Both Mermaid diagrams render in Safari; no render errors or console errors |

The browser checks used a temporary local Markdown preview with Markdown-it 14.1.0 and Mermaid 11.12.0. No preview dependency or generated website was added to the repository. Actual Markdown presentation also depends on the reader's renderer. Physical and firmware acceptance gaps remain as listed above.
