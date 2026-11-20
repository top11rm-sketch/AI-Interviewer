# Mini AI Interviewer

A lightweight, interactive command-line qualitative research tool inspired by [Anthropic Interviewer](https://www.anthropic.com/news/anthropic-interviewer). Given any user-selected topic, the application dynamically designs a structured interview guide, conducts an adaptive multi-turn conversation, synthesizes key insights (including numerical sentiment scoring and keyword extraction), and archives the session to JSON.

---

## Core Concepts & Architecture

Rather than relying on a single monolithic prompt, this system replicates Anthropic Interviewer's **three-stage qualitative research pipeline**:

```text
[User Enters Topic]
        │
        ▼
1. PLANNER STAGE ──────► Generates a 4-question research guide (Pydantic-validated JSON)
        │
        ▼
2. INTERVIEW LOOP ─────► Conducts 4 sequential, adaptive turns using conversation memory
   (User ↔ Gemini)       • Listens actively without lecturing or stacking questions
                         • Adapts follow-up phrasing based on participant responses
        │
        ▼
3. ANALYST STAGE ──────► Synthesizes executive summary, themes, verbatim quotes,
                         sentiment score (-1.0 to +1.0), emotion tags & keywords
        │
        ▼
4. JSON STORAGE ───────► Exports timestamped session file to `transcripts/`
```

### Design Decisions Mapped to Evaluation Criteria

* **Code Clarity & Modular Structure:** Separated into four single-responsibility modules—data contracts (`models.py`), prompt templates (`prompts.py`), LLM orchestration (`interviewer.py`), and terminal UI/storage (`main.py`).
* **Prompt Engineering & Reliable LLM Interaction:**
  * Uses explicit XML delimiters (`<topic>`, `<interview_plan>`, `<rules>`, `<transcript>`) to isolate instructions from dynamic user input.
  * Enforces strict **Structured Outputs** via Pydantic (`response_schema`), guaranteeing valid JSON for both planning and post-interview analysis with zero manual string parsing.
* **Polished Terminal User Experience:** Built with `rich` to provide clear visual hierarchy, progress tracking (`Question X of 4`), non-blocking loading spinners, formatted insight tables, input validation, and graceful early exit (`quit`).

---

## Features & Assignment Coverage

| Requirement | Implementation Details |
| :--- | :--- |
| **Custom Topic Selection** | Prompts the user for any topic (e.g., *"AI in the workplace"*, *"productivity tools"*, *"scientific research"*). |
| **3–5 Sequential Questions** | Stage 1 generates a 4-question progressive guide moving from concrete context to deeper reflection. |
| **Interactive Answer Collection** | Multi-turn terminal chat loop maintaining full conversation history (`user` / `model` roles). |
| **End-of-Interview Summary** | Produces an executive summary, overarching themes, and verbatim illustrative quotes. |
| **Structured Persistence** | Automatically saves metadata, plan, Q&A transcript, and analysis to `transcripts/<timestamp>_<topic>.json`. |
| **Bonus: Sentiment & Keywords** | Extracts a continuous sentiment score (`-1.0` to `+1.0`), categorical label, emotion tags, and top domain keywords. |

---

## Project Structure

```text
AI-Interviewer/
├── main.py             # CLI entry point, Rich UI rendering, conversation loop, and JSON export
├── interviewer.py      # Google GenAI SDK integration (Planner, Interviewer, Analyst functions)
├── prompts.py          # Decoupled XML-structured system and task prompts
├── models.py           # Pydantic schemas (InterviewPlan & InterviewAnalysis)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Excludes .env, virtual environments, and cache files
└── transcripts/        # Auto-generated JSON interview archives
```

---

## Quickstart & Setup

### Prerequisites
* Python 3.10 or higher
* A free API key from [Google AI Studio](https://aistudio.google.com/) (works on the $0 free tier with no billing account required)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/top11rm-sketch/AI-Interviewer.git
   cd AI-Interviewer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # macOS / Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy `.env.example` to `.env` and add your API key:
   ```bash
   cp .env.example .env
   ```
   Inside `.env`:
   ```env
   GEMINI_API_KEY=your_google_ai_studio_api_key
   GEMINI_MODEL=gemini-3.5-flash-lite
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

---

## Sample JSON Output Schema

Each completed interview is saved automatically in `transcripts/` using the following structure:

```json
{
  "timestamp": "2026-11-20T12:45:00",
  "topic": "AI in the workplace",
  "interview_plan": {
    "research_goal": "Explore how daily AI tool adoption impacts workflow efficiency and trust.",
    "questions": ["..."]
  },
  "transcript": [
    {
      "turn": 1,
      "question": "...",
      "answer": "..."
    }
  ],
  "analysis": {
    "executive_summary": "...",
    "key_themes": ["Workflow Automation", "Verification Overhead"],
    "notable_quotes": ["..."],
    "sentiment_label": "Mixed",
    "sentiment_score": 0.25,
    "emotion_tags": ["pragmatic", "cautiously optimistic"],
    "keywords": ["code review", "boilerplate", "hallucinations", "productivity"]
  }
}
```