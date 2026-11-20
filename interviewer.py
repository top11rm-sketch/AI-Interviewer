import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from models import InterviewAnalysis, InterviewPlan
from prompts import ANALYST_PROMPT, INTERVIEWER_SYSTEM_PROMPT, PLANNER_PROMPT

load_dotenv()

client = genai.Client()
MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def generate_plan(topic: str) -> InterviewPlan:
    """Stage 1: Generate a structured 4-question interview plan for the topic."""
    prompt = PLANNER_PROMPT.format(topic=topic)

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InterviewPlan,
        ),
    )
    return response.parsed


def get_next_question(
    topic: str,
    plan: InterviewPlan,
    messages: list[dict],
    current_turn: int,
) -> str:
    """Stage 2: Generate the next adaptive interview question based on chat history."""
    formatted_questions = "\n".join(
        f"{idx}. {q}" for idx, q in enumerate(plan.questions, start=1)
    )

    system_instruction = INTERVIEWER_SYSTEM_PROMPT.format(
        topic=topic,
        research_goal=plan.research_goal,
        plan_questions=formatted_questions,
        current_turn=current_turn,
        total_turns=len(plan.questions),
    )

    conversation = messages if messages else [
        {"role": "user", "parts": [{"text": "I am ready to begin the interview."}]}
    ]

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=conversation,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )
    return response.text.strip()


def analyze_interview(topic: str, transcript_text: str) -> InterviewAnalysis:
    """Stage 3: Synthesize themes, sentiment score, and keywords from the transcript."""
    prompt = ANALYST_PROMPT.format(
        topic=topic,
        transcript=transcript_text,
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InterviewAnalysis,
        ),
    )
    return response.parsed