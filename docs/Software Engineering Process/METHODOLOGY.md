# Software Engineering Project Methodology (Reusable Playbook)

> A **project-agnostic** guide to the exact structure and process we follow for a Software
> Engineering analysis-and-design project — from inception, through the requirements phase
> and the seven modelling assignments (plus packages/CRC), to the final assembled report.
> Use this as a template for **any** project: replace the bracketed `[…]` placeholders with
> your own domain, actors, and rules. The companion `FULL_REPORT.md` is a *worked example*
> of this playbook applied to UTOS; `PROCESS.md` is the project-specific making-of.

---

## 0. The big picture

Every project moves through the same chain, and each link is **traceable to the previous
one** — nothing appears downstream without a justification upstream:

```
Inception ─► Requirements (SRS) ─► Process model ─► Use cases ─► Domain model
   ─► DFDs ─► Design class diagram ─► System sequence diagrams ─► Operation contracts
   ─► Packages & CRC ─► Final report
```

The single rule that keeps the whole thing coherent — the **traceability chain**:

```
Requirement (FR-xx)
   → Use case (who needs it, how it flows)
      → Domain concept (the things involved)
         → Design class / operation (the software that realizes it)
            → System event in an SSD (what crosses the boundary)
               → Operation contract (the exact state change)
                  → Test case (proof it works)
```

If you can draw that line for every feature, the design is **complete** (every requirement is
realized) and **justified** (no class or operation exists without a requirement behind it).

---

## Stage 0 — Inception (before anything is modelled)

Produce the decisions every later artifact depends on. No graded diagram, but get these
wrong and everything downstream is wrong.

**Checklist**
- [ ] **Problem statement** — the real pain, in 3–5 concrete bullet points.
- [ ] **Vision** — one sentence: *"a [system] that turns [inputs] into [valuable output] via
      [core mechanism], for [users]."*
- [ ] **Scope** — explicit **In scope** vs **Out of scope** lists. Writing the out-of-scope
      list is what keeps later diagrams honest.
- [ ] **Actors** — the distinct user roles and each one's primary goal.
- [ ] **Technology decisions** — language, storage, UI, and any "swappable seam" you want to
      protect (isolate the riskiest/most-likely-to-change part behind an interface).
- [ ] **Project setup** — repo, layered folder layout, a *reproducible* docs toolkit.

**Exit criteria:** problem, vision, scope, actors, tech stack, and repo all fixed.

---

## Stage R — Requirements (the SRS)

Turn the vision into a written, numbered, **testable** specification. This is the bridge
between "we have an idea" and "we can model it."

**The four activities**
1. **Elicitation** — gather needs (stakeholder goals, pain points, scenario walkthroughs).
2. **Analysis & negotiation** — resolve conflicts; record every trade-off as an explicit
   scope decision, not an accident.
3. **Specification** — write the SRS (structure below).
4. **Validation** — check it is complete, consistent, unambiguous, and **verifiable** (every
   requirement must be testable).

**SRS structure**
1. Introduction — purpose, overview, problem statement.
2. Scope — In/Out of scope (per module if multiple).
3. Users & roles — actor table + user characteristics.
4. **Functional requirements** — numbered `FR-xx`, grouped by feature/use case. *This
   numbering is the traceability key the whole project cites.*
5. **Non-functional requirements** — quality attributes: usability, performance, reliability/
   robustness, security/access, portability, maintainability.
6. Constraints & business rules — the hard rules that can never be violated vs the soft
   preferences, plus domain invariants.

**Classify every requirement** as Functional (what it does), Non-functional (how well), or
Business rule/domain invariant (what must always hold).

**Exit criteria:** a validated, numbered SRS with a clear scope boundary and a testable FR set.

---

## Assignment 01 — Software Process Model

**Goal:** choose a development process model and justify it; propose a fallback.

**Contents**
1. **Survey** the candidates with their defining characteristics:

   | Model | Use it when |
   |-------|-------------|
   | Waterfall | Requirements are fully known and stable up front; little change expected. |
   | Incremental | The system splits into value-adding increments on a stable base. |
   | Iterative | Understanding of the product matures by building; refine the same product. |
   | Spiral | High-risk projects needing risk-driven prototyping (heavyweight). |
   | Agile/Scrum | Requirements are volatile; need continuous re-prioritization. |
   | Prototyping | Requirements are unclear and need a prototype to clarify. |

2. **Selected model + justification** — tie it to *your* project's realities (where is the
   risk? are requirements stable in shape but deep in detail? can features be staged?).
3. **Alternative model + trigger** — which model you'd switch to, and the *specific condition*
   that would force the switch (e.g. "requirements churn faster than increments can close").

**Notation:** prose + comparison table; optional phase diagram of the chosen loop.

---

## Assignment 02 — Use Cases

**Goal:** a use-case diagram, plus a high-level **and** an expanded description for **each**
use case.

**Contents**
1. **Use case diagram** — actors, use-case ellipses, the system boundary, and
   `«include»` / `«extend»` relationships.
2. **High-level descriptions** — one table: each use case's name, primary actor, and a
   1–2 sentence intent.
3. **Expanded (fully-dressed) use cases** — Cockburn template per use case:

   | Field | What to write |
   |-------|---------------|
   | Use case name / ID | Verb-phrase goal. |
   | Scope / Level | The system; user-goal level. |
   | Primary actor | Who initiates. |
   | Stakeholders & interests | Each party and what they want from this use case. |
   | Preconditions | What must be true before. |
   | Postconditions (success guarantees) | What is true after success. |
   | Main success scenario | Numbered happy-path steps. |
   | Extensions / alternate flows | `Na.` branches (errors, variants). |
   | Special requirements | NFRs touching this use case. |

**Tip:** the message names in the main success scenario become the **system operations** in
Assignment 06 and the **contracts** in Assignment 07 — keep them consistent.

**Notation:** UML use-case diagram + Cockburn fully-dressed template.

---

## Assignment 03 — Domain Model

**Goal:** the key **concepts**, their **attributes**, and their **relationships** — at the
conceptual level, *not* software.

**Contents**
- **Conceptual classes** — the nouns from the problem domain (real-world things, roles,
  transactions, events).
- **Attributes** — the data each concept carries (no types/methods needed).
- **Associations** — named lines between concepts with **multiplicities** on both ends
  (`1`, `*`, `0..1`, `1..*`).
- **Generalizations / association classes** — where natural.

**Rules:** **no operations/methods**, no foreign keys, no UI elements. This is vocabulary, not
software. It is the conceptual ancestor of your database schema, but stays at concept level.

**Notation:** UML conceptual class diagram (concept name + attributes; lines with role names
and multiplicities).

---

## Assignment 04 — Data Flow Diagrams

**Goal:** start at Level 0 (context), then decompose into a functional hierarchy.

**Contents**
1. **Level 0 / context diagram** — the whole system as **one** process bubble, the external
   entities (your actors), and the major data flows in/out.
2. **Level 1** — the major processes (number them `1.0, 2.0, …`) and the **data stores**
   (`D1, D2, …`) they read/write.
3. **Level 2** (where useful) — explode any complex process into its sub-steps.
4. **Functional hierarchy** — a tree mirroring the leveling.

**Notation:** process = bubble/rounded rect, external entity = rectangle, data store =
open-ended bar, data flow = labelled arrow.

**The balancing rule (don't skip):** every flow entering/leaving a parent process must
re-appear in its child diagram. If a Level-1 process takes input D1 and produces D2, its
Level-2 explosion must show D1 coming in and D2 going out.

---

## Assignment 05 — Design Class Diagram

**Goal:** the **software** classes with attributes, methods, and relationship multiplicities
(the design view, unlike Assignment 03's concepts).

**Contents**
- **Classes** — controllers/handlers, services, repositories/data-access, the core
  algorithm/engine, and entity/data classes (these often mirror domain concepts).
- **Attributes** — with **types**.
- **Methods** — with **signatures** (params + return type).
- **Relationships** — association / aggregation / composition / dependency, each with
  **multiplicities**; mark visibility (`+` public, `-` private).
- Show any **swappable seam** as a dependency on an interface, not a concrete class.

**Notation:** UML design class diagram — three compartments (name / attributes / operations).

---

## Assignment 06 — System Sequence Diagrams

**Goal:** one SSD per essential use case (referencing the expanded use cases).

**Contents**
- The **actor**, a single `:System` lifeline (black box), and the **time-ordered system
  events** the actor sends, with the system's returns (`◄--`).
- SSDs capture **what crosses the system boundary**, not internal objects.
- Use `loop` / `alt` frames where the use case has iteration or alternatives.

**Tip:** name each message as the **system operation** it triggers — these names become the
contracts in Assignment 07. One use case → one SSD → its operations.

**Notation:** UML sequence diagram, single `:System` lifeline.

---

## Assignment 07 — Operation Contracts

**Goal:** one contract per **system operation** identified in the SSDs.

**Contents (per operation)** — Larman template:

| Field | What to write |
|-------|---------------|
| Operation | Signature: `name(params)`. |
| Cross-references | The use case(s) it serves. |
| Preconditions | What must be true before (and any guard conditions). |
| Postconditions | State changes, **in past tense**: instances *created/deleted*, associations *formed/broken*, attributes *modified*. |

**The key discipline:** postconditions describe the **resulting state**, not the steps to get
there. Write "a `Version` *was created*" / "version.status *was changed* to published", never
"the system creates…" or procedural how-to. Query operations note "*(query — no state change)*".

---

## Design Artifacts — Packages & CRC

**Package diagram**
- Group classes into logical **packages** (e.g. ui / controller / services / data-access /
  engine / persistence).
- Show **dependency arrows** and confirm they flow in **one direction** (no cycles, no upward
  dependencies) — proof of clean layering.
- Notation: UML package notation (tabbed folders + dashed dependency arrows).

**CRC cards** — one per principal class:

| Section | Content |
|---------|---------|
| **Class** | The class name. |
| **Responsibilities** | What it *knows* and *does* (a few bullets). |
| **Collaborators** | The other classes it works with to fulfil them. |

CRC cards are a quick sanity check that responsibilities are well-distributed and no class is
doing too much.

---

## Assignment 08 — Final Report

**Goal:** assemble everything into one report in the **prescribed sample order**. Deviating
from the order loses marks.

**Contents (in order)**
1. **Title page** — project title + all team members.
2. **Table of contents** — real, page-numbered.
3. The artifacts as numbered **chapters**, in the sample's exact sequence:
   process model → requirements/use cases → domain model → DFDs → design class diagram →
   SSDs → operation contracts → (packages & CRC) → supporting material.

**Assembly principle:** generate the combined report from the **same content** as the
standalone deliverables (re-leveled into chapters), so the two can never drift out of sync.
Fill the TOC/page numbers as a final pass, then render to PDF for visual QA.

---

## Recommended toolchain pattern (reproducible docs)

Treat documents as **build output**, not hand-maintained files, so they stay consistent and
regenerable:

```
source notes / live system
        │  extract
        ▼
   structured data (JSON) + captured images
        │  builder (one title-page style, heading scheme, table look, figure captions)
        ▼
   per-assignment documents  ──┐
                               ├─ combined final report (same emitters, re-leveled)
   diagrams (drawn fresh) ─────┘
        │  TOC/page-number pass + export
        ▼
   final .docx + PDF (for QA), mirrored to a "final" folder
```

Conventions worth standardizing: one **title page** (project, team, author, instructor);
**numbered headings** (1, 1.1, 1.1.1) so the TOC and cross-references resolve; **banded
tables** for use cases / contracts / CRC; **captioned figures** ("Figure N: …") so every
diagram is referenceable.

---

## Master checklist (per project)

- [ ] **0 Inception** — problem, vision, scope (in/out), actors, tech, repo.
- [ ] **R Requirements** — numbered FRs + NFRs + business rules; all testable.
- [ ] **01 Process model** — choice justified + fallback with switch trigger.
- [ ] **02 Use cases** — diagram + high-level table + expanded (fully-dressed) per use case.
- [ ] **03 Domain model** — concepts + attributes + multiplicities (no methods).
- [ ] **04 DFD** — L0 context + L1 (processes & stores) + functional hierarchy; balanced.
- [ ] **05 Class diagram** — classes/attributes/methods/multiplicities + swappable seam.
- [ ] **06 SSDs** — one per use case; boundary events named as operations.
- [ ] **07 Contracts** — one per operation; past-tense state-change postconditions.
- [ ] **+ Packages & CRC** — one-directional dependencies; CRC per principal class.
- [ ] **08 Final report** — prescribed order, title page, generated TOC, PDF QA.
- [ ] **Traceability** — every FR traces FR → UC → concept → class/op → SSD → contract → test.

---

*Replace the placeholders, keep the order, preserve the traceability chain — and any project
follows the same disciplined path from idea to delivered report.*
