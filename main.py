import json
import re
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from interviewer import analyze_interview, generate_plan, get_next_question
from models import InterviewAnalysis, InterviewPlan

console = Console()


def prompt_non_empty(label: str) -> str:
    """Keep prompting until the user enters a non-empty string."""
    while True:
        value = Prompt.ask(label).strip()
        if value:
            return value
        console.print("[yellow]Please enter a response before continuing.[/yellow]")


def save_session(
    topic: str,
    plan: InterviewPlan,
    transcript: list[dict],
    analysis: InterviewAnalysis,
) -> Path:
    """Save the complete interview plan, transcript, and analysis to a JSON file."""
    output_dir = Path("transcripts")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40] or "interview"
    file_path = output_dir / f"{timestamp}_{slug}.json"

    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "topic": topic,
        "interview_plan": plan.model_dump(),
        "transcript": transcript,
        "analysis": analysis.model_dump(),
    }

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return file_path


def display_analysis(topic: str, analysis: InterviewAnalysis, saved_path: Path) -> None:
    """Render the post-interview summary and bonus analysis metrics in a Rich table."""
    console.print()
    console.print(
        Panel(
            f"[bold]Topic:[/bold] {topic}\n\n{analysis.executive_summary}",
            title="[bold green]Interview Summary[/bold green]",
            border_style="green",
        )
    )

    table = Table(title="Key Insights & Bonus Analysis", show_lines=True)
    table.add_column("Metric", style="bold cyan", width=20)
    table.add_column("Result", style="white")

    table.add_row("Key Themes", "\n".join(f"• {t}" for t in analysis.key_themes))
    table.add_row(
        "Notable Quotes",
        "\n".join(f'"{q}"' for q in analysis.notable_quotes) or "None extracted",
    )
    table.add_row(
        "Sentiment Score",
        f"{analysis.sentiment_label} ({analysis.sentiment_score:+.2f} on -1.0 to +1.0 scale)",
    )
    table.add_row("Tone / Emotions", ", ".join(analysis.emotion_tags))
    table.add_row("Extracted Keywords", ", ".join(analysis.keywords))

    console.print(table)
    console.print(f"\n[dim]Full transcript and analysis saved to:[/dim] [bold]{saved_path}[/bold]\n")


def run_interview() -> None:
    console.print(
        Panel(
            "[bold cyan]Mini AI Interviewer[/bold cyan]\n"
            "An interactive qualitative research tool powered by Gemini.\n"
            "[dim]Type 'quit' at any answer prompt to exit early.[/dim]",
            border_style="cyan",
        )
    )

    topic = prompt_non_empty("\n[bold]Enter an interview topic[/bold] (e.g., AI in the workplace)")

    try:
        with console.status("[cyan]Designing structured interview guide...[/cyan]"):
            plan = generate_plan(topic)

        console.print(f"\n[bold green]Research Goal:[/bold green] {plan.research_goal}\n")

        messages: list[dict] = []
        transcript: list[dict] = []
        total_turns = len(plan.questions)

        for turn in range(1, total_turns + 1):
            with console.status(f"[cyan]Preparing question {turn} of {total_turns}...[/cyan]"):
                question = get_next_question(topic, plan, messages, turn)

            console.print(
                Panel(
                    question,
                    title=f"[bold magenta]Interviewer ({turn}/{total_turns})[/bold magenta]",
                    border_style="magenta",
                )
            )

            answer = prompt_non_empty("[bold yellow]Your answer[/bold yellow]")
            if answer.lower() in {"quit", "exit"}:
                console.print("\n[yellow]Interview ended early. Goodbye![/yellow]")
                return

            if turn == 1:
                messages.append({"role": "user", "parts": [{"text": "I am ready to begin the interview."}]})
            messages.append({"role": "model", "parts": [{"text": question}]})
            messages.append({"role": "user", "parts": [{"text": answer}]})

            transcript.append({"turn": turn, "question": question, "answer": answer})
            console.print()

        formatted_transcript = "\n\n".join(
            f"Interviewer: {item['question']}\nParticipant: {item['answer']}"
            for item in transcript
        )

        with console.status("[cyan]Analyzing responses, sentiment, and keywords...[/cyan]"):
            analysis = analyze_interview(topic, formatted_transcript)

        saved_path = save_session(topic, plan, transcript, analysis)
        display_analysis(topic, analysis, saved_path)

    except Exception as exc:
        console.print(f"\n[bold red]API or Runtime Error:[/bold red] {exc}")
        console.print("[dim]Check your GEMINI_API_KEY in .env and your internet connection.[/dim]")


if __name__ == "__main__":
    run_interview()