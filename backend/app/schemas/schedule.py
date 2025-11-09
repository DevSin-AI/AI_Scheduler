from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class ScheduleBase(BaseModel):
    title: str
    start: datetime
    end: datetime
    type: str
    description: Optional[str] = None

    @validator("end")
    def end_after_start(cls, v, values):
        if "start" in values and v <= values["start"]:
            raise ValueError("end must be after start")
        return v

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    title: Optional[str]
    start: Optional[datetime]
    end: Optional[datetime]
    type: Optional[str]
    description: Optional[str]

class ScheduleRead(ScheduleBase):
    id: int

    class Config:
        orm_mode = True