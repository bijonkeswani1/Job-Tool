"""
CLI tool for scraping LinkedIn jobs and adding them to Notion.
"""

import asyncio
import argparse
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from linkedin_scraper import scrape_linkedin_jobs
from notion_client import create_notion_tracker
from job_parser import JobParser
from models import ApplicationData, ApplicationStatus
from config import get_settings

console = Console()


async def scrape_and_save_jobs(
    keywords: str,
    location: str = "",
    limit: int = 25,
    easy_apply: bool = False,
    remote: bool = False,
    save_to_notion: bool = True,
    auto_match: bool = True
) -> List[ApplicationData]:
    """
    Scrape jobs from LinkedIn and optionally save to Notion.

    Args:
        keywords: Job search keywords
        location: Job location
        limit: Maximum number of jobs to scrape
        easy_apply: Filter for Easy Apply jobs only
        remote: Filter for remote jobs only
        save_to_notion: Save jobs to Notion database
        auto_match: Automatically calculate match scores

    Returns:
        List of ApplicationData objects
    """
    console.print(Panel.fit(
        f"[bold cyan]Scraping LinkedIn Jobs[/bold cyan]\n"
        f"Keywords: {keywords}\n"
        f"Location: {location or 'Any'}\n"
        f"Limit: {limit}",
        title="Job Search"
    ))

    applications = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scraping jobs from LinkedIn...", total=None)

        # Scrape jobs
        jobs = await scrape_linkedin_jobs(
            keywords=keywords,
            location=location,
            limit=limit,
            easy_apply=easy_apply,
            remote=remote
        )

        progress.update(task, description=f"Found {len(jobs)} jobs. Processing...")

        # Get user profile for matching
        settings = get_settings()
        user_skills = []  # You would load this from user profile

        # Process each job
        for i, job in enumerate(jobs, 1):
            # Enhanced parsing
            if not job.skills_required:
                job.skills_required = JobParser.extract_skills(job.description)

            if not job.requirements:
                job.requirements = JobParser.extract_requirements(job.description)

            if not job.responsibilities:
                job.responsibilities = JobParser.extract_responsibilities(job.description)

            # Calculate match score if requested
            match_score = None
            if auto_match:
                match_score = JobParser.calculate_match_score(
                    job_skills=job.skills_required,
                    user_skills=user_skills,
                    job_description=job.description
                )

            # Create application data
            application = ApplicationData(
                job=job,
                status=ApplicationStatus.NOT_STARTED,
                match_score=match_score
            )

            applications.append(application)

            progress.update(
                task,
                description=f"Processing job {i}/{len(jobs)}: {job.title}"
            )

        progress.update(task, description="Processing complete!")

    # Display results
    console.print(f"\n[green]✓[/green] Successfully scraped {len(jobs)} jobs\n")

    # Create results table
    table = Table(title="Scraped Jobs")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Title", style="yellow")
    table.add_column("Company", style="green")
    table.add_column("Location", style="blue")
    table.add_column("Match", style="magenta", width=8)
    table.add_column("Easy Apply", width=10)

    for i, app in enumerate(applications, 1):
        job = app.job
        match_display = f"{app.match_score:.1f}%" if app.match_score else "N/A"
        easy_apply_display = "✓" if job.easy_apply else ""

        table.add_row(
            str(i),
            job.title[:40],
            job.company.name[:30],
            job.location[:30],
            match_display,
            easy_apply_display
        )

    console.print(table)

    # Save to Notion if requested
    if save_to_notion:
        console.print("\n[bold]Saving to Notion...[/bold]")

        tracker = create_notion_tracker()
        saved_count = 0
        updated_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Saving jobs to Notion...", total=len(applications))

            for app in applications:
                try:
                    # Check if job already exists
                    existing = tracker.get_job_by_url(str(app.job.application_url))

                    if existing:
                        updated_count += 1
                        progress.update(task, description=f"Updated: {app.job.title}")
                    else:
                        saved_count += 1
                        progress.update(task, description=f"Saved: {app.job.title}")

                    # Add or update in Notion
                    app.notion_page_id = tracker.add_or_update_job(app)

                    progress.advance(task)

                except Exception as e:
                    console.print(f"[red]Error saving {app.job.title}: {e}[/red]")

        console.print(f"\n[green]✓[/green] Notion update complete!")
        console.print(f"  New jobs saved: {saved_count}")
        console.print(f"  Existing jobs updated: {updated_count}")

    return applications


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scrape LinkedIn jobs and add them to Notion"
    )

    parser.add_argument(
        "keywords",
        help="Job search keywords (e.g., 'Software Engineer')"
    )

    parser.add_argument(
        "-l", "--location",
        default="",
        help="Job location (e.g., 'San Francisco, CA')"
    )

    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=25,
        help="Maximum number of jobs to scrape (default: 25)"
    )

    parser.add_argument(
        "-e", "--easy-apply",
        action="store_true",
        help="Filter for Easy Apply jobs only"
    )

    parser.add_argument(
        "-r", "--remote",
        action="store_true",
        help="Filter for remote jobs only"
    )

    parser.add_argument(
        "--no-notion",
        action="store_true",
        help="Don't save jobs to Notion (just display results)"
    )

    parser.add_argument(
        "--no-match",
        action="store_true",
        help="Don't calculate match scores"
    )

    args = parser.parse_args()

    try:
        # Run the scraper
        asyncio.run(scrape_and_save_jobs(
            keywords=args.keywords,
            location=args.location,
            limit=args.limit,
            easy_apply=args.easy_apply,
            remote=args.remote,
            save_to_notion=not args.no_notion,
            auto_match=not args.no_match
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Scraping cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
