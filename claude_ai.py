"""
Claude AI integration for job matching and cover letter generation.
Uses Anthropic's Claude API for intelligent job analysis and content creation.
"""

import logging
from typing import List, Optional, Dict, Any
from anthropic import Anthropic

from models import (
    JobListing,
    UserProfile,
    JobMatchAnalysis,
    CoverLetterRequest,
    CoverLetterResponse
)
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeJobAssistant:
    """AI assistant for job search using Claude."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude AI client.

        Args:
            api_key: Anthropic API key (uses config if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)

    def analyze_job_match(
        self,
        job: JobListing,
        user_profile: UserProfile
    ) -> JobMatchAnalysis:
        """
        Analyze how well a job matches the user's profile using Claude AI.

        Args:
            job: Job listing to analyze
            user_profile: User's profile and preferences

        Returns:
            JobMatchAnalysis with detailed insights
        """
        # Build the analysis prompt
        prompt = self._build_match_analysis_prompt(job, user_profile)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            analysis_text = response.content[0].text
            analysis = self._parse_match_analysis(analysis_text, job.job_id)

            logger.info(f"Analyzed job match for {job.title} at {job.company.name}: {analysis.match_score}%")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing job match: {e}")
            raise

    def _build_match_analysis_prompt(
        self,
        job: JobListing,
        user_profile: UserProfile
    ) -> str:
        """Build the prompt for job match analysis."""
        return f"""You are a career advisor helping someone evaluate a job opportunity. Analyze how well this job matches their profile.

JOB DETAILS:
Title: {job.title}
Company: {job.company.name}
Location: {job.location}
Type: {job.job_type.value if job.job_type else 'Not specified'}
Work Location: {job.work_location.value if job.work_location else 'Not specified'}

Job Description:
{job.description[:2000]}

Required Skills: {', '.join(job.skills_required) if job.skills_required else 'Not specified'}

USER PROFILE:
Name: {user_profile.full_name}
Skills: {', '.join(user_profile.skills) if user_profile.skills else 'Not specified'}
Desired Job Titles: {', '.join(user_profile.desired_titles) if user_profile.desired_titles else 'Not specified'}
Desired Locations: {', '.join(user_profile.desired_locations) if user_profile.desired_locations else 'Any'}
Remote Preference: {user_profile.remote_preference.value if user_profile.remote_preference else 'Not specified'}

Professional Summary:
{user_profile.summary or 'Not provided'}

Please analyze this job match and provide your response in the following format:

MATCH_SCORE: [0-100]
RECOMMENDATION: [Apply/Maybe/Skip]

MATCHING_SKILLS:
- [skill 1]
- [skill 2]
...

MISSING_SKILLS:
- [skill 1]
- [skill 2]
...

PROS:
- [pro 1]
- [pro 2]
...

CONS:
- [con 1]
- [con 2]
...

REASONING:
[2-3 sentences explaining your recommendation]

Be honest and specific in your analysis. Focus on genuine match quality."""

    def _parse_match_analysis(self, analysis_text: str, job_id: str) -> JobMatchAnalysis:
        """Parse Claude's analysis response into a JobMatchAnalysis object."""
        lines = analysis_text.strip().split('\n')

        match_score = 50.0  # Default
        recommendation = "Maybe"
        matching_skills = []
        missing_skills = []
        pros = []
        cons = []
        reasoning = ""

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("MATCH_SCORE:"):
                try:
                    match_score = float(line.split(":")[-1].strip())
                except:
                    pass

            elif line.startswith("RECOMMENDATION:"):
                recommendation = line.split(":")[-1].strip()

            elif line == "MATCHING_SKILLS:":
                current_section = "matching_skills"
            elif line == "MISSING_SKILLS:":
                current_section = "missing_skills"
            elif line == "PROS:":
                current_section = "pros"
            elif line == "CONS:":
                current_section = "cons"
            elif line == "REASONING:":
                current_section = "reasoning"

            elif line.startswith("-") and current_section:
                item = line[1:].strip()
                if current_section == "matching_skills":
                    matching_skills.append(item)
                elif current_section == "missing_skills":
                    missing_skills.append(item)
                elif current_section == "pros":
                    pros.append(item)
                elif current_section == "cons":
                    cons.append(item)

            elif current_section == "reasoning" and line:
                reasoning += line + " "

        return JobMatchAnalysis(
            job_id=job_id,
            match_score=match_score,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            pros=pros,
            cons=cons,
            recommendation=recommendation,
            reasoning=reasoning.strip()
        )

    def generate_cover_letter(
        self,
        job: JobListing,
        user_profile: UserProfile,
        additional_context: Optional[str] = None,
        tone: str = "professional"
    ) -> CoverLetterResponse:
        """
        Generate a personalized cover letter using Claude AI.

        Args:
            job: Job listing
            user_profile: User's profile
            additional_context: Additional context or specific points to highlight
            tone: Tone of the letter (professional, enthusiastic, etc.)

        Returns:
            CoverLetterResponse with generated letter
        """
        # Build the prompt
        prompt = self._build_cover_letter_prompt(job, user_profile, additional_context, tone)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            letter_text = response.content[0].text
            cover_letter_response = self._parse_cover_letter(letter_text)

            logger.info(f"Generated cover letter for {job.title} at {job.company.name}")
            return cover_letter_response

        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            raise

    def _build_cover_letter_prompt(
        self,
        job: JobListing,
        user_profile: UserProfile,
        additional_context: Optional[str],
        tone: str
    ) -> str:
        """Build the prompt for cover letter generation."""
        context_section = f"\nAdditional Context:\n{additional_context}" if additional_context else ""

        return f"""You are a professional career coach helping someone write a compelling cover letter. Generate a personalized, genuine cover letter.

JOB DETAILS:
Title: {job.title}
Company: {job.company.name}
Location: {job.location}

Job Description:
{job.description[:2000]}

USER PROFILE:
Name: {user_profile.full_name}
Email: {user_profile.email}
Phone: {user_profile.phone}

Skills: {', '.join(user_profile.skills) if user_profile.skills else 'Not specified'}

Professional Summary:
{user_profile.summary or 'Not provided'}

{context_section}

Tone: {tone}

Please generate a cover letter with the following structure:

KEY_POINTS:
- [3-5 key points that will be highlighted in the letter]

COVER_LETTER:
[The complete cover letter text - should be 3-4 paragraphs, professional, specific to this role, and genuine. Include:
- Opening paragraph expressing interest
- 2-3 paragraphs highlighting relevant experience and skills
- Closing paragraph with call to action]

CUSTOMIZATION_NOTES:
[Any specific customizations or personal touches added]

Keep it concise (300-400 words), genuine, and tailored to this specific role. Avoid generic phrases."""

    def _parse_cover_letter(self, letter_text: str) -> CoverLetterResponse:
        """Parse Claude's cover letter response."""
        sections = letter_text.split("COVER_LETTER:")

        key_points = []
        cover_letter = ""
        customization_notes = ""

        # Extract key points
        if "KEY_POINTS:" in letter_text:
            key_points_section = letter_text.split("KEY_POINTS:")[1].split("COVER_LETTER:")[0]
            for line in key_points_section.split('\n'):
                line = line.strip()
                if line.startswith("-"):
                    key_points.append(line[1:].strip())

        # Extract cover letter
        if len(sections) > 1:
            letter_section = sections[1].split("CUSTOMIZATION_NOTES:")[0]
            cover_letter = letter_section.strip()

        # Extract customization notes
        if "CUSTOMIZATION_NOTES:" in letter_text:
            customization_notes = letter_text.split("CUSTOMIZATION_NOTES:")[1].strip()

        return CoverLetterResponse(
            cover_letter=cover_letter,
            key_points=key_points,
            customization_notes=customization_notes if customization_notes else None
        )

    def batch_analyze_jobs(
        self,
        jobs: List[JobListing],
        user_profile: UserProfile
    ) -> List[JobMatchAnalysis]:
        """
        Analyze multiple jobs in batch.

        Args:
            jobs: List of jobs to analyze
            user_profile: User's profile

        Returns:
            List of JobMatchAnalysis results
        """
        analyses = []

        for i, job in enumerate(jobs, 1):
            logger.info(f"Analyzing job {i}/{len(jobs)}: {job.title}")
            try:
                analysis = self.analyze_job_match(job, user_profile)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze job {job.job_id}: {e}")
                continue

        # Sort by match score
        analyses.sort(key=lambda x: x.match_score, reverse=True)

        return analyses


def create_claude_assistant() -> ClaudeJobAssistant:
    """Create a ClaudeJobAssistant instance with settings from config."""
    return ClaudeJobAssistant()
