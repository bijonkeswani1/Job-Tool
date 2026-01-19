# LinkedIn Job Application Agent

An intelligent automation agent that helps you discover, analyze, and apply to jobs on LinkedIn. Uses Claude AI for smart job matching, cover letter generation, and application tracking through Notion.

## Features

- **Job Discovery**: Scrape and discover jobs from LinkedIn
- **Smart Matching**: AI-powered job matching based on your profile and preferences
- **Cover Letter Generation**: Automatically generate tailored cover letters using Claude AI
- **Notion Integration**: Track all applications in a Notion database
- **Email Discovery**: Find recruiter/hiring manager emails using Hunter.io
- **Application Automation**: Streamline the application process with intelligent automation

## Project Structure

```
linkedin-job-agent/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variable template
├── .env                       # Your actual environment variables (create this)
├── .gitignore                 # Git ignore rules
├── config.py                  # Configuration management
├── models.py                  # Pydantic data models
├── notion_client.py           # Notion API integration
├── linkedin_scraper.py        # LinkedIn job scraper with Playwright
├── job_parser.py              # Job description parsing utilities
├── scrape_jobs.py             # CLI tool for scraping jobs
├── inspect_notion.py          # Notion database inspector utility
├── example_notion_usage.py    # Usage examples for Notion integration
└── [Additional modules to be created]
```

## Prerequisites

- Python 3.9 or higher
- Anthropic API key (for Claude AI)
- Notion account and API key
- Hunter.io API key (optional, for email discovery)
- LinkedIn account

## Setup Instructions

### 1. Clone or Create Repository

If you haven't already:
```bash
git clone <your-repo-url>
cd Job-Tool
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

Playwright requires browser binaries:
```bash
playwright install
```

### 5. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and fill in your actual values:

```env
# API Keys
ANTHROPIC_API_KEY=your_actual_anthropic_api_key
NOTION_API_KEY=your_actual_notion_api_key
HUNTER_IO_API_KEY=your_actual_hunter_io_api_key  # Optional

# Notion Configuration
NOTION_DATABASE_ID=your_notion_database_id

# Personal Details
FULL_NAME=Your Full Name
EMAIL=your.email@example.com
PHONE=+1-234-567-8900
LINKEDIN_URL=https://linkedin.com/in/yourprofile

# Application Settings
MAX_APPLICATIONS_PER_DAY=50
AUTO_SUBMIT=false
```

### 6. Set Up Notion Database

Create a Notion database with the following properties:

- **Job Title** (Title)
- **Company** (Text)
- **Location** (Text)
- **Status** (Select: Not Started, In Progress, Submitted, Interview, Rejected, Accepted, Withdrawn)
- **Application URL** (URL)
- **Applied Date** (Date)
- **Match Score** (Number)
- **Salary Range** (Text)
- **Job Type** (Text)
- **Work Location** (Select: Remote, Hybrid, On-site)
- **Notes** (Text)

Get your database ID from the URL:
```
https://www.notion.so/your-workspace/DATABASE_ID?v=...
```

### 7. Get API Keys

#### Anthropic API Key
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

#### Notion API Key
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name and select your workspace
4. Copy the "Internal Integration Token"
5. Share your database with the integration

#### Hunter.io API Key (Optional)
1. Go to [Hunter.io](https://hunter.io/)
2. Sign up for a free account
3. Go to API section in your dashboard
4. Copy your API key

### 8. Test Your Notion Integration

After setting up your API keys, inspect your Notion database:

```bash
python inspect_notion.py
```

This will:
- Connect to your Notion database
- Show your current database schema
- Display application statistics
- Recommend any missing properties for full functionality
- Verify your integration is working correctly

You can also try the example usage:

```bash
python example_notion_usage.py
```

This demonstrates how to:
- Add jobs to your Notion database
- Query existing applications
- Get statistics
- Update application status

## Usage

### Scraping LinkedIn Jobs

The `scrape_jobs.py` CLI tool makes it easy to discover jobs and save them to Notion:

#### Basic Job Search

```bash
# Search for jobs and save to Notion
python scrape_jobs.py "Software Engineer" -l "San Francisco, CA" -n 25

# Search for remote jobs only
python scrape_jobs.py "Python Developer" --remote -n 50

# Search for Easy Apply jobs only
python scrape_jobs.py "Data Scientist" --easy-apply -n 30

# Just scrape without saving to Notion (preview mode)
python scrape_jobs.py "Machine Learning Engineer" --no-notion
```

#### CLI Options

```bash
python scrape_jobs.py <keywords> [options]

Arguments:
  keywords              Job search keywords (e.g., "Software Engineer")

Options:
  -l, --location       Job location (e.g., "San Francisco, CA")
  -n, --limit          Maximum number of jobs to scrape (default: 25)
  -e, --easy-apply     Filter for Easy Apply jobs only
  -r, --remote         Filter for remote jobs only
  --no-notion          Don't save to Notion (just display results)
  --no-match           Don't calculate match scores
```

#### Examples

```bash
# Find remote Python jobs
python scrape_jobs.py "Python Backend Developer" --remote -n 50

# Find Easy Apply data science jobs in NYC
python scrape_jobs.py "Data Scientist" -l "New York, NY" --easy-apply -n 30

# Find machine learning jobs (no location filter)
python scrape_jobs.py "Machine Learning Engineer" -n 100

# Preview jobs without saving to Notion
python scrape_jobs.py "Full Stack Developer" -l "Seattle, WA" --no-notion
```

### Programmatic Usage

You can also use the scraper programmatically in Python:

```python
import asyncio
from linkedin_scraper import scrape_linkedin_jobs
from notion_client import create_notion_tracker
from models import ApplicationData, ApplicationStatus

async def main():
    # Scrape jobs
    jobs = await scrape_linkedin_jobs(
        keywords="Software Engineer",
        location="San Francisco, CA",
        limit=25,
        remote=True,
        easy_apply=True
    )

    # Save to Notion
    tracker = create_notion_tracker()
    for job in jobs:
        application = ApplicationData(
            job=job,
            status=ApplicationStatus.NOT_STARTED
        )
        tracker.add_or_update_job(application)

asyncio.run(main())
```

### Basic Workflow

1. **Configure your environment** - Set up `.env` with API keys
2. **Test Notion integration** - Run `python inspect_notion.py`
3. **Scrape jobs** - Use `scrape_jobs.py` to discover positions
4. **Review in Notion** - Check your database for new jobs
5. **Apply to jobs** - Use the tracked URLs to apply
6. **Update status** - Mark jobs as Applied, Interview, etc. in Notion

## Configuration Options

See `config.py` for all available configuration options. Key settings:

- `max_applications_per_day`: Limit daily applications
- `auto_submit`: Enable/disable automatic submission
- `api_host` and `api_port`: API server configuration

## Data Models

The project uses Pydantic for type-safe data validation. See `models.py` for:

- `JobListing`: Job information from LinkedIn
- `ApplicationData`: Application tracking data
- `UserProfile`: Your profile and preferences
- `CoverLetterRequest/Response`: Cover letter generation
- `JobMatchAnalysis`: AI job matching analysis

## Development

### Adding New Features

1. Create new modules in the project root
2. Import models from `models.py`
3. Use `get_settings()` from `config.py` for configuration
4. Follow existing patterns for consistency

### Testing

```bash
# Run tests (when available)
pytest

# Type checking
mypy .

# Linting
ruff check .
```

## Security & Legal Notes

- **Never commit your `.env` file** - Contains sensitive API keys and credentials
- **Keep API keys secure** - Rotate regularly and use environment variables
- **LinkedIn Terms of Service** - Be respectful of LinkedIn's ToS when scraping:
  - Use reasonable rate limiting (built-in delays in scraper)
  - Don't scrape excessively (recommend max 100 jobs per session)
  - Consider using LinkedIn's official API for production use
  - This tool is for personal job search automation only
- **Review before auto-submit** - Always review applications before enabling automatic submission
- **Data Privacy** - Job data is stored in your personal Notion database
- **Authentication** - LinkedIn credentials are optional but enable access to more features

## Important Notes on LinkedIn Scraping

The LinkedIn scraper uses Playwright to automate browser interactions. Please note:

- **Rate Limiting**: The scraper includes delays to avoid overwhelming LinkedIn's servers
- **Authentication**: LinkedIn login is optional but may be required for some job listings
- **Browser Mode**: Runs in headless mode by default (no GUI) for efficiency
- **Captchas**: May encounter verification challenges if scraping too aggressively
- **Session Management**: Maintains browser session during scraping
- **Duplicate Prevention**: Automatically checks Notion to avoid re-adding existing jobs

**Best Practices:**
1. Start with small batches (25-50 jobs) to test
2. Use specific search keywords to get relevant results
3. Add delays between large scraping sessions
4. Monitor LinkedIn account for any security warnings

## Roadmap

- [x] Notion integration (✓ Complete)
- [x] LinkedIn job scraping (✓ Complete)
- [x] Job parsing & skill extraction (✓ Complete)
- [ ] Claude AI integration for job matching
- [ ] Cover letter generation with Claude
- [ ] Email discovery with Hunter.io
- [ ] Web UI dashboard
- [ ] Application analytics
- [ ] Interview scheduling assistant
- [ ] Resume tailoring for specific jobs

## Troubleshooting

### Common Issues

**ModuleNotFoundError**: Make sure virtual environment is activated and dependencies are installed

**Playwright errors**: Run `playwright install` to install browser binaries

**API key errors**: Verify all keys in `.env` are correct and active

**Notion errors**: Ensure integration is added to your database

## Contributing

This is a personal project but feel free to fork and customize for your needs.

## License

MIT License - Feel free to use and modify as needed.
