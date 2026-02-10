from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.database import Base


class GradingStepResult(Base):
    __tablename__ = "grading_step_results"

    result_id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(String(100), ForeignKey("cells.cell_id"))
    step_number = Column(Integer)
    step_type = Column(String(100))
    end_v = Column(Numeric(5, 3))
    end_cap = Column(Numeric(6, 2))
    time_min = Column(Numeric(6, 2))
