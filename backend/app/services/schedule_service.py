from sqlmodel import Session, select
from ..models.schedule import Schedule
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate
from datetime import datetime

class ScheduleService:
    def create(self, payload: ScheduleCreate, session: Session) -> Schedule:
        s = Schedule(**payload.dict())
        session.add(s)
        session.commit()
        session.refresh(s)
        # 선호도 반영: 추천 벡터에 반영 (간단하게 호출)
        from .preferences import preference_manager
        preference_manager.update_on_create(s, session=session)
        return s

    def list_all(self, session: Session):
        q = select(Schedule).order_by(Schedule.start)
        return session.exec(q).all()

    def update(self, schedule_id: int, payload: ScheduleUpdate, session: Session):
        s = session.get(Schedule, schedule_id)
        if not s:
            return None
        for k, v in payload.dict(exclude_unset=True).items():
            setattr(s, k, v)
        s.updated_at = datetime.utcnow()
        session.add(s)
        session.commit()
        session.refresh(s)
        from .preferences import preference_manager
        preference_manager.update_on_update(s, session=session)
        return s

    def delete(self, schedule_id: int, session: Session) -> bool:
        s = session.get(Schedule, schedule_id)
        if not s:
            return False
        session.delete(s)
        session.commit()
        from .preferences import preference_manager
        preference_manager.update_on_delete(s, session=session)
        return True