"""Assignment 08 — the combined UTOS Final Project Report.
Title page + Table of Contents + all artifacts in the standard SE order.
"""
import os
from report_builder import Report
from build_assignments import (emit_a01, emit_a02, emit_a03, emit_a04,
                               emit_a05, emit_a06, emit_a07)
from build_design_artifacts import emit_packages, emit_crc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
AUTHOR = "Muhammad Hammad Shakeel"

CHAPTERS = [
    ("Chapter 1 — Introduction and Process Model",
     "The system overview, scope, and the chosen software development process "
     "model (with justification and a fallback model).", emit_a01),
    ("Chapter 2 — Use Case Analysis",
     "Actors, the use case diagram, and high-level plus fully-dressed expanded "
     "use cases, each shown realized in the actual UTOS user interface.", emit_a02),
    ("Chapter 3 — Domain Model",
     "The conceptual classes, their attributes, and the associations and "
     "multiplicities among them.", emit_a03),
    ("Chapter 4 — Data Flow Diagram",
     "The Level 0 context diagram, functional hierarchy, and Level 1 / Level 2 "
     "process decompositions.", emit_a04),
    ("Chapter 5 — Class Diagram",
     "The design class diagram: classes, attributes, methods, and the "
     "multiplicity of every relationship.", emit_a05),
    ("Chapter 6 — System Sequence Diagrams",
     "An SSD for each essential expanded use case, capturing the system "
     "operations exchanged between actors and the system.", emit_a06),
    ("Chapter 7 — Operation Contracts",
     "A formal contract (pre-conditions and post-conditions) for every system "
     "operation identified in the system sequence diagrams.", emit_a07),
    ("Chapter 8 — Package Diagram",
     "The logical packaging of the system into cohesive, loosely-coupled layers "
     "and their dependencies.", emit_packages),
    ("Chapter 9 — CRC Cards",
     "Class–Responsibility–Collaborator cards for the principal classes.", emit_crc),
]


def build():
    rep = Report()
    rep.title_page(
        "Software Engineering  ·  Final Project Report",
        "Assignment 08",
        "University Timetable Optimization & Management System (UTOS)",
        "Final Project Report — Software Analysis & Design",
        AUTHOR,
        ["Team Hakari Bankai", "Project: Optimize Flow",
         "4th Semester  ·  Spring 2026"])

    rep.page_break()
    rep.toc_title()
    rep.para("This report compiles all software-engineering analysis and design "
             "artifacts for UTOS in the standard sequence. Update the field below "
             "in Word (Ctrl+A, then F9) if the page numbers need refreshing.",
             italic=True, size=10)
    rep.table_of_contents(depth="1-3")

    for title, blurb, emitter in CHAPTERS:
        rep.page_break()
        rep.heading(1, title)
        rep.para(blurb, italic=True)
        emitter(rep, loff=1)

    path = os.path.join(OUT, "Assignment_08_Final_Project_Report.docx")
    rep.save(path)
    print("A08 done ->", path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build()
