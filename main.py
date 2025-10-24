from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.users import router as users_router
from routers.exercise import router as exercise_router

app = FastAPI(title="Habits & Streaks API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(exercise_router, prefix="/users", tags=["exercise"])

@app.get("/health")
def health():
    return {"ok": True}
