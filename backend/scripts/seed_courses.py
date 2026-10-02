from app.database import SessionLocal
from app.models.course import Course, CourseSeat


BRANCHES = ["CSE", "CSBS", "CV", "EE", "ET", "IT", "ME", "AI", "DS", "CS", "IIOT", "RAI"]

COURSES = [
    ("CSE",  "Indian Cyber Law"),
    ("AI",   "Responsible AI"),
    ("CS",   "Fundamentals of Network Security"),
    ("CV",   "Basics of Civil Engineering"),
    ("EE",   "Basic Electrical Machines"),
    ("ET",   "Electronic Devices and Applications"),
    ("IIOT", "Microcontrollers: Arduino Playground"),
    ("IT",   "Fundamentals of Cloud Computing"),
    ("ME",   "Orientation Course on Entrepreneurship"),
    ("DS",   "Data Engineering"),
    ("RAI",  "Gen AI and Robotics"),
]

QUOTA = {"CSE": 14}
DEFAULT_QUOTA = 7


def seed():
    db = SessionLocal()
    try:
        if db.query(Course).count() > 0:
            print("Courses already seeded. Skipping.")
            return

        for offering_branch, course_name in COURSES:
            course = Course(branch_name=offering_branch, course_name=course_name,
                            syllabus_pdf=None)
            db.add(course)
            db.flush()
            for student_branch in BRANCHES:
                db.add(CourseSeat(
                    course_id=course.id,
                    branch=student_branch,
                    seats=QUOTA.get(student_branch, DEFAULT_QUOTA),
                    filled_seats=0,
                ))

        db.commit()
        print(f"Seeded {len(COURSES)} courses × {len(BRANCHES)} branches.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()