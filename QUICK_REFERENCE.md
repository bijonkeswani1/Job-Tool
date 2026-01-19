# Quick Reference Card

Copy and paste these commands. Replace the parts in quotes with your own values.

---

## 🔍 Finding Jobs

### Basic job search
```bash
python scrape_jobs.py "Software Engineer" -l "San Francisco, CA" -n 25
```

### Find remote jobs
```bash
python scrape_jobs.py "Python Developer" --remote -n 50
```

### Find Easy Apply jobs (faster to apply!)
```bash
python scrape_jobs.py "Data Analyst" --easy-apply -n 30
```

### Preview jobs without saving to Notion
```bash
python scrape_jobs.py "Product Manager" -l "New York, NY" --no-notion
```

### Combine filters (remote + Easy Apply)
```bash
python scrape_jobs.py "Marketing Manager" --remote --easy-apply -n 40
```

---

## 🤖 Using AI to Analyze Jobs

### Analyze all your Not Started jobs
```bash
python analyze_jobs.py analyze -n 10
```

### Analyze more jobs
```bash
python analyze_jobs.py analyze -n 50
```

### Analyze only "Not Started" jobs
```bash
python analyze_jobs.py analyze -s "Not Started" -n 20
```

---

## ✍️ Generating Cover Letters

### Generate cover letter for a specific job
```bash
python analyze_jobs.py cover-letter "Software Engineer" "Google"
```

**Important:** Replace "Software Engineer" with the job title and "Google" with the company name EXACTLY as they appear in your Notion database.

---

## 📊 Checking Your Database

### See your Notion database stats and structure
```bash
python inspect_notion.py
```

This shows:
- How many jobs you have
- Jobs applied this week/month
- Breakdown by status
- Your database structure

---

## 🛠️ Setup & Testing

### Install everything (first time only)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install browser for scraping
playwright install
```

### Test your Notion connection
```bash
python inspect_notion.py
```

---

## 🎯 Common Workflows

### Morning Job Search Routine
```bash
# 1. Find new jobs (customize keywords for your search)
python scrape_jobs.py "Your Job Title" -l "Your Location" --remote -n 50

# 2. Analyze them with AI
python analyze_jobs.py analyze -n 50

# 3. Check your Notion database - apply to the high-match jobs!
```

### Applying to a Specific Job
```bash
# 1. Generate cover letter
python analyze_jobs.py cover-letter "Job Title" "Company Name"

# 2. Copy the cover letter and customize it

# 3. Apply through LinkedIn

# 4. Update status in Notion to "Applied"
```

---

## 💡 Command Options Explained

### For scrape_jobs.py:
- `"Job Title"` - What job you're looking for (REQUIRED)
- `-l "Location"` - Where (optional, leave out for any location)
- `-n 25` - How many jobs to find (default: 25, max recommended: 100)
- `--remote` - Only remote jobs
- `--easy-apply` - Only jobs with Easy Apply button
- `--no-notion` - Don't save to Notion (just preview)
- `--no-match` - Skip AI match score calculation

### For analyze_jobs.py:
- `analyze` - Analyze jobs command
  - `-n 10` - How many jobs to analyze
  - `-s "Not Started"` - Filter by status

- `cover-letter` - Generate cover letter command
  - First argument: Job title (must match Notion)
  - Second argument: Company name (must match Notion)

---

## 🚨 Troubleshooting Quick Fixes

### "Command not found" or "No such file"
**Fix:** Make sure you're in the Job-Tool directory
```bash
cd /path/to/Job-Tool
```

### "ModuleNotFoundError"
**Fix:** Activate virtual environment
```bash
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### "API key error"
**Fix:** Check your `.env` file has the correct API keys

### LinkedIn wants verification
**Fix:** Wait a few hours, then try with smaller batches (-n 25)

---

## 📝 Job Search Keywords Examples

Customize these for your search:

**Software Engineering:**
- "Senior Frontend Engineer"
- "Python Backend Developer"
- "Full Stack JavaScript Developer"
- "DevOps Engineer"
- "Machine Learning Engineer"

**Data & Analytics:**
- "Data Scientist"
- "Business Intelligence Analyst"
- "Data Engineer"
- "Analytics Manager"

**Product & Design:**
- "Product Manager"
- "UX Designer"
- "Product Designer"
- "UI/UX Researcher"

**Marketing & Sales:**
- "Digital Marketing Manager"
- "Content Marketing Specialist"
- "Sales Development Representative"
- "Growth Marketing Manager"

**Other:**
- "Project Manager"
- "Operations Manager"
- "Customer Success Manager"
- "Technical Writer"

---

## 🎓 Pro Tips

1. **Be specific with job titles** - "Senior Python Developer" gets better matches than just "Developer"

2. **Use --remote and --easy-apply together** - Finds the easiest jobs to apply to quickly

3. **Analyze before applying** - Let the AI help you focus on the best matches

4. **Start your search with -n 25** - Test it out before doing larger batches

5. **Run searches daily** - New jobs are posted all the time

6. **Keep Notion updated** - Mark jobs as Applied, Interview, etc.

---

## 📞 Need Help?

1. Read the error message carefully - it usually tells you what's wrong
2. Check `GETTING_STARTED.md` for detailed setup instructions
3. Make sure your `.env` file has all the correct API keys
4. Try `python inspect_notion.py` to test your setup

---

**Save this file for quick reference!** 📌
