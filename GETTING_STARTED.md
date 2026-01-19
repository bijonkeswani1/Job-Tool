# Getting Started - Simple Guide

**Welcome!** This guide will help you set up and use the LinkedIn Job Application Agent, even if you've never coded before.

## What Does This Tool Do?

This tool helps you:
1. **Find jobs** on LinkedIn automatically
2. **Save them** to your Notion database for tracking
3. **Analyze** which jobs are the best match for you using AI
4. **Generate** personalized cover letters automatically

Think of it as your personal job search assistant!

---

## Before You Start

You'll need accounts for:
- **Notion** (free) - Where your jobs will be tracked
- **Anthropic** (has free tier) - Powers the AI features
- **GitHub** (free) - Where this code lives
- **LinkedIn** - For job searching (you already have this!)

Don't worry, we'll go through each one step by step.

---

## Step 1: Set Up Notion (15 minutes)

### 1.1 Create a Notion Account
1. Go to https://www.notion.so
2. Click "Get Notion free"
3. Sign up with your email
4. Complete the setup

### 1.2: You Already Have a Job Tracker!
You mentioned you have a tracker at: `https://www.notion.so/Job-Tracker-202507e7851880edae31e75807984ffe`

Great! We'll use that one. Just make sure it has these columns (properties):
- Job Title
- Company
- Location
- Status (with options: Not Started, In Progress, Submitted, Interview, Rejected, Accepted)
- Application URL
- Applied Date
- Match Score (number)
- Notes

### 1.3: Create a Notion Integration
This lets the tool talk to your Notion database.

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Name it: **"LinkedIn Job Agent"**
4. Select your workspace
5. Click **"Submit"**
6. **IMPORTANT:** Copy the "Internal Integration Token" - it starts with `secret_`
7. Save this somewhere safe (you'll need it soon!)

### 1.4: Share Your Database with the Integration
1. Open your Job Tracker page in Notion
2. Click the **"..."** menu at the top right
3. Scroll down and click **"+ Add connections"**
4. Select **"LinkedIn Job Agent"** (the integration you just created)
5. Click **"Confirm"**

✅ Notion is now ready!

---

## Step 2: Get an Anthropic API Key (5 minutes)

This powers the AI that analyzes jobs and writes cover letters.

1. Go to https://console.anthropic.com
2. Click **"Sign Up"** or **"Sign In"**
3. After signing in, click your name in the top right
4. Click **"API Keys"**
5. Click **"Create Key"**
6. Give it a name like "Job Agent"
7. **Copy the key** - it starts with `sk-ant-`
8. Save this somewhere safe!

**Note:** Anthropic offers free credits for new users. Check their pricing page for current rates.

---

## Step 3: Set Up the Tool on Your Computer (20 minutes)

### 3.1: Check if You Have Python

**On Mac:**
1. Open **Terminal** (search for it in Spotlight)
2. Type: `python3 --version`
3. Press Enter

**On Windows:**
1. Open **Command Prompt** (search for "cmd")
2. Type: `python --version`
3. Press Enter

**What to look for:**
- If you see "Python 3.9" or higher → You're good!
- If you see an error → You need to install Python

**To install Python:**
- Go to https://www.python.org/downloads/
- Download the latest version (3.11 or 3.12)
- Run the installer
- **IMPORTANT on Windows:** Check the box "Add Python to PATH"
- Click through the installation

### 3.2: Download This Project

**Option A: If you have Git:**
```bash
git clone <your-repo-url>
cd Job-Tool
```

**Option B: Without Git:**
1. Go to the GitHub page for this project
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the file to your Documents folder
5. Remember where you put it!

### 3.3: Open Terminal/Command Prompt in the Project Folder

**On Mac:**
1. Open Terminal
2. Type `cd ` (with a space after cd)
3. Drag the Job-Tool folder into the Terminal window
4. Press Enter

**On Windows:**
1. Open the Job-Tool folder in File Explorer
2. Right-click in the folder (not on a file)
3. Choose **"Open in Terminal"** or **"Open Command Prompt here"**

### 3.4: Install the Tool

Copy and paste these commands one at a time:

```bash
# Create a virtual environment (keeps things organized)
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install all the requirements
pip install -r requirements.txt

# Install the browser for LinkedIn scraping
playwright install
```

**What you'll see:**
- Lots of text scrolling by
- Some download progress bars
- Eventually it will finish and show your command prompt again

---

## Step 4: Configure Your API Keys (5 minutes)

### 4.1: Create Your Configuration File

1. In the Job-Tool folder, you'll see a file called `.env.example`
2. Make a copy of it and name it `.env` (just `.env`, no `.example`)

**On Mac/Linux:**
```bash
cp .env.example .env
```

**On Windows:**
Right-click `.env.example` → Copy → Paste → Rename to `.env`

### 4.2: Edit the .env File

Open `.env` in a text editor (Notepad on Windows, TextEdit on Mac).

Replace the placeholder values:

```env
# Your API keys (the ones you saved earlier!)
ANTHROPIC_API_KEY=sk-ant-PASTE_YOUR_KEY_HERE
NOTION_API_KEY=secret_PASTE_YOUR_KEY_HERE
NOTION_DATABASE_ID=202507e7851880edae31e75807984ffe

# Your personal info
FULL_NAME=Your Full Name
EMAIL=your.email@example.com
PHONE=+1-555-555-5555
LINKEDIN_URL=https://linkedin.com/in/yourprofile

# Optional: LinkedIn login (helps find more jobs)
LINKEDIN_EMAIL=your.linkedin.email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# Settings
MAX_APPLICATIONS_PER_DAY=50
AUTO_SUBMIT=false
```

**IMPORTANT:**
- Replace ALL the placeholder values with your real information
- Don't add extra spaces
- Don't use quotes around the values
- Save the file when done

---

## Step 5: Test That Everything Works (5 minutes)

Run this command to test your Notion connection:

```bash
python inspect_notion.py
```

**What you should see:**
- A message saying "Connected to Notion API"
- A table showing your database properties
- Statistics about your applications

**If you see an error:**
- Double-check your API keys in the `.env` file
- Make sure you shared your Notion database with the integration
- Make sure your database ID is correct

---

## How to Use the Tool

Now that everything is set up, here's how to actually use it!

### Use Case 1: Find Jobs and Save to Notion

This finds jobs on LinkedIn and automatically adds them to your Notion tracker.

```bash
python scrape_jobs.py "Software Engineer" -l "San Francisco, CA" -n 25
```

**What this does:**
- Searches LinkedIn for "Software Engineer" jobs in San Francisco
- Finds up to 25 jobs
- Extracts all the job details
- Saves them to your Notion database

**Customize it:**
```bash
# Find remote Python jobs
python scrape_jobs.py "Python Developer" --remote -n 50

# Find Easy Apply jobs (faster to apply!)
python scrape_jobs.py "Data Analyst" --easy-apply -n 30

# Just preview without saving to Notion
python scrape_jobs.py "Product Manager" --no-notion
```

**Options:**
- `-l "Location"` = Where the job is
- `-n 25` = How many jobs to find (max)
- `--remote` = Only remote jobs
- `--easy-apply` = Only jobs with Easy Apply
- `--no-notion` = Don't save to Notion (just show results)

### Use Case 2: Analyze Your Jobs with AI

This uses Claude AI to tell you which jobs are the best match for you.

```bash
python analyze_jobs.py analyze -n 10
```

**What this does:**
- Looks at the jobs in your Notion database
- Uses AI to analyze how well each job matches your profile
- Gives you a score (0-100%) for each job
- Tells you: "Apply", "Maybe", or "Skip"
- Shows pros and cons for each job

**What you'll see:**
- A table with all your jobs ranked by match score
- Detailed analysis for the top 3 matches
- Specific reasons why each job is or isn't a good fit

### Use Case 3: Generate a Cover Letter

This creates a personalized cover letter for a specific job.

```bash
python analyze_jobs.py cover-letter "Software Engineer" "Google"
```

**What this does:**
- Finds the job in your Notion database (matching the title and company)
- Uses AI to write a customized cover letter
- Shows you the letter with key points highlighted

**Copy the letter and customize it further before submitting!**

---

## Common Commands Cheat Sheet

Save this for quick reference:

```bash
# 1. Find jobs
python scrape_jobs.py "Job Title" -l "Location" -n 25

# 2. Find remote jobs only
python scrape_jobs.py "Job Title" --remote -n 50

# 3. Analyze all your saved jobs
python analyze_jobs.py analyze -n 10

# 4. Generate a cover letter
python analyze_jobs.py cover-letter "Job Title" "Company Name"

# 5. Check your Notion database stats
python inspect_notion.py
```

---

## Tips for Success

### 1. Start Small
- Try finding just 10-25 jobs first
- Make sure they're saving to Notion correctly
- Then scale up to more jobs

### 2. Be Specific with Keywords
- Instead of "Engineer", use "Senior Frontend Engineer"
- Instead of "Developer", use "Python Backend Developer"
- More specific = better results

### 3. Use the AI Analysis
- Don't apply to everything!
- Focus on the high-match jobs (80%+)
- Read the AI's reasoning - it's usually spot-on

### 4. Customize Generated Cover Letters
- The AI creates a great starting point
- Add your personal touch
- Mention specific projects or experiences

### 5. Keep Your Notion Updated
- Mark jobs as "Applied" after you apply
- Add notes about interview dates
- Track your progress!

---

## Troubleshooting

### "ModuleNotFoundError"
**Fix:** Make sure you're in the virtual environment.
```bash
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Then run your command again.

### "API key error" or "Authentication failed"
**Fix:** Check your `.env` file
- Make sure the keys are correct
- No extra spaces
- No quotes around the values

### "Could not find job in Notion"
**Fix:** The job needs to exist in your Notion database first.
1. Run `python scrape_jobs.py` first to add jobs
2. Then use `analyze_jobs.py`

### "Playwright errors"
**Fix:** Install the browsers:
```bash
playwright install
```

### LinkedIn asks for verification/captcha
**Fix:** This is normal if you scrape too much.
- Wait a few hours
- Use smaller batches (25 jobs max)
- Add your LinkedIn email/password to `.env`

---

## Getting Help

### If something doesn't work:

1. **Check the error message** - It usually tells you what's wrong
2. **Re-read the setup steps** - Did you miss anything?
3. **Check your `.env` file** - Are all the keys correct?
4. **Try the simple test first** - Run `python inspect_notion.py`

### Provide feedback:

Since you're testing this, please note:
- What worked well?
- What was confusing?
- What errors did you encounter?
- What features would you like to add?

---

## Next Steps

Once you're comfortable with the basics:

1. **Customize your profile** - Edit the user profile in `analyze_jobs.py` to match your actual skills and experience
2. **Set up automated scraping** - Run the scraper daily to find new jobs
3. **Track your applications** - Use Notion to manage your entire job search
4. **Iterate on cover letters** - Use the AI as a starting point, then personalize

---

## Quick Start Checklist

Use this to make sure you've done everything:

- [ ] Created Notion account and job tracker
- [ ] Created Notion integration and got API key
- [ ] Shared Notion database with integration
- [ ] Got Anthropic API key
- [ ] Installed Python 3.9+
- [ ] Downloaded the project
- [ ] Installed requirements (`pip install -r requirements.txt`)
- [ ] Installed Playwright browsers (`playwright install`)
- [ ] Created and configured `.env` file
- [ ] Tested with `python inspect_notion.py`
- [ ] Ran first job search successfully
- [ ] Checked that jobs appeared in Notion

---

**You're all set!** 🎉

Start with finding some jobs, then try the AI analysis. Good luck with your job search!