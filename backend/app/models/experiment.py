from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor_id = Column(String(32), nullable=False)
    mode = Column(String(16), nullable=False)                # "cgpa" | "lottery" | "hybrid"
    seed = Column(Integer, nullable=True)
    total_students = Column(Integer, nullable=False)
    first_choice_pct = Column(Float, nullable=False)
    fifth_choice_pct = Column(Float, nullable=False)
    fallback_pct = Column(Float, nullable=False)
    p_value = Column(Float, nullable=True)
    cramers_v = Column(Float, nullable=True)