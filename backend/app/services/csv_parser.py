import csv
import io
import secrets
import string

STUDENT_HEADERS = [
    "UID",
    "Name of the students",
    "CGPA (As per the I semester)",
    "Contact number",
    "Name of the Parent Branch",
]

ADMIN_HEADERS = ["admin_id", "name", "branch"]


def parse_student_csv(raw: bytes) -> tuple[list[dict], list[str]]:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return [], ["CSV is empty"]

    header_map = {h.strip().lower(): h for h in reader.fieldnames}
    resolved = {}
    for want in STUDENT_HEADERS:
        key = want.strip().lower()
        if key not in header_map:
            return [], [f"Missing required column: '{want}'"]
        resolved[want] = header_map[key]

    rows, errors = [], []
    for i, row in enumerate(reader, start=2):
        try:
            uid = (row[resolved["UID"]] or "").strip().upper()
            name = (row[resolved["Name of the students"]] or "").strip()
            cgpa_raw = (row[resolved["CGPA (As per the I semester)"]] or "").strip()
            contact = (row[resolved["Contact number"]] or "").strip()
            branch = (row[resolved["Name of the Parent Branch"]] or "").strip().upper()

            if not uid or not name or not cgpa_raw or not branch:
                errors.append(f"Row {i}: missing required value")
                continue

            try:
                cgpa = float(cgpa_raw)
            except ValueError:
                errors.append(f"Row {i}: CGPA not numeric ('{cgpa_raw}')")
                continue

            if not (0 <= cgpa <= 10):
                errors.append(f"Row {i}: CGPA out of range ({cgpa})")
                continue

            rows.append({"uid": uid, "name": name, "cgpa": cgpa,
                         "contact_no": contact, "parent_branch": branch})
        except Exception as e:
            errors.append(f"Row {i}: {e}")
    return rows, errors


def parse_admin_csv(raw: bytes) -> tuple[list[dict], list[str]]:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return [], ["CSV is empty"]

    header_map = {h.strip().lower(): h for h in reader.fieldnames}
    resolved = {}
    for want in ADMIN_HEADERS:
        if want.lower() not in header_map:
            return [], [f"Missing required column: '{want}'"]
        resolved[want] = header_map[want.lower()]

    rows, errors = [], []
    for i, row in enumerate(reader, start=2):
        admin_id = (row[resolved["admin_id"]] or "").strip()
        name = (row[resolved["name"]] or "").strip()
        branch = (row[resolved["branch"]] or "").strip().upper()

        if not admin_id or not name or not branch:
            errors.append(f"Row {i}: missing required value")
            continue

        rows.append({"admin_id": admin_id, "name": name, "branch": branch})
    return rows, errors


def generate_password(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))