#!/bin/bash
# Simple script to run a job search
# Usage: ./run_job_search.sh

echo "======================================"
echo "LinkedIn Job Search"
echo "======================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Prompt for job search details
echo "What job title are you looking for?"
read -p "Job Title: " job_title

echo ""
echo "Where? (Leave blank for 'Any location')"
read -p "Location: " location

echo ""
echo "How many jobs? (Default: 25)"
read -p "Number of jobs: " num_jobs
num_jobs=${num_jobs:-25}

echo ""
echo "Remote jobs only? (y/n)"
read -p "Remote: " remote

echo ""
echo "Easy Apply only? (y/n)"
read -p "Easy Apply: " easy_apply

# Build command
cmd="python scrape_jobs.py \"$job_title\""

if [ -n "$location" ]; then
    cmd="$cmd -l \"$location\""
fi

cmd="$cmd -n $num_jobs"

if [ "$remote" = "y" ] || [ "$remote" = "Y" ]; then
    cmd="$cmd --remote"
fi

if [ "$easy_apply" = "y" ] || [ "$easy_apply" = "Y" ]; then
    cmd="$cmd --easy-apply"
fi

echo ""
echo "======================================"
echo "Running search..."
echo "======================================"
echo ""

# Run the command
eval $cmd

echo ""
echo "======================================"
echo "Search complete!"
echo "Check your Notion database for results"
echo "======================================"
