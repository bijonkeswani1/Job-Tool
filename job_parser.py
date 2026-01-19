"""
Job parsing utilities for extracting structured data from job descriptions.
Uses regex and NLP techniques to extract requirements, skills, and metadata.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta


class JobParser:
    """Parser for extracting structured information from job descriptions."""

    # Common skill keywords to look for
    TECH_SKILLS = [
        # Programming Languages
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Ruby", "Go", "Rust",
        "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",

        # Web Technologies
        "React", "Vue.js", "Angular", "Node.js", "Express", "Django", "Flask", "FastAPI",
        "Spring", "ASP.NET", "HTML", "CSS", "SASS", "Tailwind",

        # Databases
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "DynamoDB", "Cassandra",
        "Oracle", "SQLite", "Elasticsearch",

        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins",
        "CI/CD", "Git", "GitHub", "GitLab", "CircleCI",

        # Data & ML
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
        "Pandas", "NumPy", "Data Science", "NLP", "Computer Vision", "AI",

        # Other
        "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "JIRA",
        "Linux", "Unix", "Bash", "PowerShell",
    ]

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """
        Extract technical skills mentioned in the text.

        Args:
            text: Job description or requirements text

        Returns:
            List of identified skills
        """
        found_skills = []
        text_lower = text.lower()

        for skill in JobParser.TECH_SKILLS:
            # Case-insensitive search
            if skill.lower() in text_lower:
                if skill not in found_skills:
                    found_skills.append(skill)

        return found_skills

    @staticmethod
    def extract_years_of_experience(text: str) -> Optional[int]:
        """
        Extract years of experience requirement.

        Args:
            text: Job description text

        Returns:
            Number of years or None
        """
        # Patterns like "5+ years", "3-5 years", "at least 2 years"
        patterns = [
            r'(\d+)\+?\s*(?:to|\-)\s*\d+\s*years?',  # "3-5 years"
            r'(\d+)\+\s*years?',  # "5+ years"
            r'at least (\d+)\s*years?',  # "at least 3 years"
            r'minimum (\d+)\s*years?',  # "minimum 2 years"
            r'(\d+)\s*years?\s*(?:of)?\s*experience',  # "3 years experience"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    @staticmethod
    def extract_salary_range(text: str) -> Optional[str]:
        """
        Extract salary range from text.

        Args:
            text: Job description text

        Returns:
            Salary range string or None
        """
        # Patterns like "$100,000 - $150,000", "$100k-150k", "100-150k"
        patterns = [
            r'\$[\d,]+\s*(?:to|\-)\s*\$[\d,]+',  # "$100,000 - $150,000"
            r'\$\d+k\s*(?:to|\-)\s*\$?\d+k',  # "$100k-150k"
            r'\d+k\s*(?:to|\-)\s*\d+k',  # "100k-150k"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    @staticmethod
    def extract_requirements(text: str) -> List[str]:
        """
        Extract job requirements from description.

        Args:
            text: Job description text

        Returns:
            List of requirements
        """
        requirements = []

        # Look for "Requirements" or "Qualifications" section
        req_pattern = r'(?:requirements|qualifications|required skills|what we\'re looking for)[:\s]*(.+?)(?:responsibilities|what you\'ll do|about|$)'
        match = re.search(req_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            req_text = match.group(1)

            # Split by bullet points or newlines
            items = re.split(r'[•\*\-\n]', req_text)

            for item in items:
                item = item.strip()
                if item and len(item) > 10 and len(item) < 200:
                    requirements.append(item)

        return requirements[:10]  # Limit to 10 requirements

    @staticmethod
    def extract_responsibilities(text: str) -> List[str]:
        """
        Extract job responsibilities from description.

        Args:
            text: Job description text

        Returns:
            List of responsibilities
        """
        responsibilities = []

        # Look for "Responsibilities" section
        resp_pattern = r'(?:responsibilities|what you\'ll do|you will)[:\s]*(.+?)(?:requirements|qualifications|about|$)'
        match = re.search(resp_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            resp_text = match.group(1)

            # Split by bullet points or newlines
            items = re.split(r'[•\*\-\n]', resp_text)

            for item in items:
                item = item.strip()
                if item and len(item) > 10 and len(item) < 200:
                    responsibilities.append(item)

        return responsibilities[:10]  # Limit to 10 responsibilities

    @staticmethod
    def extract_education(text: str) -> Optional[str]:
        """
        Extract education requirements.

        Args:
            text: Job description text

        Returns:
            Education requirement or None
        """
        education_keywords = [
            r"Bachelor'?s?\s+(?:degree|Degree)",
            r"Master'?s?\s+(?:degree|Degree)",
            r"PhD",
            r"Ph\.D\.",
            r"Doctorate",
        ]

        for keyword in education_keywords:
            match = re.search(keyword, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    @staticmethod
    def parse_posted_date(date_text: str) -> Optional[datetime]:
        """
        Parse relative date strings like "2 days ago", "1 week ago".

        Args:
            date_text: Date string from LinkedIn

        Returns:
            datetime object or None
        """
        now = datetime.now()

        # Patterns
        if "just now" in date_text.lower() or "today" in date_text.lower():
            return now

        if "yesterday" in date_text.lower():
            return now - timedelta(days=1)

        # Match "X days/weeks/months ago"
        match = re.search(r'(\d+)\s+(day|week|month)s?\s+ago', date_text, re.IGNORECASE)
        if match:
            amount = int(match.group(1))
            unit = match.group(2).lower()

            if unit == "day":
                return now - timedelta(days=amount)
            elif unit == "week":
                return now - timedelta(weeks=amount)
            elif unit == "month":
                return now - timedelta(days=amount * 30)

        return None

    @staticmethod
    def extract_company_size(text: str) -> Optional[str]:
        """
        Extract company size from text.

        Args:
            text: Text containing company info

        Returns:
            Company size string or None
        """
        patterns = [
            r'\d+\s*(?:to|\-)\s*\d+\s*employees?',
            r'\d+\+\s*employees?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    @staticmethod
    def calculate_match_score(
        job_skills: List[str],
        user_skills: List[str],
        job_description: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate how well a job matches the user's profile.

        Args:
            job_skills: Skills required for the job
            user_skills: User's skills
            job_description: Job description text
            user_profile: Optional user profile data

        Returns:
            Match score from 0-100
        """
        score = 0.0

        # Skills match (40 points)
        if job_skills and user_skills:
            job_skills_lower = [s.lower() for s in job_skills]
            user_skills_lower = [s.lower() for s in user_skills]

            matching_skills = set(job_skills_lower) & set(user_skills_lower)
            if job_skills_lower:
                skills_score = (len(matching_skills) / len(job_skills_lower)) * 40
                score += min(skills_score, 40)

        # Experience match (30 points)
        required_years = JobParser.extract_years_of_experience(job_description)
        if required_years and user_profile and "years_experience" in user_profile:
            user_years = user_profile["years_experience"]
            if user_years >= required_years:
                score += 30
            elif user_years >= required_years * 0.7:  # Within 70% of requirement
                score += 20

        # Education match (15 points)
        required_education = JobParser.extract_education(job_description)
        if required_education and user_profile and "education" in user_profile:
            if required_education.lower() in user_profile["education"].lower():
                score += 15

        # Keywords in description (15 points)
        if user_profile and "keywords" in user_profile:
            keywords = user_profile["keywords"]
            desc_lower = job_description.lower()
            keyword_matches = sum(1 for kw in keywords if kw.lower() in desc_lower)
            if keywords:
                score += (keyword_matches / len(keywords)) * 15

        return min(score, 100.0)  # Cap at 100

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)]', '', text)

        return text.strip()
