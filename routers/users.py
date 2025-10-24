from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import User
from schemas import UserOut

router = APIRouter()

@router.get("/{user_id}", response_model=UserOut)
def upsert_user(user_id: int, db: Session = Depends(get_db)):
    """
    *Sin registro*. Si no existe, se crea automáticamente con ese `user_id`.
    Esto permite que el usuario use su número como PK.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    # Crear si no existe (upsert simple)
    user = User(id=user_id)
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se pudo crear el usuario")
    db.refresh(user)
    return user
