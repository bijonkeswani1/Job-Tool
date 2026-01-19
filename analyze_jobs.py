"""
CLI tool for analyzing jobs with Claude AI and generating cover letters.
"""

import argparse
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from claude_ai import create_claude_assistant
from notion_client import create_notion_tracker
from models import UserProfile, ApplicationStatus, ApplicationData, JobListing, Company
from config import get_settings

console = Console()


def create_user_profile() -> UserProfile:
    """Create user profile from config settings."""
    settings = get_settings()

    # This is a simplified version - in production, you'd load from a file or database
    return UserProfile(
        full_name=settings.full_name,
        email=settings.email,
        phone=settings.phone,
        linkedin_url=settings.linkedin_url,
        summary="Experienced professional seeking new opportunities",  # User should customize
        skills=["Python", "JavaScript", "SQL"],  # User should customize
        desired_titles=["Software Engineer", "Developer"],  # User should customize
        desired_locations=["Remote", "San Francisco"],  # User should customize
    )


def analyze_notion_jobs(limit: int = 10, status: Optional[str] = None):
    """
    Analyze jobs from Notion database with Claude AI.

    Args:
        limit: Maximum number of jobs to analyze
        status: Filter by status (e.g., "Not Started")
    """
    console.print(Panel.fit(
        "[bold cyan]Analyzing Jobs with Claude AI[/bold cyan]",
        title="Job Analysis"
    ))

    # Initialize clients
    tracker = create_notion_tracker()
    assistant = create_claude_assistant()
    user_profile = create_user_profile()

    # Get jobs from Notion
    console.print("\n[yellow]Fetching jobs from Notion...[/yellow]")

    status_filter = None
    if status:
        status_map = {
            "not started": ApplicationStatus.NOT_STARTED,
            "in progress": ApplicationStatus.IN_PROGRESS,
            "submitted": ApplicationStatus.SUBMITTED,
        }
        status_filter = status_map.get(status.lower())

    jobs_data = tracker.query_jobs(status=status_filter, limit=limit)

    if not jobs_data:
        console.print("[red]No jobs found in Notion database![/red]")
        console.print("Run [cyan]python scrape_jobs.py[/cyan] first to add jobs.")
        return

    console.print(f"[green]✓[/green] Found {len(jobs_data)} jobs to analyze\n")

    # Analyze each job
    analyses = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing jobs with AI...", total=len(jobs_data))

        for job_data in jobs_data:
            # Extract job info from Notion data
            props = job_data.get("properties", {})

            # Get title
            title_prop = props.get("Job Title", {}).get("title", [])
            title = title_prop[0].get("text", {}).get("content", "Unknown") if title_prop else "Unknown"

            # Get company
            company_prop = props.get("Company", {}).get("rich_text", [])
            company_name = company_prop[0].get("text", {}).get("content", "Unknown") if company_prop else "Unknown"

            # Get location
            location_prop = props.get("Location", {}).get("rich_text", [])
            location = location_prop[0].get("text", {}).get("content", "Unknown") if location_prop else "Unknown"

            # Get URL
            url_prop = props.get("Application URL", {}).get("url")
            job_url = url_prop or "No URL"

            # Get description from Notes (simplified - in real scenario, you'd store full description)
            notes_prop = props.get("Notes", {}).get("rich_text", [])
            description = notes_prop[0].get("text", {}).get("content", "") if notes_prop else ""

            # Create simplified JobListing object
            job = JobListing(
                job_id=job_data["id"],
                title=title,
                company=Company(name=company_name, location=location),
                location=location,
                description=description or f"{title} at {company_name}",
                application_url=job_url
            )

            progress.update(task, description=f"Analyzing: {title}")

            # Analyze with Claude
            try:
                analysis = assistant.analyze_job_match(job, user_profile)
                analyses.append((job, analysis))
            except Exception as e:
                console.print(f"[red]Error analyzing {title}: {e}[/red]")

            progress.advance(task)

    # Display results
    console.print("\n[bold green]Analysis Complete![/bold green]\n")

    # Create results table
    table = Table(title="Job Match Analysis")
    table.add_column("Job", style="yellow", width=30)
    table.add_column("Company", style="green", width=20)
    table.add_column("Score", style="cyan", width=8)
    table.add_column("Recommendation", style="magenta", width=12)

    for job, analysis in analyses:
        # Color code recommendation
        rec_color = {
            "Apply": "green",
            "Maybe": "yellow",
            "Skip": "red"
        }.get(analysis.recommendation, "white")

        table.add_row(
            job.title[:28],
            job.company.name[:18],
            f"{analysis.match_score:.1f}%",
            f"[{rec_color}]{analysis.recommendation}[/{rec_color}]"
        )

    console.print(table)

    # Show detailed analysis for top matches
    top_matches = sorted(analyses, key=lambda x: x[1].match_score, reverse=True)[:3]

    if top_matches:
        console.print("\n[bold]Top 3 Matches - Detailed Analysis:[/bold]\n")

        for i, (job, analysis) in enumerate(top_matches, 1):
            console.print(f"\n[bold cyan]#{i}. {job.title} at {job.company.name}[/bold cyan]")
            console.print(f"[cyan]Match Score: {analysis.match_score}% | Recommendation: {analysis.recommendation}[/cyan]\n")

            console.print("[green]✓ Pros:[/green]")
            for pro in analysis.pros[:3]:
                console.print(f"  • {pro}")

            console.print("\n[yellow]⚠ Cons:[/yellow]")
            for con in analysis.cons[:3]:
                console.print(f"  • {con}")

            console.print(f"\n[bold]Reasoning:[/bold] {analysis.reasoning}\n")
            console.print("─" * 80)


def generate_cover_letter_for_job(job_title: str, company_name: str):
    """
    Generate a cover letter for a specific job.

    Args:
        job_title: Job title to search for
        company_name: Company name to search for
    """
    console.print(Panel.fit(
        f"[bold cyan]Generating Cover Letter[/bold cyan]\n"
        f"Job: {job_title}\n"
        f"Company: {company_name}",
        title="Cover Letter Generator"
    ))

    # Initialize clients
    tracker = create_notion_tracker()
    assistant = create_claude_assistant()
    user_profile = create_user_profile()

    # Search for the job in Notion
    console.print("\n[yellow]Searching for job in Notion...[/yellow]")

    all_jobs = tracker.query_jobs(limit=100)
    matching_job = None

    for job_data in all_jobs:
        props = job_data.get("properties", {})

        # Get title and company
        title_prop = props.get("Job Title", {}).get("title", [])
        title = title_prop[0].get("text", {}).get("content", "") if title_prop else ""

        company_prop = props.get("Company", {}).get("rich_text", [])
        company = company_prop[0].get("text", {}).get("content", "") if company_prop else ""

        if job_title.lower() in title.lower() and company_name.lower() in company.lower():
            matching_job = job_data
            break

    if not matching_job:
        console.print(f"[red]Could not find job matching '{job_title}' at '{company_name}'[/red]")
        console.print("Make sure the job exists in your Notion database.")
        return

    console.print("[green]✓[/green] Found matching job!\n")

    # Extract job details
    props = matching_job.get("properties", {})

    title_prop = props.get("Job Title", {}).get("title", [])
    title = title_prop[0].get("text", {}).get("content", "Unknown") if title_prop else "Unknown"

    company_prop = props.get("Company", {}).get("rich_text", [])
    company = company_prop[0].get("text", {}).get("content", "Unknown") if company_prop else "Unknown"

    location_prop = props.get("Location", {}).get("rich_text", [])
    location = location_prop[0].get("text", {}).get("content", "Unknown") if location_prop else "Unknown"

    url_prop = props.get("Application URL", {}).get("url")
    job_url = url_prop or ""

    notes_prop = props.get("Notes", {}).get("rich_text", [])
    description = notes_prop[0].get("text", {}).get("content", "") if notes_prop else ""

    # Create JobListing
    job = JobListing(
        job_id=matching_job["id"],
        title=title,
        company=Company(name=company, location=location),
        location=location,
        description=description or f"{title} at {company}",
        application_url=job_url or "https://linkedin.com"
    )

    # Generate cover letter
    console.print("[yellow]Generating cover letter with Claude AI...[/yellow]\n")

    try:
        cover_letter_response = assistant.generate_cover_letter(
            job=job,
            user_profile=user_profile,
            tone="professional"
        )

        console.print("[bold green]✓ Cover Letter Generated![/bold green]\n")

        # Display the cover letter
        console.print(Panel(
            cover_letter_response.cover_letter,
            title=f"Cover Letter for {title} at {company}",
            border_style="green"
        ))

        console.print("\n[bold]Key Points Highlighted:[/bold]")
        for point in cover_letter_response.key_points:
            console.print(f"  • {point}")

        # Offer to save
        console.print(f"\n[dim]💡 Tip: Copy this cover letter and customize it further before submitting![/dim]")

    except Exception as e:
        console.print(f"[red]Error generating cover letter: {e}[/red]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze jobs and generate cover letters with Claude AI"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze jobs from Notion")
    analyze_parser.add_argument("-n", "--limit", type=int, default=10, help="Max jobs to analyze")
    analyze_parser.add_argument("-s", "--status", help="Filter by status (e.g., 'Not Started')")

    # Cover letter command
    cover_parser = subparsers.add_parser("cover-letter", help="Generate cover letter for a job")
    cover_parser.add_argument("job_title", help="Job title")
    cover_parser.add_argument("company_name", help="Company name")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_notion_jobs(limit=args.limit, status=args.status)
    elif args.command == "cover-letter":
        generate_cover_letter_for_job(args.job_title, args.company_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
