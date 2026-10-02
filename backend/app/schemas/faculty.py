from pydantic import BaseModel


class StudentPreferenceRow(BaseModel):
    uid: str
    name: str
    cgpa: float
    parent_branch: str
    rank: int


class FacultyCourseInfo(BaseModel):
    course_id: int
    course_name: str
    branch_name: str
    students_selected: list[StudentPreferenceRow]
    seats_by_branch: list[dict]


class SeatUpdate(BaseModel):
    branch: str
    seats: int