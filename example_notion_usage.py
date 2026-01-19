"""
Example usage of the Notion Job Tracker integration.
This demonstrates how to add jobs to your Notion database.
"""

from datetime import datetime
from models import (
    JobListing,
    Company,
    ApplicationData,
    ApplicationStatus,
    JobType,
    WorkLocation
)
from notion_client import create_notion_tracker


def example_add_job():
    """Example: Add a job to Notion database."""

    # Create a company object
    company = Company(
        name="Anthropic",
        website="https://anthropic.com",
        linkedin_url="https://linkedin.com/company/anthropic",
        industry="Artificial Intelligence",
        size="51-200 employees",
        description="AI safety and research company",
        location="San Francisco, CA"
    )

    # Create a job listing
    job = JobListing(
        job_id="anthropic-ml-engineer-001",
        title="Senior Machine Learning Engineer",
        company=company,
        location="San Francisco, CA (Hybrid)",
        work_location=WorkLocation.HYBRID,
        job_type=JobType.FULL_TIME,
        description="Join our team to work on cutting-edge AI safety research...",
        requirements=[
            "5+ years of ML experience",
            "Strong Python skills",
            "Experience with PyTorch/TensorFlow"
        ],
        responsibilities=[
            "Design and implement ML models",
            "Collaborate with research team",
            "Deploy models to production"
        ],
        salary_range="$180,000 - $250,000",
        posted_date=datetime.now(),
        application_url="https://jobs.anthropic.com/apply/123",
        linkedin_url="https://linkedin.com/jobs/view/123456",
        easy_apply=False,
        skills_required=["Python", "PyTorch", "Machine Learning", "AI Safety"],
        experience_level="Senior",
        applicant_count=45
    )

    # Create application data
    application = ApplicationData(
        job=job,
        status=ApplicationStatus.IN_PROGRESS,
        match_score=85.5,
        notes="Great match! Company culture aligns with values. Need to prepare examples of ML projects.",
        contact_email="recruiter@anthropic.com",
        contact_name="Jane Doe"
    )

    # Add to Notion
    tracker = create_notion_tracker()
    page_id = tracker.add_or_update_job(application)

    print(f"✓ Job added to Notion! Page ID: {page_id}")
    print(f"  Company: {job.company.name}")
    print(f"  Position: {job.title}")
    print(f"  Match Score: {application.match_score}%")


def example_query_jobs():
    """Example: Query jobs from Notion database."""

    tracker = create_notion_tracker()

    # Get all jobs
    all_jobs = tracker.query_jobs(limit=10)
    print(f"\nFound {len(all_jobs)} jobs in database")

    # Get jobs by status
    submitted = tracker.query_jobs(status=ApplicationStatus.SUBMITTED)
    print(f"Submitted applications: {len(submitted)}")

    # Get jobs by company
    anthropic_jobs = tracker.query_jobs(company="Anthropic")
    print(f"Anthropic applications: {len(anthropic_jobs)}")


def example_get_stats():
    """Example: Get application statistics."""

    tracker = create_notion_tracker()
    stats = tracker.get_statistics()

    print("\n📊 Application Statistics:")
    print(f"  Total Applications: {stats['total']}")
    print(f"  This Week: {stats['this_week']}")
    print(f"  This Month: {stats['this_month']}")

    print("\n  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")


def example_update_job():
    """Example: Update an existing job application."""

    tracker = create_notion_tracker()

    # Find job by URL
    job_url = "https://jobs.anthropic.com/apply/123"
    existing_job = tracker.get_job_by_url(job_url)

    if existing_job:
        # Update the status
        print(f"\nUpdating job: {existing_job['id']}")

        # You would normally fetch the full ApplicationData here
        # For this example, we'll create a mock update
        # In practice, you'd load the existing data and modify it

        # tracker.update_job(page_id, updated_application_data)
        print("Job updated successfully!")
    else:
        print("Job not found")


if __name__ == "__main__":
    print("=" * 60)
    print("Notion Job Tracker - Example Usage")
    print("=" * 60)

    try:
        # Make sure you have .env configured before running this!

        # Example 1: Add a job
        print("\n1. Adding a job to Notion...")
        example_add_job()

        # Example 2: Query jobs
        print("\n2. Querying jobs...")
        example_query_jobs()

        # Example 3: Get statistics
        print("\n3. Getting statistics...")
        example_get_stats()

    except FileNotFoundError:
        print("\n❌ Error: .env file not found!")
        print("Please create a .env file based on .env.example")
        print("Make sure to set NOTION_API_KEY and NOTION_DATABASE_ID")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Created a .env file with your API keys")
        print("  2. Set up your Notion integration")
        print("  3. Shared the database with your integration")
