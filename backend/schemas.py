from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    file_path: str
    parsed_text: str
    ats_score: Optional[int] = None
    skills: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewStartRequest(BaseModel):
    user_id: str
    interview_type: str # HR, TECHNICAL, DSA

class InterviewResponse(BaseModel):
    id: str
    user_id: str
    interview_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DialogueResponse(BaseModel):
    id: str
    interview_id: str
    question: str
    answer: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None

    class Config:
        from_attributes = True

class AnswerRequest(BaseModel):
    dialogue_id: str
    answer_text: str

class CodeSubmitRequest(BaseModel):
    user_id: str
    question_title: str
    code: str
    language_id: int # Judge0 language ID (e.g., 71 for Python)

class CodeSubmitResponse(BaseModel):
    id: str
    status: str
    output: Optional[str] = None
    ai_feedback: Optional[str] = None
    time_complexity: Optional[str] = None

    class Config:
        from_attributes = True

class RunCodeRequest(BaseModel):
    code: str
    language_id: int
    question_title: str

class RunCodeResponse(BaseModel):
    output: str
    status: str

class DashboardResponse(BaseModel):
    total_interviews: int
    total_coding_attempts: int
    average_score: float
    weak_topics: str
    recent_scores: list[float]
    recent_coding_status: list[str]
