"""
Pydantic models for LinkedIn Job Application Agent.
Defines data structures for jobs, applications, companies, and user profiles.
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    """Status of a job application."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class JobType(str, Enum):
    """Type of job employment."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class WorkLocation(str, Enum):
    """Work location type."""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"


class Company(BaseModel):
    """Company information."""
    name: str = Field(..., description="Company name")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    linkedin_url: Optional[HttpUrl] = Field(None, description="Company LinkedIn page")
    industry: Optional[str] = Field(None, description="Company industry")
    size: Optional[str] = Field(None, description="Company size")
    description: Optional[str] = Field(None, description="Company description")
    location: Optional[str] = Field(None, description="Company headquarters location")


class JobListing(BaseModel):
    """Job listing information from LinkedIn."""
    job_id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job title")
    company: Company = Field(..., description="Company information")
    location: str = Field(..., description="Job location")
    work_location: Optional[WorkLocation] = Field(None, description="Remote/Hybrid/On-site")
    job_type: Optional[JobType] = Field(None, description="Employment type")
    description: str = Field(..., description="Job description")
    requirements: Optional[List[str]] = Field(default_factory=list, description="Job requirements")
    responsibilities: Optional[List[str]] = Field(default_factory=list, description="Job responsibilities")
    salary_range: Optional[str] = Field(None, description="Salary range if available")
    posted_date: Optional[datetime] = Field(None, description="When the job was posted")
    application_url: HttpUrl = Field(..., description="URL to apply for the job")
    linkedin_url: Optional[HttpUrl] = Field(None, description="LinkedIn job posting URL")
    easy_apply: bool = Field(default=False, description="Whether job has Easy Apply")

    # Extracted metadata
    skills_required: Optional[List[str]] = Field(default_factory=list, description="Required skills")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    applicant_count: Optional[int] = Field(None, description="Number of applicants")


class ApplicationData(BaseModel):
    """Data for a job application."""
    job: JobListing = Field(..., description="Job being applied to")
    status: ApplicationStatus = Field(default=ApplicationStatus.NOT_STARTED, description="Application status")
    applied_date: Optional[datetime] = Field(None, description="When application was submitted")
    cover_letter: Optional[str] = Field(None, description="Generated cover letter")
    resume_used: Optional[str] = Field(None, description="Resume version used")
    notes: Optional[str] = Field(None, description="Application notes")
    match_score: Optional[float] = Field(None, ge=0, le=100, description="Job match score (0-100)")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID for tracking")

    # Communication tracking
    contact_email: Optional[EmailStr] = Field(None, description="Hiring manager or recruiter email")
    contact_name: Optional[str] = Field(None, description="Contact person name")
    follow_up_date: Optional[datetime] = Field(None, description="Date to follow up")


class UserProfile(BaseModel):
    """User profile information for job applications."""
    full_name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    linkedin_url: HttpUrl = Field(..., description="LinkedIn profile URL")

    # Resume information
    summary: Optional[str] = Field(None, description="Professional summary")
    skills: List[str] = Field(default_factory=list, description="Skills list")
    experience: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Work experience")
    education: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Education history")
    certifications: Optional[List[str]] = Field(default_factory=list, description="Certifications")

    # Preferences
    desired_titles: List[str] = Field(default_factory=list, description="Desired job titles")
    desired_locations: List[str] = Field(default_factory=list, description="Preferred locations")
    desired_salary_min: Optional[int] = Field(None, description="Minimum desired salary")
    remote_preference: Optional[WorkLocation] = Field(None, description="Remote work preference")


class NotionJobEntry(BaseModel):
    """Structure for Notion database entry."""
    page_id: Optional[str] = Field(None, description="Notion page ID")
    job_title: str = Field(..., description="Job title")
    company_name: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    status: ApplicationStatus = Field(..., description="Application status")
    application_url: str = Field(..., description="Application URL")
    applied_date: Optional[str] = Field(None, description="Date applied (YYYY-MM-DD)")
    match_score: Optional[float] = Field(None, description="Match score")
    notes: Optional[str] = Field(None, description="Additional notes")
    salary_range: Optional[str] = Field(None, description="Salary range")
    job_type: Optional[str] = Field(None, description="Job type")
    work_location: Optional[str] = Field(None, description="Work location type")


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter."""
    job: JobListing = Field(..., description="Job listing")
    user_profile: UserProfile = Field(..., description="User profile")
    additional_context: Optional[str] = Field(None, description="Additional context for cover letter")
    tone: str = Field(default="professional", description="Tone of the cover letter")


class CoverLetterResponse(BaseModel):
    """Generated cover letter response."""
    cover_letter: str = Field(..., description="Generated cover letter text")
    key_points: List[str] = Field(..., description="Key points highlighted in the letter")
    customization_notes: Optional[str] = Field(None, description="Notes on customizations made")


class JobMatchAnalysis(BaseModel):
    """Analysis of how well a job matches user profile."""
    job_id: str = Field(..., description="Job identifier")
    match_score: float = Field(..., ge=0, le=100, description="Match score (0-100)")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match")
    missing_skills: List[str] = Field(default_factory=list, description="Skills that are missing")
    pros: List[str] = Field(default_factory=list, description="Pros of this position")
    cons: List[str] = Field(default_factory=list, description="Cons of this position")
    recommendation: str = Field(..., description="Apply/Skip/Maybe recommendation")
    reasoning: str = Field(..., description="Reasoning for recommendation")
