# domain/prakriti/models.py
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Dosha = Literal["vata", "pitta", "kapha", "tridoshic"]

class Profile(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None

class PrakritiQuestion(BaseModel):
    question: str
    answer: str  # free text or option id

class GeneratePrakritiRequest(BaseModel):
    profile: Profile
    questions: List[PrakritiQuestion] = Field(default_factory=list)
    model: Optional[str] = None
    prompt_version: Optional[int] = None
    force: bool = False

class PrakritiDistribution(BaseModel):
    vata: float = Field(ge=0, le=100)
    pitta: float = Field(ge=0, le=100)
    kapha: float = Field(ge=0, le=100)

class PrakritiGuidance(BaseModel):
    foods_to_favor: List[str]
    foods_to_avoid: List[str]
    lifestyle_tips: List[str]

class GeneratePrakritiResponse(BaseModel):
    primaryDosha: Dosha
    secondaryDosha: Optional[Dosha] = None
    distribution: PrakritiDistribution
    guidance: PrakritiGuidance
    notes: Optional[str] = None
    meta: dict
