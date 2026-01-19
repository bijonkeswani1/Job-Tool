"""
LinkedIn job scraper using Playwright.
Handles job discovery, search, and data extraction from LinkedIn.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import re

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup

from models import JobListing, Company, JobType, WorkLocation
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Scraper for LinkedIn job listings."""

    def __init__(self, headless: bool = True):
        """
        Initialize LinkedIn scraper.

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the browser and create a new page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await self.context.new_page()
        logger.info("Browser started successfully")

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

    async def login(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Login to LinkedIn.

        Args:
            email: LinkedIn email (uses config if not provided)
            password: LinkedIn password (uses config if not provided)
        """
        settings = get_settings()
        email = email or settings.linkedin_email
        password = password or settings.linkedin_password

        if not email or not password:
            logger.warning("LinkedIn credentials not provided. Some features may be limited.")
            return

        try:
            logger.info("Logging into LinkedIn...")
            await self.page.goto("https://www.linkedin.com/login", wait_until="networkidle")

            # Fill in credentials
            await self.page.fill('input[name="session_key"]', email)
            await self.page.fill('input[name="session_password"]', password)

            # Click sign in
            await self.page.click('button[type="submit"]')

            # Wait for navigation
            await self.page.wait_for_load_state("networkidle")

            # Check if login was successful
            current_url = self.page.url
            if "feed" in current_url or "checkpoint" in current_url:
                self.is_authenticated = True
                logger.info("Successfully logged into LinkedIn")

                # Handle potential verification
                if "checkpoint" in current_url:
                    logger.warning("LinkedIn verification required. Please complete it manually.")
                    await asyncio.sleep(30)  # Wait for manual verification
            else:
                logger.error("Login may have failed. Check credentials.")

        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        job_type: Optional[List[str]] = None,
        remote: bool = False,
        easy_apply: bool = False,
        experience_level: Optional[List[str]] = None,
        posted_within_days: int = 7,
        limit: int = 25
    ) -> List[JobListing]:
        """
        Search for jobs on LinkedIn.

        Args:
            keywords: Job search keywords (e.g., "Software Engineer")
            location: Location (e.g., "San Francisco, CA")
            job_type: List of job types (Full-time, Part-time, Contract, etc.)
            remote: Filter for remote jobs only
            easy_apply: Filter for Easy Apply jobs only
            experience_level: Experience levels (Internship, Entry level, Associate, Mid-Senior level, Director, Executive)
            posted_within_days: Only show jobs posted within N days
            limit: Maximum number of jobs to scrape

        Returns:
            List of JobListing objects
        """
        # Build search URL
        search_params = {
            "keywords": keywords,
            "location": location,
            "f_TPR": f"r{posted_within_days * 86400}",  # Time posted (in seconds)
        }

        if easy_apply:
            search_params["f_AL"] = "true"  # Easy Apply filter

        if remote:
            search_params["f_WT"] = "2"  # Remote work type

        if job_type:
            # Map job types to LinkedIn filters
            job_type_map = {
                "Full-time": "F",
                "Part-time": "P",
                "Contract": "C",
                "Temporary": "T",
                "Internship": "I",
            }
            type_filters = [job_type_map.get(jt, "") for jt in job_type if jt in job_type_map]
            if type_filters:
                search_params["f_JT"] = ",".join(type_filters)

        if experience_level:
            # Map experience levels to LinkedIn filters
            level_map = {
                "Internship": "1",
                "Entry level": "2",
                "Associate": "3",
                "Mid-Senior level": "4",
                "Director": "5",
                "Executive": "6",
            }
            level_filters = [level_map.get(lvl, "") for lvl in experience_level if lvl in level_map]
            if level_filters:
                search_params["f_E"] = ",".join(level_filters)

        search_url = f"https://www.linkedin.com/jobs/search/?{urlencode(search_params)}"

        logger.info(f"Searching jobs: {keywords} in {location or 'any location'}")
        logger.info(f"Search URL: {search_url}")

        await self.page.goto(search_url, wait_until="networkidle")
        await asyncio.sleep(2)  # Let page fully load

        jobs = []
        job_count = 0

        try:
            # Scroll to load more jobs
            for _ in range(5):  # Scroll multiple times to load more
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

            # Get job cards
            job_cards = await self.page.query_selector_all(".job-card-container, .jobs-search-results__list-item")
            logger.info(f"Found {len(job_cards)} job cards")

            for card in job_cards[:limit]:
                if job_count >= limit:
                    break

                try:
                    job = await self._extract_job_from_card(card)
                    if job:
                        jobs.append(job)
                        job_count += 1
                        logger.info(f"Scraped job {job_count}/{limit}: {job.title} at {job.company.name}")

                except Exception as e:
                    logger.warning(f"Error extracting job: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error during job search: {e}")

        logger.info(f"Successfully scraped {len(jobs)} jobs")
        return jobs

    async def _extract_job_from_card(self, card) -> Optional[JobListing]:
        """
        Extract job information from a job card element.

        Args:
            card: Playwright element representing a job card

        Returns:
            JobListing object or None if extraction fails
        """
        try:
            # Click on the card to load details
            await card.click()
            await asyncio.sleep(1)  # Wait for details to load

            # Get job details from the right panel
            html = await self.page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Extract basic info
            title_elem = soup.select_one(".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

            company_elem = soup.select_one(".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name")
            company_name = company_elem.get_text(strip=True) if company_elem else "Unknown Company"

            location_elem = soup.select_one(".job-details-jobs-unified-top-card__bullet, .jobs-unified-top-card__bullet")
            location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"

            # Extract job description
            description_elem = soup.select_one(".jobs-description-content__text, .jobs-box__html-content")
            description = description_elem.get_text(strip=True) if description_elem else ""

            # Extract application URL
            apply_button = soup.select_one("a.jobs-apply-button, button.jobs-apply-button")
            job_url = self.page.url

            # Check if Easy Apply
            easy_apply = bool(soup.select_one(".jobs-apply-button--easy-apply"))

            # Extract job metadata
            criteria = soup.select(".jobs-unified-top-card__job-insight")
            job_type = None
            work_location = None
            experience_level = None

            for criterion in criteria:
                text = criterion.get_text(strip=True).lower()
                if "full-time" in text:
                    job_type = JobType.FULL_TIME
                elif "part-time" in text:
                    job_type = JobType.PART_TIME
                elif "contract" in text:
                    job_type = JobType.CONTRACT
                elif "internship" in text:
                    job_type = JobType.INTERNSHIP

                if "remote" in text:
                    work_location = WorkLocation.REMOTE
                elif "hybrid" in text:
                    work_location = WorkLocation.HYBRID
                elif "on-site" in text or "on site" in text:
                    work_location = WorkLocation.ON_SITE

            # Extract skills (if available)
            skills = []
            skill_elems = soup.select(".job-details-skill-match-status-list__skill")
            for skill_elem in skill_elems:
                skill_text = skill_elem.get_text(strip=True)
                if skill_text:
                    skills.append(skill_text)

            # Create Company object
            company = Company(
                name=company_name,
                location=location
            )

            # Generate job ID from URL
            job_id = self._extract_job_id_from_url(job_url)

            # Create JobListing object
            job_listing = JobListing(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                work_location=work_location,
                job_type=job_type,
                description=description[:5000],  # Limit description length
                application_url=job_url,
                linkedin_url=job_url,
                easy_apply=easy_apply,
                skills_required=skills,
                experience_level=experience_level,
                posted_date=datetime.now()  # LinkedIn doesn't always show exact dates
            )

            return job_listing

        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return None

    def _extract_job_id_from_url(self, url: str) -> str:
        """Extract job ID from LinkedIn job URL."""
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            return f"linkedin-{match.group(1)}"
        return f"linkedin-{hash(url)}"

    async def get_job_details(self, job_url: str) -> Optional[JobListing]:
        """
        Get detailed information about a specific job.

        Args:
            job_url: LinkedIn job URL

        Returns:
            JobListing object or None
        """
        try:
            await self.page.goto(job_url, wait_until="networkidle")
            await asyncio.sleep(2)

            # Use the same extraction logic
            html = await self.page.content()
            soup = BeautifulSoup(html, "html.parser")

            # This would use similar extraction logic as _extract_job_from_card
            # Simplified for now
            logger.info(f"Fetched job details from {job_url}")

            return None  # Implement full extraction if needed

        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None


async def scrape_linkedin_jobs(
    keywords: str,
    location: str = "",
    limit: int = 25,
    **kwargs
) -> List[JobListing]:
    """
    Convenience function to scrape LinkedIn jobs.

    Args:
        keywords: Job search keywords
        location: Job location
        limit: Maximum number of jobs
        **kwargs: Additional search parameters

    Returns:
        List of JobListing objects
    """
    async with LinkedInScraper(headless=True) as scraper:
        # Optionally login
        settings = get_settings()
        if settings.linkedin_email and settings.linkedin_password:
            await scraper.login()

        jobs = await scraper.search_jobs(
            keywords=keywords,
            location=location,
            limit=limit,
            **kwargs
        )

        return jobs
