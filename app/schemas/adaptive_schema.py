from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    skill_name: str
    answers: Dict[str, int]  # question_id -> chosen_index


class AdjustmentActionRequest(BaseModel):
    action: str  # "accept" or "reject"

