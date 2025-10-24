from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from db import get_db
from models import ExerciseHabit, User
from schemas import ExerciseHabitCreate, ExerciseHabitOut
from utils.dates import today_in_tz

router = APIRouter()

# Helper para asegurar que el usuario exista (y autocrearlo)
def ensure_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/{user_id}/exercise-habits", response_model=ExerciseHabitOut, status_code=status.HTTP_201_CREATED)
def create_exercise_habit(user_id: int, payload: ExerciseHabitCreate, db: Session = Depends(get_db)):
    ensure_user(db, user_id)
    habit = ExerciseHabit(user_id=user_id, name=payload.name, kind=payload.kind, streak=0, last_done=None)
    db.add(habit)
    try:
        db.commit()
        db.refresh(habit)
        return habit
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un hábito con ese nombre para este usuario")

@router.get("/{user_id}/exercise-habits", response_model=List[ExerciseHabitOut])
def list_exercise_habits(user_id: int, db: Session = Depends(get_db)):
    ensure_user(db, user_id)
    return (
        db.query(ExerciseHabit)
        .filter(ExerciseHabit.user_id == user_id)
        .order_by(ExerciseHabit.id.asc())
        .all()
    )

@router.get("/{user_id}/exercise-habits/{habit_id}", response_model=ExerciseHabitOut)
def get_exercise_habit(user_id: int, habit_id: int, db: Session = Depends(get_db)):
    ensure_user(db, user_id)
    habit = (
        db.query(ExerciseHabit)
        .filter(ExerciseHabit.user_id == user_id, ExerciseHabit.id == habit_id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return habit

@router.delete("/{user_id}/exercise-habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_habit(user_id: int, habit_id: int, db: Session = Depends(get_db)):
    ensure_user(db, user_id)
    habit = (
        db.query(ExerciseHabit)
        .filter(ExerciseHabit.user_id == user_id, ExerciseHabit.id == habit_id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    db.delete(habit)
    db.commit()
    return None

@router.post("/{user_id}/exercise-habits/{habit_id}/done", response_model=ExerciseHabitOut)
def mark_exercise_done(
    user_id: int,
    habit_id: int,
    tz: Optional[str] = Query(None, description="IANA timezone, ej: America/Bogota"),
    db: Session = Depends(get_db),
):
    ensure_user(db, user_id)
    habit = (
        db.query(ExerciseHabit)
        .filter(ExerciseHabit.user_id == user_id, ExerciseHabit.id == habit_id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    today = today_in_tz(tz)
    if habit.last_done == today:
        return habit  # idempotente

    if habit.last_done == (today - timedelta(days=1)):
        habit.streak = (habit.streak or 0) + 1
    else:
        habit.streak = 1
    habit.last_done = today

    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

# Extra: marcar por nombre
from pydantic import BaseModel
class DoneByName(BaseModel):
    name: str

@router.post("/{user_id}/exercise-habits:done-by-name", response_model=ExerciseHabitOut)
def mark_done_by_name(
    user_id: int,
    payload: DoneByName,
    tz: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    ensure_user(db, user_id)
    habit = (
        db.query(ExerciseHabit)
        .filter(ExerciseHabit.user_id == user_id, ExerciseHabit.name.ilike(payload.name))
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")
    return mark_exercise_done(user_id=user_id, habit_id=habit.id, tz=tz, db=db)
