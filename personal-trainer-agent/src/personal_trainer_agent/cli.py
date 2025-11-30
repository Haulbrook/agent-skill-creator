"""
CLI for Personal Trainer Agent.

Usage:
    trainer-agent analyze <input_file> [--output <output>]
    trainer-agent evaluate <input_file> --rubric <rubric_file>
    trainer-agent train <plan_file> [--data <data_file>]
    trainer-agent session --load <session_file>
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from personal_trainer_agent.main import PersonalTrainerAgent, TrainingConfig

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="trainer-agent")
def main() -> None:
    """Personal Trainer Agent - Systematically improve AI agents."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for analysis results")
@click.option("--expected", "-e", type=click.Path(exists=True), help="Expected outputs file")
def analyze(input_file: str, output: Optional[str], expected: Optional[str]) -> None:
    """Analyze agent outputs to identify weaknesses."""
    console.print(Panel.fit("Analyzing agent outputs...", style="blue"))

    # Load input
    with open(input_file) as f:
        outputs = json.load(f)

    expected_outputs = None
    if expected:
        with open(expected) as f:
            expected_outputs = json.load(f)

    # Run analysis
    trainer = PersonalTrainerAgent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Analyzing...", total=None)
        analysis = trainer.analyze(outputs, expected_outputs)

    # Display results
    _display_analysis(analysis)

    # Save if output specified
    if output:
        with open(output, "w") as f:
            json.dump(analysis, f, indent=2)
        console.print(f"\n[green]Results saved to {output}[/green]")


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--rubric", "-r", type=click.Path(exists=True), required=True, help="Rubric file")
@click.option("--baseline", "-b", type=click.Path(exists=True), help="Baseline outputs for comparison")
@click.option("--output", "-o", type=click.Path(), help="Output file for evaluation results")
def evaluate(
    input_file: str,
    rubric: str,
    baseline: Optional[str],
    output: Optional[str],
) -> None:
    """Evaluate agent outputs against a rubric."""
    console.print(Panel.fit("Evaluating agent outputs...", style="blue"))

    # Load files
    with open(input_file) as f:
        outputs = json.load(f)

    with open(rubric) as f:
        rubric_data = json.load(f)

    baseline_outputs = None
    if baseline:
        with open(baseline) as f:
            baseline_outputs = json.load(f)

    # Run evaluation
    trainer = PersonalTrainerAgent()
    results = trainer.evaluate(outputs, rubric_data, baseline_outputs)

    # Display results
    _display_evaluation(results)

    # Save if output specified
    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]Results saved to {output}[/green]")


@main.command()
@click.argument("plan_file", type=click.Path(exists=True))
@click.option("--data", "-d", type=click.Path(exists=True), help="Training data file")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def train(plan_file: str, data: Optional[str], output: Optional[str]) -> None:
    """Execute training based on an improvement plan."""
    console.print(Panel.fit("Starting training...", style="blue"))

    # Load plan
    with open(plan_file) as f:
        plan = json.load(f)

    training_data = None
    if data:
        with open(data) as f:
            training_data = json.load(f)

    # Configure trainer
    config = TrainingConfig(
        name=plan.get("name", "training_session"),
        target_agent=plan.get("target_agent", "unknown"),
        training_method=plan.get("training_method", "prompt_optimization"),
        output_dir=Path(output) if output else Path("./training_output"),
    )

    trainer = PersonalTrainerAgent(config=config)

    # Run training
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Training...", total=None)
        result = trainer.train(plan, training_data)
        progress.update(task, completed=True)

    # Display results
    _display_training_result(result)

    # Save session
    session_path = trainer.save_session()
    console.print(f"\n[green]Session saved to {session_path}[/green]")


@main.command()
@click.option("--load", "-l", type=click.Path(exists=True), help="Load existing session")
@click.option("--new", "-n", type=str, help="Start new session with name")
def session(load: Optional[str], new: Optional[str]) -> None:
    """Manage training sessions."""
    if load:
        trainer = PersonalTrainerAgent.load_session(Path(load))
        report = trainer.get_session_report()
        _display_session_report(report)
    elif new:
        config = TrainingConfig(name=new, target_agent="unknown")
        trainer = PersonalTrainerAgent(config=config)
        console.print(f"[green]Created new session: {new}[/green]")
    else:
        console.print("[yellow]Specify --load or --new[/yellow]")


@main.command()
@click.argument("outputs_file", type=click.Path(exists=True))
@click.option("--feedback", "-f", type=str, help="Human feedback to include")
def coach(outputs_file: str, feedback: Optional[str]) -> None:
    """Run a coaching session on agent outputs."""
    console.print(Panel.fit("Starting coaching session...", style="blue"))

    with open(outputs_file) as f:
        outputs = json.load(f)

    trainer = PersonalTrainerAgent()
    result = trainer.coaching_session(outputs, feedback)

    if "error" in result:
        console.print(f"[yellow]{result['error']}[/yellow]")
        console.print(f"[dim]{result.get('suggestion', '')}[/dim]")
        return

    console.print("\n[bold]Coaching Feedback:[/bold]")
    console.print(result.get("coaching_feedback", "No feedback generated"))

    if result.get("action_items"):
        console.print("\n[bold]Action Items:[/bold]")
        for item in result["action_items"]:
            console.print(f"  - {item}")


def _display_analysis(analysis: dict) -> None:
    """Display analysis results in a formatted table."""
    console.print("\n[bold]Performance Analysis[/bold]")

    # Performance metrics
    perf = analysis.get("performance", {})
    if perf:
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in perf.items():
            if isinstance(value, float):
                table.add_row(key, f"{value:.2%}")
            else:
                table.add_row(key, str(value))

        console.print(table)

    # Weaknesses
    weaknesses = analysis.get("weaknesses", [])
    if weaknesses:
        console.print("\n[bold]Identified Weaknesses[/bold]")
        for i, w in enumerate(weaknesses, 1):
            severity = w.get("severity", "unknown")
            color = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "dim"}.get(
                severity, "white"
            )
            console.print(f"  {i}. [{color}][{severity.upper()}][/{color}] {w.get('description', 'Unknown')}")


def _display_evaluation(results: dict) -> None:
    """Display evaluation results."""
    console.print("\n[bold]Evaluation Results[/bold]")

    if "rubric_scores" in results:
        scores = results["rubric_scores"]
        table = Table(title="Rubric Scores")
        table.add_column("Criterion", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Max", style="dim")

        for criterion, data in scores.items():
            if isinstance(data, dict):
                table.add_row(criterion, str(data.get("score", 0)), str(data.get("max", 10)))
            else:
                table.add_row(criterion, str(data), "10")

        console.print(table)

    if "comparison" in results:
        comp = results["comparison"]
        console.print(f"\n[bold]Comparison:[/bold] {comp.get('summary', 'No summary')}")


def _display_training_result(result: dict) -> None:
    """Display training results."""
    console.print("\n[bold]Training Results[/bold]")

    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column("Before", style="yellow")
    table.add_column("After", style="green")
    table.add_column("Change", style="magenta")

    before = result.get("before", {})
    after = result.get("after", {})

    for key in set(before.keys()) | set(after.keys()):
        b_val = before.get(key, 0)
        a_val = after.get(key, 0)
        if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
            change = a_val - b_val
            change_str = f"+{change:.2f}" if change > 0 else f"{change:.2f}"
            table.add_row(key, f"{b_val:.2f}", f"{a_val:.2f}", change_str)

    console.print(table)


def _display_session_report(report: dict) -> None:
    """Display session report."""
    console.print("\n[bold]Session Report[/bold]")

    session = report.get("session", {})
    console.print(f"Name: [cyan]{session.get('name', 'Unknown')}[/cyan]")
    console.print(f"Iterations: [green]{session.get('iteration_count', 0)}[/green]")

    metrics = report.get("metrics", {})
    if metrics.get("summary"):
        console.print("\n[bold]Metrics Summary:[/bold]")
        for key, value in metrics["summary"].items():
            console.print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
