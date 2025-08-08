#  SQLAlchemy is an ORM — an Object-Relational Mapper
from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base


class MathOperation(Base):
    __tablename__ = 'math_operations'

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, index=True)
    input_data = Column(String)
    result = Column(Float)
