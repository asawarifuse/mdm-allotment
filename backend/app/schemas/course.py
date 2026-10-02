from pydantic import BaseModel


class CourseSeatInfo(BaseModel):
    branch: str
    seats: int
    filled_seats: int
    available: int


class CourseOut(BaseModel):
    id: int
    course_name: str
    branch_name: str
    syllabus_pdf: str | None
    total_seats: int
    seats_by_branch: list[CourseSeatInfo]