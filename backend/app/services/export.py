import io

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from sqlalchemy.orm import Session

from app.models.allotment import Allotment
from app.models.course import Course
from app.models.student import Student


def _rows(db: Session) -> list[dict]:
    q = (
        db.query(Allotment, Student, Course)
        .join(Student, Student.uid == Allotment.student_uid)
        .join(Course, Course.id == Allotment.course_id)
        .order_by(Course.course_name, Student.uid)
        .all()
    )
    return [
        {
            "uid": s.uid,
            "name": s.name,
            "cgpa": s.cgpa,
            "parent_branch": s.parent_branch,
            "course": c.course_name,
            "offering_branch": c.branch_name,
            "choice": a.choice_number if a.choice_number else "Fallback",
            "allotted_at": a.allotted_at.strftime("%Y-%m-%d %H:%M") if a.allotted_at else "",
        }
        for a, s, c in q
    ]


def export_excel(db: Session) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Allotments"

    headers = ["UID", "Name", "CGPA", "Branch", "Course", "Offered By", "Choice", "Allotted At"]
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    for r in _rows(db):
        ws.append([
            r["uid"], r["name"], r["cgpa"], r["parent_branch"],
            r["course"], r["offering_branch"], r["choice"], r["allotted_at"],
        ])

    for col, width in zip("ABCDEFGH", [12, 24, 8, 10, 32, 12, 10, 18]):
        ws.column_dimensions[col].width = width

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def export_pdf(db: Session) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=20, rightMargin=20, topMargin=30, bottomMargin=20,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("<b>MDM Course Allotment — Master List</b>", styles["Title"]),
        Spacer(1, 12),
    ]

    data = [["UID", "Name", "CGPA", "Branch", "Course", "Offered By", "Choice"]]
    for r in _rows(db):
        data.append([
            r["uid"], r["name"], str(r["cgpa"]), r["parent_branch"],
            r["course"], r["offering_branch"], str(r["choice"]),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2b5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f4f8")]),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("ALIGN", (6, 1), (6, -1), "CENTER"),
    ]))
    elements.append(table)
    doc.build(elements)
    return buf.getvalue()