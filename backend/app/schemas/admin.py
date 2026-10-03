from pydantic import BaseModel


class SeatMatrixCell(BaseModel):
    course_id: int
    course_name: str
    branch: str
    seats: int
    filled_seats: int
    available: int


class CourseRow(BaseModel):
    course_id: int
    course_name: str
    offering_branch: str


class SeatMatrixResponse(BaseModel):
    branches: list[str]
    courses: list[CourseRow]
    cells: list[SeatMatrixCell]


class MasterAllotmentRow(BaseModel):
    uid: str
    name: str
    cgpa: float
    parent_branch: str
    course_id: int
    course_name: str
    offering_branch: str
    choice_number: int | None
    allotted_at: str


class ExperimentResponse(BaseModel):
    cgpa: dict
    lottery: dict
    hybrid: dict
    p_value: float
    cramers_v: float
    interpretation: str