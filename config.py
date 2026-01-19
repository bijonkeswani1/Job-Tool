"""
Configuration management for LinkedIn Job Application Agent.
Uses Pydantic Settings for type-safe configuration from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, HttpUrl
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")
    notion_api_key: str = Field(..., description="Notion API key")
    hunter_io_api_key: Optional[str] = Field(None, description="Hunter.io API key for email discovery")

    # Notion Configuration
    notion_database_id: str = Field(..., description="Notion database ID for job tracking")

    # Personal Details
    full_name: str = Field(..., description="Full name for job applications")
    email: str = Field(..., description="Email address for job applications")
    phone: str = Field(..., description="Phone number for job applications")
    linkedin_url: HttpUrl = Field(..., description="LinkedIn profile URL")

    # Optional: LinkedIn Credentials
    linkedin_email: Optional[str] = Field(None, description="LinkedIn login email")
    linkedin_password: Optional[str] = Field(None, description="LinkedIn login password")

    # Application Settings
    max_applications_per_day: int = Field(default=50, description="Maximum applications per day")
    auto_submit: bool = Field(default=False, description="Automatically submit applications")

    # Server Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")

    def get_personal_info(self) -> dict:
        """Get personal information as a dictionary."""
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": str(self.linkedin_url)
        }


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    This ensures we only load the .env file once.
    """
    global settings
    if settings is None:
        settings = Settings()
    return settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    Useful for testing or when .env file changes.
    """
    global settings
    settings = Settings()
    return settings
