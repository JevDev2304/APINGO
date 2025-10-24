from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, UniqueConstraint
from db import Base, engine

class User(Base):
    __tablename__ = "users"
    # Nota: no hay registro formal; el user_id lo define el propio usuario (PK numérica)
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())

class ExerciseHabit(Base):
    __tablename__ = "exercise_habits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(120), nullable=False, default="Ejercicio")
    # Para futuro: tipo de ejercicio (correr, gym, etc.)
    kind = Column(String(50), nullable=False, default="general")
    streak = Column(Integer, nullable=False, default=0)
    last_done = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_exercise_name"),
    )

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)