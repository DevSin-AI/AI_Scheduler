from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.database import get_session, engine
from .schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate
from .services.schedule_service import ScheduleService
from .services.preferences import preference_manager
from app.services.llm_adapter import parse_schedule_text

app = FastAPI(title="AI-Scheduler Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ScheduleService()

@app.on_event("startup")
def on_startup():
    # DB 테이블 생성
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

@app.post("/schedules/", response_model=ScheduleRead)
def create_schedule(payload: ScheduleCreate, session: Session = Depends(get_session)):
    schedule = service.create(payload, session)
    return schedule

@app.get("/schedules/", response_model=list[ScheduleRead])
def list_schedules(session: Session = Depends(get_session)):
    return service.list_all(session)

@app.put("/schedules/{schedule_id}", response_model=ScheduleRead)
def update_schedule(schedule_id: int, payload: ScheduleUpdate, session: Session = Depends(get_session)):
    updated = service.update(schedule_id, payload, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, session: Session = Depends(get_session)):
    ok = service.delete(schedule_id, session)
    if not ok:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"ok": True}

class RecommendRequest(BaseModel):
    text: str

@app.post("/recommend/")
def recommend(req: RecommendRequest):
    result = parse_schedule_text(req.text)
    return {"parsed_result": result}

@app.post("/recommend/feedback")
def recommend_feedback(feedback: dict):
    # feedback: {"accepted": true/false, "recommendations": [...], "type":"game"}
    preference_manager.apply_feedback(feedback)
    return {"ok": True}