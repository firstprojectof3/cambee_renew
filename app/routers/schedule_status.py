# app/routers/schedule_status.py
from fastapi import APIRouter
from app.schedule.jobs import get_status

router = APIRouter()

@router.get("/schedule/status")
def schedule_status():
    return get_status()
