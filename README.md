# Job-Hunting AI Agent

File-driven job-hunting assistant that reads job posters, resumes, and a knowledge base to generate analysis reports, tailored resume suggestions, interview questions, and application reminders.

## Features
- Reads input files from structured folders (jobs, resumes, KB).
- Job analysis, skill-gap report, and tailored resume suggestions.
- Interview questions derived from job keywords and KB notes.
- Application tracker dashboard and reminder generation.
- Reminder urgency labels (today, tomorrow, this week, overdue).
- Cover letter draft generation.

## Expected Folder Structure
```
job-hunting-agent/
|-- README.md
|-- app.py
|-- requirements.txt
|-- reflection.md
|-- input_jobs/
|-- input_resumes/
|-- input_kb/
|-- outputs/
|-- tracker/
|-- samples/
```

## Setup
```
pip install -r requirements.txt
```

## Run
```
python app.py
```

If multiple job posters or resumes exist, the script prompts you to pick one.

## Inputs
- input_jobs/ : job posters or job descriptions (.txt or .pdf)
- input_resumes/ : resume text (.txt or .pdf)
- input_kb/ : course slides notes or interview prep notes (.txt or .pdf)

## Outputs (generated in outputs/)
- job_analysis_report.txt
- skill_gap_report.txt
- tailored_resume_suggestions.txt
- interview_questions.txt
- preparation_plan.txt
- cover_letter.txt
- final_agent_report.txt

## Tracker
The tracker/applications.csv file stores application status. It is used to generate:
- reminders.txt (interview and follow-up reminders)
- Application status dashboard inside final_agent_report.txt

## Notes
- PDF support uses pypdf (listed in requirements.txt).
- Sample inputs are provided in input_* and samples/ folders.
