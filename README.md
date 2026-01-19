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

### Running the Application

```bash
# Start the API server
uvicorn main:app --reload

# Or run specific modules
python agent.py
```

### Basic Workflow

1. **Configure your profile** in `.env`
2. **Set up your Notion database** for tracking
3. **Run the job discovery** to find relevant positions
4. **Review AI-generated match scores** and recommendations
5. **Generate cover letters** for high-match jobs
6. **Track applications** automatically in Notion

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

## Security Notes

- Never commit your `.env` file
- Keep API keys secure and rotate regularly
- Review auto-submit applications before enabling
- Be mindful of LinkedIn's terms of service

## Roadmap

- [ ] Job scraping module (LinkedIn automation)
- [ ] Claude AI integration for job matching
- [ ] Cover letter generation
- [x] Notion integration (✓ Complete)
- [ ] Email discovery with Hunter.io
- [ ] Web UI dashboard
- [ ] Application analytics
- [ ] Interview scheduling assistant

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
