# SE Project — Step-by-Step Prompt Library

> A ready-to-use set of **prompts**, one per stage, to drive an AI assistant (e.g. Claude)
> through a complete Software Engineering analysis-and-design project — from inception to the
> final assembled report. The prompts are engineered to be run **in order**, each one
> consuming the previous step's output so the **traceability chain** is preserved end to end.
>
> Pair this with `METHODOLOGY.md` (what each artifact is) and `FULL_REPORT.md` (a worked
> example). This file is *how to generate* each artifact.

---

## How to use this file

1. **Fill the Project Context Block once** (below) and keep it pinned. Paste it at the top of
   every prompt — it gives the model the fixed facts so outputs stay consistent.
2. **Run the prompts in order** (Step 0 → Step 10). Do not skip: each step's output is an
   input to the next.
3. **Feed prior outputs forward.** Where a prompt says *"INPUT: paste the [X] from Step N"*,
   actually paste it. This is what keeps use cases, classes, SSDs, and contracts aligned.
4. **Keep names stable.** A use-case step name → an SSD message name → a contract operation
   name must be the *same string* across steps. Tell the model so explicitly (the prompts do).
5. **Review with the QA prompts** (end of file) before assembling the final report.

> Placeholder convention: replace every `[[ … ]]` with your project's real value.

---

## The Project Context Block (fill once, paste everywhere)

```
PROJECT CONTEXT — paste at the top of every step.

Project name: [[e.g. UTOS — University Timetable Optimization System]]
One-line vision: a [[system]] that turns [[inputs]] into [[valuable output]] via
  [[core mechanism]], for [[users]].
Domain: [[e.g. university class scheduling]]
Team / author: [[name(s)]]   Instructor: [[name]]   Course: Software Engineering
Actors (roles): [[Actor1 — goal]], [[Actor2 — goal]], … (3–6 distinct roles)
In scope (this iteration): [[bullet list]]
Out of scope (future): [[bullet list]]
Tech stack: backend=[[ ]], storage=[[ ]], frontend=[[ ]], swappable seam=[[ ]]
Hard rules (never violated): [[list]]
Soft preferences (optimize, not mandatory): [[list]]
Output format: GitHub-flavored Markdown. Diagrams as labelled ASCII/Mermaid unless told
  otherwise. Be concrete and specific to THIS project — no generic filler.
```

---

## Step 0 — Inception

```
[PASTE PROJECT CONTEXT BLOCK]

ROLE: You are a senior software engineer scoping a new project.

TASK: Produce the Inception section. Do not model anything yet — fix the decisions everything
else depends on.

PRODUCE, as Markdown with these exact headings:
1. Problem statement — 3–5 concrete bullets describing the real pain (be specific to the
   domain; name the failures that happen today).
2. Vision — one sentence using the form in the context block.
3. Scope — two sub-lists: "In scope (this iteration)" and "Out of scope (future)". The
   out-of-scope list must be honest and specific; it is what keeps later diagrams bounded.
4. Actors — a table: Actor | Primary goal | What they can/can't do.
5. Technology decisions — language, storage, UI, and the ONE part you deliberately isolate
   behind an interface because it is most likely to change (the "swappable seam"). Justify it.
6. Exit criteria — confirm problem, vision, scope, actors, tech, repo are all fixed.

CONSTRAINTS: No use cases, no classes, no diagrams here. Keep it to one page. Everything must
be specific to this project; reject generic statements.
```

---

## Step R — Requirements (SRS)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the Inception output from Step 0.

ROLE: You are a requirements engineer writing a Software Requirements Specification.

TASK: Turn the inception into a numbered, testable SRS for the IN-SCOPE features only.

PRODUCE, as Markdown:
1. Introduction — purpose, system overview, problem statement (1 short paragraph each).
2. Scope — In scope vs Out of scope (carry from Step 0, refine).
3. Users & roles — a table of actors + a "user characteristics" table (skill level, intended
   use).
4. Functional requirements — a table with columns: ID | Requirement. Number them FR-01, FR-02,
   … grouped by feature/use case. Each FR must be a single, atomic, VERIFIABLE statement
   ("The system shall …"). This numbering is the traceability key for the whole project.
5. Non-functional requirements — at least 6, labelled NFR-1..n, covering usability,
   performance, reliability/robustness, security/access, portability, maintainability.
6. Constraints & business rules — split hard rules (never violated) vs soft preferences
   (optimize), plus domain invariants.

RULES:
- Every FR must be testable. If you can't imagine a test for it, rewrite it.
- Do NOT invent features outside the in-scope list.
- Keep FR IDs stable; later steps will cite them by number.
```

---

## Step 1 — Software Process Model (Assignment 01)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the SRS from Step R (at least the scope + FR overview).

ROLE: You are a software process consultant.

TASK: Recommend a development process model for THIS project and a fallback.

PRODUCE, as Markdown:
1. Survey — a comparison table of Waterfall, Incremental, Iterative, Spiral, Agile/Scrum,
   Prototyping: one row each, column "Use it when".
2. Selected model + justification — name ONE (or a named hybrid like "Iterative & Incremental")
   and give 3–4 justifications tied to THIS project's realities: Where is the risk? Are
   requirements stable in shape but deep in detail? Can features be staged into increments?
   What is the integration risk?
3. Alternative model + trigger — name the fallback model AND the specific, observable
   condition that would force the switch (e.g. "requirements churn faster than an increment
   can close").

CONSTRAINTS: Justify against the actual scope/risk above — do not give a textbook answer that
would fit any project.
```

---

## Step 2 — Use Cases (Assignment 02)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the SRS functional requirements (FR table) from Step R.

ROLE: You are a systems analyst writing use cases.

TASK: Produce the use-case model. Cover EVERY in-scope FR with at least one use case.

PRODUCE, as Markdown:
1. Use case diagram — as labelled ASCII (or Mermaid): actors on the left, use-case names
   inside a "System" box, and any «include» / «extend» relationships listed explicitly.
2. High-level use cases — one table: UC# | Name | Primary actor | One-line summary | FRs
   covered (cite FR IDs). This is where you prove full FR coverage.
3. Expanded (fully-dressed) use cases — pick the 5–7 most essential and write each with the
   Cockburn template:
   - Use case name / ID, Scope, Level, Primary actor
   - Stakeholders & interests (each party + what they want)
   - Preconditions
   - Postconditions (success guarantees)
   - Main success scenario (numbered steps)
   - Extensions / alternate flows (Na. branches: errors and variants)
   - Special requirements (any NFRs that bite here)

RULES:
- Name each main-success-scenario step's system action as a clear verb phrase
  (e.g. "generateTimetable", "publishVersion"). These exact names WILL be reused as SSD
  messages (Step 6) and contract operations (Step 7) — keep them stable.
- Every UC in the high-level table must cite at least one FR; every in-scope FR must appear
  under at least one UC.
```

---

## Step 3 — Domain Model (Assignment 03)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the high-level use cases from Step 2.

ROLE: You are a domain modeller.

TASK: Produce a CONCEPTUAL domain model (real-world concepts, not software).

PRODUCE, as Markdown:
1. A labelled ASCII (or Mermaid class) diagram of the conceptual classes: each box shows the
   concept name + its attributes (no types, no methods).
2. An "Associations & multiplicities" list: every association named, with multiplicities on
   both ends (1, *, 0..1, 1..*), e.g. "Teacher 1 —teaches— * Course".

RULES:
- NO methods/operations, NO foreign keys, NO UI elements, NO software/technical classes.
- Derive concepts from the NOUNS in the use cases. Include roles, transactions, and the
  things being scheduled/managed.
- This is the conceptual ancestor of the database, but stays at concept level.
```

---

## Step 4 — Data Flow Diagrams (Assignment 04)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the actors (Step 0) and high-level use cases (Step 2).

ROLE: You are a structured-analysis modeller.

TASK: Produce DFDs from Level 0 down, plus a functional hierarchy.

PRODUCE, as Markdown (labelled ASCII):
1. Level 0 / context diagram — the system as ONE process, external entities (the actors), and
   the major labelled data flows in/out.
2. Level 1 — number the major processes (1.0, 2.0, …) and list the data stores (D1, D2, …)
   each reads/writes.
3. Level 2 — explode the single most complex Level-1 process into its sub-steps (2.1, 2.2…).
4. Functional hierarchy — a tree mirroring the leveling.
5. Balancing note — confirm that the inputs/outputs of each parent process reconcile with its
   child diagram.

RULES:
- Notation: process = bubble, external entity = rectangle, data store = open bar, flow =
  labelled arrow. State this legend.
- Enforce the balancing rule explicitly: any flow into/out of a parent must reappear in the
  child.
```

---

## Step 5 — Design Class Diagram (Assignment 05)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the domain model (Step 3) and the tech-stack/seam decision (Step 0).

ROLE: You are a software designer.

TASK: Produce the DESIGN class diagram (software classes, unlike the conceptual model).

PRODUCE, as Markdown (labelled ASCII or Mermaid):
1. A diagram with three-compartment classes (name / attributes / operations) covering:
   controllers/handlers, services, repositories/data-access, the core algorithm/engine, and
   entity classes (which often mirror domain concepts).
2. Attributes WITH types; methods WITH signatures (params + return type).
3. Relationships (association / aggregation / composition / dependency) each with
   multiplicities; mark visibility (+ public, - private).
4. Show the swappable seam as a DEPENDENCY ON AN INTERFACE, not a concrete class.

RULES:
- Entity classes should trace back to domain concepts from Step 3.
- Method names that realize system operations should match the use-case action verbs from
  Step 2 where applicable.
```

---

## Step 6 — System Sequence Diagrams (Assignment 06)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the expanded use cases from Step 2.

ROLE: You are a designer drawing system sequence diagrams.

TASK: Produce ONE SSD per essential use case from Step 2.

PRODUCE, as Markdown — for each use case, a labelled ASCII (or Mermaid) sequence showing:
- the actor and a SINGLE ":System" lifeline (black box),
- the time-ordered system events the actor sends (use the SAME operation names as the
  use-case steps),
- the system's returns (shown with ◄-- or a return arrow),
- loop / alt frames where the use case iterates or branches.

RULES:
- Capture ONLY what crosses the system boundary — no internal objects.
- The message names you choose here are the operations you will contract in Step 7 — keep them
  identical.
```

---

## Step 7 — Operation Contracts (Assignment 07)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the SSDs from Step 6 (so you have the full list of system operations) and the
domain model from Step 3 (so you know the instances/associations/attributes that change).

ROLE: You are a designer writing operation contracts (Larman style).

TASK: Write ONE contract per system operation that appears in the SSDs.

PRODUCE, as Markdown — for each operation, a block:
- Operation: signature name(params)
- Cross-references: the use case(s) it serves
- Preconditions: what must be true before (+ guard conditions)
- Postconditions: the RESULTING STATE, written in PAST TENSE as changes:
    • instances created / deleted
    • associations formed / broken
    • attributes modified

RULES:
- Postconditions describe state, NOT steps. Write "a Version was created", "version.status was
  changed to published" — never "the system creates…".
- Reference concepts/attributes by the names used in the Step 3 domain model.
- For pure queries, write "(query — no state change)" and state what was returned.
```

---

## Step 8 — Packages & CRC (Design Artifacts)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste the design class diagram from Step 5.

ROLE: You are a software architect.

TASK: Produce a package diagram and CRC cards.

PRODUCE, as Markdown:
1. Package diagram (labelled ASCII): group the Step-5 classes into logical packages
   (ui / controller / services / data-access / engine / persistence as fits), with dependency
   arrows. Then state explicitly that dependencies flow in ONE direction (no cycles, no upward
   deps) — or fix the grouping until they do.
2. CRC cards — a table per principal class: Class | Responsibilities (what it knows/does) |
   Collaborators (classes it works with).

RULES:
- Every class in the package diagram must come from Step 5.
- If you find a cyclic/upward dependency, re-package until the layering is clean and say so.
```

---

## Step 9 — Final Report Assembly (Assignment 08)

```
[PASTE PROJECT CONTEXT BLOCK]
INPUT: paste ALL prior outputs (Steps 0–8).

ROLE: You are the editor assembling the final project report.

TASK: Assemble one continuous report in the prescribed sample order, with numbered chapters.

PRODUCE, as Markdown:
1. Title page block — project title + all team members + instructor + course.
2. Table of contents — chapter list with anchors.
3. The artifacts as numbered chapters IN THIS ORDER:
   Process model → Requirements/Use cases → Domain model → DFDs → Design class diagram →
   System sequence diagrams → Operation contracts → Packages & CRC → supporting material.
4. Re-level all headings so each former assignment becomes a chapter (Chapter N, then N.1,
   N.2…) — do not alter the content, only the heading levels and numbering.

RULES:
- Preserve the exact order above; deviation loses marks.
- Do not rewrite artifacts — assemble the SAME content so the report can't drift from the
  standalone deliverables.
```

---

## Step 10 — QA & Traceability Audit (run before submitting)

### 10a. Consistency review
```
INPUT: paste the assembled report from Step 9.

ROLE: You are a strict reviewer.

TASK: Find inconsistencies. Report a table: Issue | Where | Severity | Fix. Check specifically:
- Use-case step names == SSD message names == contract operation names (flag any mismatch).
- Every entity class (Step 5) traces to a domain concept (Step 3).
- DFD balancing holds (parent flows reappear in children).
- Domain model has NO methods; design class diagram HAS methods/types.
- Operation contracts are past-tense state changes, not procedural steps.
Do not rewrite the report; just list the defects and the minimal fix for each.
```

### 10b. Requirement coverage / traceability matrix
```
INPUT: paste the FR table (Step R), the high-level use cases (Step 2), and the operation
contracts (Step 7).

TASK: Produce a traceability matrix table with columns:
FR ID | Use case(s) | Domain concept(s) | Design class/operation | SSD | Contract | Covered?
Mark "Covered?" Yes/No. List every FR that is NOT fully traceable to a contract, and every
class/operation that exists WITHOUT a backing FR (gold-plating). These are the two failure
modes to eliminate before submission.
```

---

## Tips for best results

- **One step per conversation turn.** Don't ask the model to do Steps 2–7 at once; quality
  drops and names drift. Generate, review, then proceed.
- **Always paste the named INPUT.** The traceability chain only holds if each step actually
  sees the previous artifact.
- **Lock vocabulary early.** After Step 2, keep a short glossary of operation names and entity
  names; paste it into later prompts to stop synonyms creeping in.
- **Iterate with the QA prompts** (Step 10) and feed the defect list back into the relevant
  step's prompt as "INPUT: fix these issues: …".
- **Keep diagrams as text** (ASCII/Mermaid) during drafting so they're diffable and
  editable; render to images only for the final document.
