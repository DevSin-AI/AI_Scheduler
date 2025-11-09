import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

load_dotenv()
print(os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini 모델 로드 (속도/비용/정확도 고려해 선택)
MODEL = "gemini-2.5-flash-lite"

def parse_schedule_text(text: str):
    """
    사용자의 자연어 입력을 표준화된 일정 포맷(JSON)으로 변환.
    """
    prompt = f"""
    You are a scheduler system text parser.
    You extract information from the user's statements and return them back in JSON form.
    
    The JSON form should include a title, start time and end time, whether its a fixed schedule, whether it will repeat every few days  and in what duration, and description.
    The start time and end time is denoted by the date and time in clean 30 minute chunks. This means you can't denote them like 11:20, but 11:30 or 11:00. The user may give you the wanted duration or start and end time but also may not. If they don't, give a recommend amount of time accordingly.
    A fixed schedule is schedules like work or school - a fixed pan that is more likely to be hard to change for a different schedule. If it is fixed it will be denoted as 1, else if you can't know and need a default value or it isn't a fixed schedual - input 0.
    Repeat value will be set to zero if no repetition is implied or it is said for this schedule to be a one time thing. Else, the value will be how many days untill another repeat.
    Description is set to null if no other important aspects immerge, else give description of the task.
    
    For example, if someone said they are going to exercise tomorrow once in 7pm on 2025.11.09 with no indication on it being a fixed schedule nor a repeated one;
    "title":"exercise","start":"2025-11-10T19:00:00","end":"2025-11-10T20:00:00", "fixed":0, "repeat":0, "description":null
    
    Only give back the json format accordingly. Do not include explanations, markdowns, or comments.
    If certain important parameters were not given by the user, simply fill them in with recommended values that you come up with and don't ask back.
    Only give back JSON. Note that today is {today}.
    
    입력: "{text}"
    """

    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Gemini가 종종 코드블록(```json```)을 붙이기 때문에 제거
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").split("json")[-1].strip()

    try:
        parsed = json.loads(raw_output)
        return parsed
    except json.JSONDecodeError:
        return {"error": "JSON 파싱 실패", "raw_output": raw_output}
