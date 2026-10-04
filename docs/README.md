# Documentation suite

This suite describes Especcy's packaging study, 48K Dizzy bench firmware and electrical placement study. The original review was authored on **2026-10-03** against `13053ce`; U2's firmware and U3's **2026-10-04** electrical evidence are recorded separately from that CAD baseline.

The authoring mode is **mixed**: extract constraints, research integration facts and review requirements. Business intent remains inferred. U2 approves the firmware phase; U3 approves the electrical study. Neither approves the full product catalogue or physical prototype.

## Documents

| Document | What it answers |
| --- | --- |
| [Product prospectus (PDF)](prospectus/speccy-micro-prospectus.pdf) | What does the concept look like, how is it designed, and what is its prototype status? [Preview and source](prospectus/README.md). |
| [Product brief](product-brief.md) | What is this product concept, who would use it, and what is in scope? |
| [Research and sources](research.md) | What evidence supports the design, and what remains unverified? |
| [Requirements](requirements.md) | What obligations are extracted, proposed or blocked by decisions? |
| [Architecture](architecture.md) | How do the mechanical, electrical, firmware and CAD parts relate? |
| [Hardware specification](hardware.md) | What are the modeled dimensions, component selections and assembly limits? |
| [Interfaces and firmware](interfaces-and-firmware.md) | What connects to what, and which runtime contracts still need decisions? |
| [Verification](verification.md) | How can each requirement be assessed, and which checks have run? |
| [Traceability](traceability.md) | Which source, implementation and verification item belongs to each requirement? |
| [Requirements review](requirements-review.md) | What defects and coverage questions were found? |
| [Decisions](decisions.md) | Which design choices are recorded, pending now or deferred to decomposition? |
| [Risks](risks.md) | What could prevent a working prototype, and what evidence would reduce that uncertainty? |
| [Development guide](development.md) | How are artifacts rebuilt, checked and updated? |
| [Firmware guide](../firmware/README.md) | How are native checks, content preparation, ESP32 builds and bench checks run? |
| [Electrical guide](../hardware/electronics/README.md) | How are KiCad circuits, BOMs, placement, programming and fit/thermal gates reviewed and reproduced? |
| [Roadmap](roadmap.md) | Which phase is implemented, and what evidence closes the next gate? |
| [Glossary](glossary.md) | What do the domain terms and abbreviations mean? |

## Reading paths

- **Assess the concept:** product brief → research → decisions → risks.
- **Implement a prototype:** requirements → hardware → interfaces and firmware → verification.
- **Review a change:** requirements → traceability → requirements review → development guide.
- **Inspect the existing model:** [original CAD notes](../hardware/cad/README.md) → hardware → development guide.

## Evidence and status rules

**Extracted** means the obligation already appears in the supplied repository. **Candidate** means it is inferred or proposed and needs confirmation. **Observed** describes implementation or a test result; it does not grant product approval. An extracted requirement can still be unimplemented.

Sources L1–L10, W1–W22 and U1–U3 are defined in [research](research.md). Requirement IDs remain stable. Verification scenarios use V-IDs, current decisions use D-IDs, later decisions use DEC-IDs, review findings use F-IDs, and risks use R-IDs.

The [requirements catalogue](requirements.md) holds obligations. Other documents explain or map them. Conflicting evidence remains visible until a decision resolves it. No commercial target, schedule, owner, test threshold or legal entitlement is assumed.

## Review boundary

The original baseline contains CAD scripts, parameters, models, renders and stored reports. Later phases add firmware, native tests, two successful ESP32 content builds and the KiCad electrical/placement study. No routed carrier, CI service or physical test record is present. Safari research, native checks and local builds are separate evidence types; static checks do not test physical products.

This is a complete documentation suite for the available evidence. It is not a claim that delivery requirements, physical feasibility or stakeholder acceptance are complete.
