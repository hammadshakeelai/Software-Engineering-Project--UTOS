"""Generate clean, consistently-styled Assignment 01-07 docx files from the
extracted source content + reused diagrams + real UI screenshots.
"""
import os, re, json
from report_builder import Report, img, shot, COLW_IN, GREY

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "extracted")
OUT = os.path.join(HERE, "out")
AUTHOR = "Muhammad Hammad Shakeel"
COURSE = "Software Engineering"
EXTRA = ["Team Hakari Bankai", "4th Semester  ·  Spring 2026"]

NUM_HEAD = re.compile(r"^(\d+(?:\.\d+){0,2})\s+[A-Z].{0,70}$")
FIG_CAP = re.compile(r"^(Figure|Reference Figure)\b", re.I)
SKIP_TEXT = re.compile(r"^(End of Document|UNIVERSITY TIMETABLE|\(UTOS\)|By:|Software Engineering Project|Version\s)", re.I)


def load(stem):
    return json.load(open(os.path.join(EX, stem + ".json"), encoding="utf-8"))


def depth_level(numstr):
    return min(1 + numstr.count("."), 3)


def emit(rep, stem, start_idx=0, promote=True, fig_prefix=None,
         caption_default="UTOS diagram.", fig_counter=None, loff=0):
    """Re-emit blocks from `start_idx` with clean styling. Returns fig count.
    `loff` shifts every heading down by N levels (for the combined report)."""
    blocks = load(stem)["blocks"]
    if fig_counter is None:
        fig_counter = [0]
    i = start_idx
    n = len(blocks)
    while i < n:
        b = blocks[i]
        t = b["type"]
        if t == "heading":
            lvl = b.get("level", 1)
            lvl = 1 if lvl == 0 else min(lvl, 3)
            rep.heading(min(lvl + loff, 4), b["text"].strip())
        elif t == "para":
            txt = b["text"].strip()
            if not txt or SKIP_TEXT.match(txt):
                i += 1
                continue
            if FIG_CAP.match(txt):
                # orphan caption (image already consumed or missing) -> small grey
                rep.para(txt, italic=True, size=9.5, color=GREY)
            elif promote and NUM_HEAD.match(txt):
                m = NUM_HEAD.match(txt)
                rep.heading(min(depth_level(m.group(1)) + loff, 4), txt)
            else:
                rep.para(txt)
        elif t == "table":
            rep.table(b["rows"])
            rep.doc.add_paragraph().paragraph_format.space_after = 0
        elif t == "image":
            path = img(stem, b["file"])
            cap = caption_default
            consumed = False
            if i + 1 < n and blocks[i + 1]["type"] == "para" and \
               FIG_CAP.match(blocks[i + 1]["text"].strip()):
                cap = re.sub(r"^(Figure[^:]*:|Reference Figure[^:]*:)\s*", "",
                             blocks[i + 1]["text"].strip()) or caption_default
                consumed = True
            fig_counter[0] += 1
            label = (fig_prefix + str(fig_counter[0])) if fig_prefix else str(fig_counter[0])
            rep.figure(path, cap, fig_no=label)
            if consumed:
                i += 2
                continue
        i += 1
    return fig_counter


def first_heading_idx(stem):
    blocks = load(stem)["blocks"]
    for idx, b in enumerate(blocks):
        if b["type"] == "heading":
            return idx
        if b["type"] == "para" and NUM_HEAD.match(b["text"].strip()) and \
           b["text"].strip().startswith("1"):
            return idx
    return 0


# ---------------------------------------------------------------------------
def emit_a01(rep, loff=0):
    emit(rep, "Assignment_01_Process_Model_UTOS",
         start_idx=first_heading_idx("Assignment_01_Process_Model_UTOS"),
         fig_prefix="2.", caption_default="Incremental process model for UTOS.", loff=loff)


def emit_a03(rep, loff=0):
    emit(rep, "Assignment_03_Domain_Model_UTOS",
         start_idx=first_heading_idx("Assignment_03_Domain_Model_UTOS"),
         fig_prefix="", caption_default="UTOS domain model.", loff=loff)


def emit_a04(rep, loff=0):
    emit(rep, "Assignment_04_DFD_UTOS",
         start_idx=first_heading_idx("Assignment_04_DFD_UTOS"),
         fig_prefix="", caption_default="UTOS data flow diagram.", loff=loff)


def emit_a05(rep, loff=0):
    emit(rep, "Assignment_05_Class_Diagram_UTOS",
         start_idx=first_heading_idx("Assignment_05_Class_Diagram_UTOS"),
         fig_prefix="", caption_default="UTOS class diagram (all multiplicities labelled).", loff=loff)


def build_a01():
    rep = Report()
    rep.title_page(COURSE, "Assignment 01", "Software Process Model Selection",
                   "Selecting and Justifying a Development Process Model for UTOS",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a01(rep)
    rep.save(os.path.join(OUT, "Assignment_01_Process_Model.docx")); print("A01 done")


def build_a03():
    rep = Report()
    rep.title_page(COURSE, "Assignment 03", "Domain Model",
                   "Conceptual Classes, Attributes, and Associations for UTOS",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a03(rep)
    rep.save(os.path.join(OUT, "Assignment_03_Domain_Model.docx")); print("A03 done")


def build_a04():
    rep = Report()
    rep.title_page(COURSE, "Assignment 04", "Data Flow Diagram",
                   "Context Diagram, Functional Hierarchy, and Level 1/2 DFDs for UTOS",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a04(rep)
    rep.save(os.path.join(OUT, "Assignment_04_DFD.docx")); print("A04 done")


def build_a05():
    rep = Report()
    rep.title_page(COURSE, "Assignment 05", "Class Diagram",
                   "Classes, Attributes, Methods, and Multiplicities for UTOS",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a05(rep)
    rep.save(os.path.join(OUT, "Assignment_05_Class_Diagram.docx")); print("A05 done")


# --- A02 Use Cases (diagrams + real UI screenshots per expanded use case) ---
UC_SHOT = {
    "UC00": ("login_account_picker", "UTOS login screen — multi-account role picker realizing UC00."),
    "UC01": ("admin_master_data", "Master Data — departments and sections realizing the organization hierarchy (UC01)."),
    "UC02": ("admin_holidays", "Holidays / blocked days editor realizing the academic calendar (UC02)."),
    "UC03": ("admin_master_data", "Master Data management for teachers, rooms, sections, and courses (UC03)."),
    "UC04": ("admin_preferences", "Scheduling preferences (enable / weight) realizing UC04."),
    "UC05": ("admin_timetable", "Generated conflict-free class timetable (UC05)."),
    "UC06": ("admin_status_panel", "Timetable quality panel — score, soft penalty, unplaced count (UC06)."),
    "UC07": ("admin_timetable", "Weekly grid with per-entry Lock controls for manual adjustment (UC07)."),
    "UC08": ("teacher_change_request", "Teacher change-request submission form (UC08)."),
    "UC09": ("coordinator_requests", "Coordinator review of a pending change request with recommendation (UC09)."),
    "UC10": ("admin_dashboard", "Schedule Control Center with the Re-optimize action (UC10)."),
    "UC11": ("admin_versions", "Timetable versions with publish controls (UC11)."),
    "UC12": ("student_timetable", "Student section timetable, filtered to the signed-in cohort (UC12)."),
    "UC13": ("admin_dashboard", "Export CSV and Print actions for the published timetable (UC13)."),
    "UC14": ("admin_notifications", "In-app notifications panel (UC14)."),
    "UC15": ("admin_compare_result", "Side-by-side version comparison / diff (UC15)."),
    "UC21": ("login_account_picker", "Per-role account directory used for sign-in and role assignment (UC21)."),
    "UC22": ("admin_audit", "Audit log viewer recording every state-changing action (UC22)."),
}
UC_PHASE2 = {
    "UC16": "Manage Exam Rooms",
    "UC17": "Manage Student Hierarchy",
    "UC18": "Manage Exam Courses",
    "UC19": "Schedule Exams",
    "UC20": "View Exam Schedule and Invigilation Duties",
}
UC_DIAG = {
    "4.1": ("figure41.png", "Class Timetabling use case diagram for UTOS."),
    "4.2": ("figure42.png", "Exam Timetabling and system-wide use case diagram for UTOS."),
    "4.3": ("figure43.jpg", "Baseline (simplified) use case diagram for UTOS."),
}
UC_HEAD = re.compile(r"^(UC\d{2})\b")


def _emit_uc_table(rep, rows):
    if not rows:
        return
    first = (rows[0][0] or "").strip() if rows[0] else ""
    if first.endswith(":"):          # key/value spec table — no header band
        rep.table(rows, header=False, first_col_bold=True,
                  widths=[1.7, 4.8] if len(rows[0]) == 2 else None)
    else:                             # course-of-events / alt-courses — header row
        rep.table(rows, header=True)


def emit_a02(rep, loff=0):
    blocks = load("Assignment_02_Use_Cases_UTOS")["blocks"]
    stem = "Assignment_02_Use_Cases_UTOS"
    n = len(blocks)
    i = 6  # skip cover
    pending_uc = [None]

    def flush_uc():
        uc = pending_uc[0]
        if not uc:
            return
        if uc in UC_SHOT:
            name, cap = UC_SHOT[uc]
            rep.para("System realization (actual UTOS user interface):", bold=True, size=10)
            rep.figure(shot(name), cap, fig_no=uc)
        elif uc in UC_PHASE2:
            rep.callout("User interface for %s (%s) is planned for the Exam "
                        "Timetabling module (Phase 2) and is not yet implemented; "
                        "the expanded use case above specifies the intended behaviour."
                        % (uc, UC_PHASE2[uc]))
        pending_uc[0] = None

    while i < n:
        b = blocks[i]
        t = b["type"]
        if t == "heading":
            txt = b["text"].strip()
            lvl = 1 if b.get("level", 1) == 0 else min(b["level"], 3)
            mdiag = re.match(r"^(4\.\d)\b", txt)
            muc = UC_HEAD.match(txt)
            if muc or (lvl == 1):
                flush_uc()
            rep.heading(min(lvl + loff, 4), txt)
            if muc:
                pending_uc[0] = muc.group(1)
            if mdiag and mdiag.group(1) in UC_DIAG:
                fn, cap = UC_DIAG[mdiag.group(1)]
                # the following block is the 1x1 image-table placeholder -> skip it
                if i + 1 < n and blocks[i + 1]["type"] == "table":
                    i += 1
                rep.figure(img(stem, fn), cap, fig_no=mdiag.group(1))
        elif t == "para":
            txt = b["text"].strip()
            if not txt or SKIP_TEXT.match(txt):
                i += 1
                continue
            if txt.startswith("Module:"):
                rep.para(txt, italic=True, color=GREY, size=10)
            elif txt in ("Typical Course of Events", "Alternative Courses"):
                rep.para(txt, bold=True, size=10.5)
            else:
                rep.para(txt)
        elif t == "table":
            _emit_uc_table(rep, b["rows"])
            rep.doc.add_paragraph().paragraph_format.space_after = 0
        i += 1
    flush_uc()


def build_a02():
    rep = Report()
    rep.title_page(COURSE, "Assignment 02", "Use Case Analysis",
                   "Use Case Diagram, High-Level and Expanded (Fully-Dressed) Use Cases for UTOS",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a02(rep)
    rep.save(os.path.join(OUT, "Assignment_02_Use_Cases.docx")); print("A02 done")


UC_LINE = re.compile(r"^UC\d{2}\b")
BULLET = re.compile(r"^[•▪\-]\s*")


def emit_a06(rep, loff=0):
    stem = "Assignment_06_System_Sequence_Diagrams_UTOS"
    blocks = load(stem)["blocks"]
    n = len(blocks)
    i = 8  # skip cover
    while i < n:
        b = blocks[i]
        t = b["type"]
        if t == "para":
            txt = b["text"].strip()
            if not txt or SKIP_TEXT.match(txt) or set(txt) <= set("━─ "):
                i += 1
                continue
            if UC_LINE.match(txt) and "—" in txt:
                rep.heading(min(2 + loff, 4), txt)
            elif txt in ("Introduction", "Notation Key", "Use Case Index"):
                rep.heading(min(1 + loff, 4), txt)
            elif txt.startswith("Module:"):
                rep.para(txt, italic=True, color=GREY, size=10)
            elif txt.startswith("Figure UC"):
                pass  # captions handled with the image
            elif BULLET.match(txt):
                rep.bullet(BULLET.sub("", txt))
            else:
                rep.para(txt)
        elif t == "table":
            rep.table(b["rows"])
            rep.doc.add_paragraph().paragraph_format.space_after = 0
        elif t == "image":
            cap = "System sequence diagram."
            uc = ""
            if i + 1 < n and blocks[i + 1]["type"] == "para" and \
               blocks[i + 1]["text"].strip().startswith("Figure UC"):
                ftxt = blocks[i + 1]["text"].strip()
                m = re.match(r"Figure (UC\d{2}):\s*(.*)", ftxt)
                if m:
                    uc, cap = m.group(1), m.group(2)
            rep.figure(img(stem, b["file"]), cap, fig_no=uc or None, max_h_in=7.5)
        i += 1


def build_a06():
    rep = Report()
    rep.title_page(COURSE, "Assignment 06", "System Sequence Diagrams",
                   "SSDs for the Essential Expanded Use Cases of UTOS (UC00–UC22)",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a06(rep)
    rep.save(os.path.join(OUT, "Assignment_06_System_Sequence_Diagrams.docx")); print("A06 done")


OC_FIELD = re.compile(r"^(Operation|Use Case|Actors|Cross References|Notes|"
                      r"Exceptions|Output(?: / Return)?|Output):\s*(.*)$")
OC_HEAD = re.compile(r"^OC-\d{2}\b")


def emit_a07(rep, loff=0):
    stem = "Assignment_07_Operation_Contracts_UTOS"
    blocks = load(stem)["blocks"]
    n = len(blocks)
    i = 6  # skip cover
    # buffer for the current OC
    rows = []
    mode = [None]  # None / 'pre' / 'post'
    pre, post = [], []

    def flush():
        if rows:
            rep.table(rows, header=False, first_col_bold=True, widths=[1.7, 4.8])
            rep.doc.add_paragraph().paragraph_format.space_after = 0
        if pre:
            rep.para("Pre-conditions:", bold=True, size=10.5)
            for x in pre:
                rep.bullet(x)
        if post:
            rep.para("Post-conditions:", bold=True, size=10.5)
            for x in post:
                rep.bullet(x)
        rows.clear(); pre.clear(); post.clear(); mode[0] = None

    while i < n:
        b = blocks[i]
        t = b["type"]
        if t == "heading":
            txt = b["text"].strip()
            if OC_HEAD.match(txt):
                flush()
                rep.heading(min(2 + loff, 4), txt)
            else:
                flush()
                rep.heading(min((b.get("level", 1) or 1) + loff, 4), txt)
        elif t == "para":
            txt = b["text"].strip()
            if not txt or SKIP_TEXT.match(txt):
                i += 1
                continue
            mf = OC_FIELD.match(txt)
            if txt.startswith("Pre-conditions"):
                mode[0] = "pre"
            elif txt.startswith("Post-conditions"):
                mode[0] = "post"
            elif BULLET.match(txt):
                (pre if mode[0] == "pre" else post if mode[0] == "post" else []).append(BULLET.sub("", txt))
            elif mf:
                rows.append([mf.group(1) + ":", mf.group(2)])
            else:
                # template-field definitions section etc.
                rep.para(txt)
        i += 1
    flush()


def build_a07():
    rep = Report()
    rep.title_page(COURSE, "Assignment 07", "Operation Contracts",
                   "Formal Operation Contracts for Every System Operation in the UTOS SSDs",
                   AUTHOR, EXTRA)
    rep.page_break(); emit_a07(rep)
    rep.save(os.path.join(OUT, "Assignment_07_Operation_Contracts.docx")); print("A07 done")


if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    targets = sys.argv[1:] or ["a01", "a02", "a03", "a04", "a05", "a06", "a07"]
    g = globals()
    for t in targets:
        g["build_" + t]()
