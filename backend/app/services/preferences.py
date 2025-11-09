from typing import Dict, Tuple, Any
import math
from datetime import datetime

# 단순 구현: Type별로 7x48 실수 값을 메모리에 유지
# production에서는 사용자별로 DB에 저장

class PreferenceManager:
    def __init__(self):
        self.type_vectors: Dict[str, list] = {}

    def ensure_type(self, t: str):
        if t not in self.type_vectors:
            # 7일 x 48슬롯(30분 단위)
            self.type_vectors[t] = [[0.0 for _ in range(48)] for _ in range(7)]

    def datetime_to_slot(self, dt: datetime) -> Tuple[int, int]:
        # weekday: 0(Mon)-6(Sun) -> convert to 0(Sun)? We'll use Python's 0=Mon
        day = dt.weekday()  # 0=Mon
        slot = dt.hour * 2 + (1 if dt.minute >= 30 else 0)
        return day, slot

    def update_on_create(self, schedule, session=None):
        self.ensure_type(schedule.type)
        day, slot = self.datetime_to_slot(schedule.start)
        self.type_vectors[schedule.type][day][slot] += 0.2

    def update_on_update(self, schedule, session=None):
        # 간단히 증가 (더 정교한 로직 가능)
        self.update_on_create(schedule)

    def update_on_delete(self, schedule, session=None):
        # 삭제는 영향력을 낮춤
        self.ensure_type(schedule.type)
        day, slot = self.datetime_to_slot(schedule.start)
        self.type_vectors[schedule.type][day][slot] = max(0.0, self.type_vectors[schedule.type][day][slot] - 0.1)

    def recommend_times(self, parsed: Dict[str, Any], session=None):
        # parsed: {"type":"game","count":2,"constraints":["evening","weekend"]}
        t = parsed.get("type")
        count = parsed.get("count", 1)
        constraints = parsed.get("constraints", [])
        self.ensure_type(t)

        candidates = []
        vec = self.type_vectors[t]
        for day in range(7):
            for slot in range(48):
                score = vec[day][slot]
                # constraints 처리: 간단한 가중치
                hour = slot // 2
                if "evening" in constraints and (hour < 18 or hour > 23):
                    score -= 1
                if "weekend" in constraints and day not in (5, 6):
                    score -= 1
                candidates.append(((day, slot), score))
        candidates.sort(key=lambda x: -x[1])
        picks = [self.slot_to_readable(c[0]) for c in candidates[:count]]
        return picks

    def apply_feedback(self, feedback: Dict):
        accepted = feedback.get("accepted", False)
        t = feedback.get("type")
        recs = feedback.get("recommendations", [])
preference_manager = PreferenceManager()