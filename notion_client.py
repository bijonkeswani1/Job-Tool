"""
Notion API client for LinkedIn Job Application Agent.
Handles all interactions with Notion database for job tracking.
"""

from notion_client import Client
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from models import NotionJobEntry, ApplicationStatus, JobListing, ApplicationData
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotionJobTracker:
    """Client for managing job applications in Notion database."""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize Notion client.

        Args:
            api_key: Notion API key (uses config if not provided)
            database_id: Notion database ID (uses config if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.notion_api_key
        self.database_id = database_id or settings.notion_database_id
        self.client = Client(auth=self.api_key)
        self._database_schema: Optional[Dict[str, Any]] = None

    async def get_database_schema(self) -> Dict[str, Any]:
        """
        Retrieve and cache the database schema.

        Returns:
            Database schema with all properties
        """
        if self._database_schema is None:
            try:
                database = self.client.databases.retrieve(database_id=self.database_id)
                self._database_schema = database
                logger.info("Retrieved database schema successfully")
                return database
            except Exception as e:
                logger.error(f"Failed to retrieve database schema: {e}")
                raise
        return self._database_schema

    def analyze_schema(self) -> Dict[str, str]:
        """
        Analyze the current database schema and return property types.

        Returns:
            Dictionary mapping property names to their types
        """
        schema = self.client.databases.retrieve(database_id=self.database_id)
        properties = schema.get("properties", {})

        property_map = {}
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            property_map[prop_name] = prop_type

        logger.info(f"Database properties: {property_map}")
        return property_map

    def get_recommended_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Get recommended database schema for optimal job tracking.

        Returns:
            Recommended property schema
        """
        return {
            "Job Title": {"type": "title"},
            "Company": {"type": "rich_text"},
            "Location": {"type": "rich_text"},
            "Status": {
                "type": "select",
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Submitted", "color": "yellow"},
                    {"name": "Interview", "color": "purple"},
                    {"name": "Rejected", "color": "red"},
                    {"name": "Accepted", "color": "green"},
                    {"name": "Withdrawn", "color": "default"}
                ]
            },
            "Application URL": {"type": "url"},
            "LinkedIn URL": {"type": "url"},
            "Applied Date": {"type": "date"},
            "Match Score": {"type": "number"},
            "Salary Range": {"type": "rich_text"},
            "Job Type": {"type": "rich_text"},
            "Work Location": {
                "type": "select",
                "options": [
                    {"name": "Remote", "color": "green"},
                    {"name": "Hybrid", "color": "blue"},
                    {"name": "On-site", "color": "orange"}
                ]
            },
            "Notes": {"type": "rich_text"},
            "Contact Email": {"type": "email"},
            "Contact Name": {"type": "rich_text"},
            "Follow Up Date": {"type": "date"},
            "Skills Required": {"type": "multi_select"},
            "Experience Level": {"type": "select"},
        }

    def add_job(self, application: ApplicationData) -> str:
        """
        Add a job application to Notion database.

        Args:
            application: ApplicationData object

        Returns:
            Page ID of created entry
        """
        job = application.job

        # Build properties based on available fields
        properties = self._build_properties(application)

        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            page_id = response["id"]
            logger.info(f"Created Notion page for {job.title} at {job.company.name}: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            raise

    def update_job(self, page_id: str, application: ApplicationData) -> None:
        """
        Update an existing job application entry.

        Args:
            page_id: Notion page ID
            application: Updated ApplicationData
        """
        properties = self._build_properties(application)

        try:
            self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            logger.info(f"Updated Notion page {page_id}")

        except Exception as e:
            logger.error(f"Failed to update Notion page: {e}")
            raise

    def _build_properties(self, application: ApplicationData) -> Dict[str, Any]:
        """
        Build Notion properties dictionary from ApplicationData.

        Args:
            application: ApplicationData object

        Returns:
            Properties dictionary for Notion API
        """
        job = application.job
        properties = {}

        # Map to flexible property names (handles variations in database schema)
        property_mappings = {
            "Job Title": ("title", [{"text": {"content": job.title}}]),
            "Company": ("rich_text", [{"text": {"content": job.company.name}}]),
            "Location": ("rich_text", [{"text": {"content": job.location}}]),
            "Status": ("select", {"name": self._map_status(application.status)}),
            "Application URL": ("url", str(job.application_url)),
            "LinkedIn URL": ("url", str(job.linkedin_url) if job.linkedin_url else None),
            "Salary Range": ("rich_text", [{"text": {"content": job.salary_range or ""}}]),
            "Job Type": ("rich_text", [{"text": {"content": job.job_type.value if job.job_type else ""}}]),
            "Notes": ("rich_text", [{"text": {"content": application.notes or ""}}]),
        }

        # Optional fields
        if application.applied_date:
            property_mappings["Applied Date"] = ("date", {"start": application.applied_date.isoformat()})

        if application.match_score is not None:
            property_mappings["Match Score"] = ("number", application.match_score)

        if job.work_location:
            property_mappings["Work Location"] = ("select", {"name": job.work_location.value.replace("_", "-").title()})

        if application.contact_email:
            property_mappings["Contact Email"] = ("email", application.contact_email)

        if application.contact_name:
            property_mappings["Contact Name"] = ("rich_text", [{"text": {"content": application.contact_name}}])

        if application.follow_up_date:
            property_mappings["Follow Up Date"] = ("date", {"start": application.follow_up_date.isoformat()})

        if job.skills_required:
            property_mappings["Skills Required"] = (
                "multi_select",
                [{"name": skill} for skill in job.skills_required[:10]]  # Limit to 10 skills
            )

        if job.experience_level:
            property_mappings["Experience Level"] = ("select", {"name": job.experience_level})

        # Build final properties dict
        for prop_name, (prop_type, value) in property_mappings.items():
            if value is not None and value != "" and value != []:
                properties[prop_name] = {prop_type: value}

        return properties

    def _map_status(self, status: ApplicationStatus) -> str:
        """Map ApplicationStatus enum to Notion select values."""
        status_map = {
            ApplicationStatus.NOT_STARTED: "Not Started",
            ApplicationStatus.IN_PROGRESS: "In Progress",
            ApplicationStatus.SUBMITTED: "Submitted",
            ApplicationStatus.INTERVIEW: "Interview",
            ApplicationStatus.REJECTED: "Rejected",
            ApplicationStatus.ACCEPTED: "Accepted",
            ApplicationStatus.WITHDRAWN: "Withdrawn",
        }
        return status_map.get(status, "Not Started")

    def query_jobs(
        self,
        status: Optional[ApplicationStatus] = None,
        company: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query jobs from Notion database with filters.

        Args:
            status: Filter by application status
            company: Filter by company name
            limit: Maximum number of results

        Returns:
            List of job entries
        """
        filters = []

        if status:
            filters.append({
                "property": "Status",
                "select": {"equals": self._map_status(status)}
            })

        if company:
            filters.append({
                "property": "Company",
                "rich_text": {"contains": company}
            })

        query_params = {
            "database_id": self.database_id,
            "page_size": limit
        }

        if filters:
            query_params["filter"] = {
                "and": filters
            } if len(filters) > 1 else filters[0]

        try:
            response = self.client.databases.query(**query_params)
            return response.get("results", [])

        except Exception as e:
            logger.error(f"Failed to query Notion database: {e}")
            raise

    def get_job_by_url(self, application_url: str) -> Optional[Dict[str, Any]]:
        """
        Find a job entry by application URL to avoid duplicates.

        Args:
            application_url: Job application URL

        Returns:
            Notion page if found, None otherwise
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Application URL",
                    "url": {"equals": application_url}
                }
            )
            results = response.get("results", [])
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Failed to search for job by URL: {e}")
            return None

    def add_or_update_job(self, application: ApplicationData) -> str:
        """
        Add a new job or update existing one (prevents duplicates).

        Args:
            application: ApplicationData object

        Returns:
            Page ID of created or updated entry
        """
        existing = self.get_job_by_url(str(application.job.application_url))

        if existing:
            page_id = existing["id"]
            logger.info(f"Job already exists, updating: {page_id}")
            self.update_job(page_id, application)
            return page_id
        else:
            return self.add_job(application)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get application statistics from Notion database.

        Returns:
            Statistics dictionary with counts by status
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                page_size=100
            )

            results = response.get("results", [])
            stats = {
                "total": len(results),
                "by_status": {},
                "this_week": 0,
                "this_month": 0
            }

            now = datetime.now()

            for page in results:
                # Count by status
                status_prop = page.get("properties", {}).get("Status", {})
                status = status_prop.get("select", {}).get("name", "Unknown")
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

                # Count by date
                date_prop = page.get("properties", {}).get("Applied Date", {})
                date_value = date_prop.get("date", {})
                if date_value and date_value.get("start"):
                    applied_date = datetime.fromisoformat(date_value["start"].replace("Z", "+00:00"))
                    days_ago = (now - applied_date).days

                    if days_ago <= 7:
                        stats["this_week"] += 1
                    if days_ago <= 30:
                        stats["this_month"] += 1

            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise


# Convenience function for quick usage
def create_notion_tracker() -> NotionJobTracker:
    """Create a NotionJobTracker instance with settings from config."""
    return NotionJobTracker()
