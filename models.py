from typing import Literal
from pydantic import BaseModel, Field


class InterviewPlan(BaseModel):
    research_goal: str = Field(
        description="A single concise sentence describing what this interview aims to uncover."
    )
    questions: list[str] = Field(
        description="An ordered list of 4 open-ended interview questions progressing from broad context to deeper reflection."
    )


class InterviewAnalysis(BaseModel):
    executive_summary: str = Field(
        description="A 2-3 sentence objective overview of the participant's perspective and key points."
    )
    key_themes: list[str] = Field(
        description="2 to 4 overarching themes identified from the participant's responses."
    )
    notable_quotes: list[str] = Field(
        description="1 to 3 exact, short quotes spoken by the participant that illustrate their views."
    )
    sentiment_label: Literal["Positive", "Neutral", "Mixed", "Negative"] = Field(
        description="Overall sentiment classification of the participant's responses."
    )
    sentiment_score: float = Field(
        ge=-1.0,
        le=1.0,
        description="Overall sentiment score from -1.0 (very negative) to 1.0 (very positive), with 0.0 as neutral.",
    )
    emotion_tags: list[str] = Field(
        description="2 to 3 specific tonal or emotional descriptors (e.g., 'optimistic', 'skeptical', 'pragmatic')."
    )
    keywords: list[str] = Field(
        description="5 to 7 specific tools, concepts, or domain keywords mentioned by the participant."
    )