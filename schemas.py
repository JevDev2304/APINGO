from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

class UserOut(BaseModel):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ExerciseHabitCreate(BaseModel):
    name: str = Field(default="Ejercicio", min_length=1, max_length=120)
    kind: str = Field(default="general", min_length=1, max_length=50)

class ExerciseHabitOut(BaseModel):
    id: int
    user_id: int
    name: str
    kind: str
    streak: int
    last_done: Optional[date]
    created_at: datetime
    class Config:
        from_attributes = True