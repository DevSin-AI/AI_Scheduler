# AI_Scheduler
Scheduler that learns user preference in planning their schedule.

//
python -m venv .venv : in backend folder if .venv is not setup

Set up by :
cd Desktop
cd AI_Scheduler
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

Normal create
curl -X POST "http://127.0.0.1:8000/schedules/" ^
 -H "Content-Type: application/json" ^
 -d "{\"title\":\"excercise\",\"start\":\"2025-11-10T19:00:00\",\"end\":\"2025-11-10T20:00:00\",\"fixed\":\"0\",\"repeat\":\"0\",\"description\":\"descriptions\"}"

Check for schedules
curl http://127.0.0.1:8000/schedules/


Ask for AI for schedule creation
curl -X POST "http://127.0.0.1:8000/recommend/" ^
 -H "Content-Type: application/json" ^
 -d "{\"text\": \"주말 저녁에 게임 일정 추천해줘\"}"

//
Open in :
Swagger UI → http://127.0.0.1:8000/docs
ReDoc → http://127.0.0.1:8000/redoc

