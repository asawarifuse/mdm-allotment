# MDM Course Allotment System

College-wide MDM course allotment with hard quota (5 per branch per course).

- Frontend: React + Tailwind (Vercel)
- Backend: FastAPI + SQLAlchemy (Render)
- DB: PostgreSQL (prod) / SQLite (dev)
- Auth: JWT + RBAC (student / branch_admin / main_admin)

## Constraints
- 12 branches × 60 students = 720 students
- 12 courses × 60 seats = 720 seats
- 5 seats per (course, branch)

## Docs
- docs/allotment.md — formal spec + complexity
- docs/threat-model.md — security analysis
- docs/load-test.md — performance report