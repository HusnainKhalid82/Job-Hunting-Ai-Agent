"""File-driven job-hunting agent."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
JOB_DIR = BASE_DIR / "input_jobs"
RESUME_DIR = BASE_DIR / "input_resumes"
KB_DIR = BASE_DIR / "input_kb"
OUTPUT_DIR = BASE_DIR / "outputs"
TRACKER_DIR = BASE_DIR / "tracker"
SAMPLES_DIR = BASE_DIR / "samples"

TRACKER_HEADERS = [
    "application_id",
    "company",
    "role",
    "source",
    "status",
    "applied_date",
    "interview_date",
    "follow_up_date",
    "next_action",
    "notes",
]

KEYWORDS = [
    "python",
    "machine learning",
    "data preprocessing",
    "feature engineering",
    "pandas",
    "numpy",
    "scikit-learn",
    "sql",
    "communication",
    "problem solving",
    "git",
    "github",
    "api",
    "rest",
    "flask",
    "streamlit",
    "nlp",
    "deep learning",
    "dashboard",
    "visualization",
    "jupyter",
]

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "using",
    "role",
    "company",
    "location",
    "responsibilities",
    "requirements",
    "skills",
    "intern",
    "internship",
}


def ensure_folders() -> None:
    for folder in [JOB_DIR, RESUME_DIR, KB_DIR, OUTPUT_DIR, TRACKER_DIR, SAMPLES_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def list_input_files(folder: Path) -> List[Path]:
    allowed = {".txt", ".pdf"}
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in allowed])


def select_file(files: List[Path], label: str) -> Optional[Path]:
    if not files:
        return None
    if len(files) == 1:
        return files[0]

    print(f"\n{label} files:")
    for idx, path in enumerate(files, start=1):
        print(f"  {idx}. {path.name}")

    if not sys.stdin.isatty():
        return files[0]

    try:
        choice = input("Select a file number (press Enter for 1): ").strip()
    except EOFError:
        return files[0]

    if not choice:
        return files[0]

    try:
        index = int(choice) - 1
    except ValueError:
        return files[0]

    if 0 <= index < len(files):
        return files[index]

    return files[0]


def read_file_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception:
            print("PDF support requires pypdf. Install it with: pip install pypdf")
            return ""

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)

    return ""


def read_combined_text(paths: List[Path]) -> Tuple[str, int]:
    combined = ""
    count = 0
    for path in paths:
        text = read_file_text(path)
        if text.strip():
            combined += f"\n\n--- FILE: {path.name} ---\n"
            combined += text
            count += 1
    return combined.strip(), count


def extract_label_value(text: str, label: str) -> str:
    pattern = rf"^{re.escape(label)}\s*:\s*(.+)$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    found = [kw for kw in KEYWORDS if kw in text_lower]

    tokens = re.findall(r"[a-z][a-z0-9+.#-]+", text_lower)
    counts = Counter(token for token in tokens if token not in STOPWORDS)
    for token, _ in counts.most_common(15):
        if token not in found:
            found.append(token)

    return found


def extract_top_terms(text: str, limit: int = 8) -> List[str]:
    tokens = re.findall(r"[a-z][a-z0-9+.#-]+", text.lower())
    counts: Dict[str, int] = {}
    for token in tokens:
        if token in STOPWORDS:
            continue
        counts[token] = counts.get(token, 0) + 1
    top_terms = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [term for term, _ in top_terms[:limit]]


def compare_skills(job_skills: List[str], resume_skills: List[str]) -> Tuple[List[str], List[str], float]:
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]
    score = 0.0 if not job_skills else round((len(matched) / len(job_skills)) * 100, 2)
    return matched, missing, score


def generate_job_analysis(job_text: str, job_skills: List[str], top_terms: List[str]) -> str:
    company = extract_label_value(job_text, "Company")
    role = extract_label_value(job_text, "Role")

    report = "Job Analysis Report\n===================\n\n"
    if company or role:
        report += f"Company: {company or 'Unknown'}\n"
        report += f"Role: {role or 'Unknown'}\n\n"

    report += "Skills/keywords found in job posters:\n"
    for skill in job_skills:
        report += f"- {skill}\n"

    if top_terms:
        report += "\nTop terms from job text:\n"
        for term in top_terms:
            report += f"- {term}\n"

    return report


def generate_skill_gap_report(
    job_skills: List[str],
    resume_skills: List[str],
    matched: List[str],
    missing: List[str],
    score: float,
) -> str:
    report = "Skill Gap Report\n================\n\n"
    report += f"Match Score: {score}%\n\n"
    report += "Matched Skills:\n"
    for skill in matched:
        report += f"- {skill}\n"
    report += "\nMissing Skills:\n"
    for skill in missing:
        report += f"- {skill}\n"

    report += "\nResume Keywords Found:\n"
    for skill in resume_skills:
        report += f"- {skill}\n"

    return report


def generate_resume_suggestions(job_skills: List[str], missing: List[str]) -> str:
    output = "Tailored Resume Suggestions\n===========================\n\n"
    output += "Suggested improvements according to job posters:\n"
    for skill in job_skills:
        output += f"- Add or improve resume evidence related to {skill}.\n"

    output += "\nSuggested resume bullets:\n"
    output += "- Built Python projects with clear documentation and results.\n"
    output += "- Used Git and GitHub for version control and collaboration.\n"
    output += "- Applied problem solving to complete data and ML tasks.\n"

    if missing:
        output += "\nSkills to improve before applying/interview:\n"
        for skill in missing:
            output += f"- {skill}\n"
    else:
        output += "\nGreat job. No major skill gaps found based on keywords.\n"

    return output


def generate_interview_questions(job_skills: List[str], kb_text: str) -> str:
    questions = "Interview Questions\n===================\n\n"
    questions += "Technical questions based on job posters:\n"
    for skill in job_skills:
        questions += f"- Explain your understanding of {skill}.\n"
        questions += f"- How have you used {skill} in a project or course activity?\n"

    questions += "\nHR and behavioral questions:\n"
    questions += "- Tell me about yourself.\n"
    questions += "- Why are you interested in this role?\n"
    questions += "- Describe your best academic or project work.\n"
    questions += "- What are your strengths and weaknesses?\n"
    questions += "- Why should we select you?\n"

    questions += "\nQuestions inspired by KB/slides:\n"
    kb_lines = [line.strip("- ").strip() for line in kb_text.splitlines() if line.strip()]
    for line in kb_lines[:10]:
        questions += f"- How would you explain this point in an interview: {line}?\n"

    return questions


def create_or_update_tracker() -> Path:
    path = TRACKER_DIR / "applications.csv"
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(TRACKER_HEADERS)
            writer.writerow(
                [
                    "APP-001",
                    "Sample Company",
                    "AI Intern",
                    "Job Poster",
                    "Not Applied",
                    "",
                    "",
                    "",
                    "Tailor resume and apply",
                    "Sample row",
                ]
            )
    return path


def load_applications() -> List[Dict[str, str]]:
    tracker_path = TRACKER_DIR / "applications.csv"
    if not tracker_path.exists():
        return []
    with tracker_path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def classify_urgency(target_date: Optional[date], today: date) -> str:
    # Lightweight urgency tiers for reminders.
    if not target_date:
        return ""
    if target_date < today:
        return "OVERDUE"
    if target_date == today:
        return "TODAY"
    if target_date == today + timedelta(days=1):
        return "TOMORROW"
    if target_date <= today + timedelta(days=7):
        return "THIS WEEK"
    return "UPCOMING"


def generate_reminders(rows: List[Dict[str, str]]) -> str:
    reminders = "Application Reminders\n=====================\n\n"
    today = date.today()

    for row in rows:
        app_id = row.get("application_id", "")
        company = row.get("company", "")
        role = row.get("role", "")
        status = row.get("status", "").lower()
        interview_date = row.get("interview_date", "")
        follow_up_date = row.get("follow_up_date", "")
        next_action = row.get("next_action", "")

        interview_day = parse_date(interview_date)
        follow_up_day = parse_date(follow_up_date)

        if status == "interview scheduled":
            urgency = classify_urgency(interview_day, today)
            tag = f" [{urgency}]" if urgency else ""
            reminders += (
                f"- {app_id}: Interview scheduled for {role} at {company} on {interview_date}.{tag} "
                f"Next action: {next_action}\n"
            )

        if follow_up_day:
            urgency = classify_urgency(follow_up_day, today)
            tag = f" [{urgency}]" if urgency else ""
            reminders += (
                f"- {app_id}: Follow up on {follow_up_date} for {role} at {company}.{tag}\n"
            )

        if status == "not applied":
            reminders += (
                f"- {app_id}: Not applied yet for {role} at {company}. Tailor resume and apply.\n"
            )

        if status == "applied" and not follow_up_day:
            reminders += (
                f"- {app_id}: Application submitted to {company}. Set a follow-up date if no response.\n"
            )

    return reminders


def generate_status_dashboard(rows: List[Dict[str, str]]) -> str:
    counts: Dict[str, int] = {}
    for row in rows:
        status = row.get("status", "Unknown").strip() or "Unknown"
        counts[status] = counts.get(status, 0) + 1

    output = "Application Status Dashboard\n============================\n\n"
    if not counts:
        return output + "No applications recorded.\n"

    for status, count in sorted(counts.items(), key=lambda item: item[0].lower()):
        output += f"- {status}: {count}\n"
    return output


def generate_preparation_plan(missing: List[str], kb_text: str, rows: List[Dict[str, str]]) -> str:
    plan = "Preparation Plan\n================\n\n"

    plan += "Focus areas based on missing skills:\n"
    if missing:
        for skill in missing[:5]:
            plan += f"- Review and practice: {skill}\n"
    else:
        plan += "- No missing skills detected. Strengthen existing projects.\n"

    plan += "\nQuick KB reminders:\n"
    kb_lines = [line.strip("- ").strip() for line in kb_text.splitlines() if line.strip()]
    for line in kb_lines[:5]:
        plan += f"- {line}\n"

    plan += "\nNext actions from tracker:\n"
    next_actions = [row.get("next_action", "") for row in rows if row.get("next_action")]
    if next_actions:
        for action in next_actions[:5]:
            plan += f"- {action}\n"
    else:
        plan += "- Add at least one application with a next_action in tracker/applications.csv.\n"

    return plan


def generate_cover_letter(job_text: str, resume_text: str) -> str:
    company = extract_label_value(job_text, "Company") or "Hiring Team"
    role = extract_label_value(job_text, "Role") or "the role"

    letter = "Cover Letter Draft\n===================\n\n"
    letter += f"Dear {company} Team,\n\n"
    letter += (
        f"I am excited to apply for {role}. My background in Python, data analysis, "
        "and project work aligns well with the responsibilities described in the job poster. "
        "I enjoy building practical solutions, documenting results, and collaborating with teams.\n\n"
    )
    letter += (
        "Highlights from my resume include hands-on projects, version control with Git, "
        "and experience presenting findings clearly. I am eager to contribute and learn.\n\n"
    )
    letter += "Thank you for your time and consideration.\n"
    letter += "Sincerely,\nSample Student\n"

    return letter


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def run_agent() -> None:
    ensure_folders()

    job_files = list_input_files(JOB_DIR)
    resume_files = list_input_files(RESUME_DIR)
    kb_files = list_input_files(KB_DIR)

    if not job_files or not resume_files or not kb_files:
        print("Please add .txt or .pdf files in input_jobs, input_resumes, and input_kb folders.")
        return

    job_file = select_file(job_files, "Job poster")
    resume_file = select_file(resume_files, "Resume")

    if not job_file or not resume_file:
        print("Missing job poster or resume file.")
        return

    job_text = read_file_text(job_file)
    resume_text = read_file_text(resume_file)
    kb_text, kb_count = read_combined_text(kb_files)

    if not job_text.strip() or not resume_text.strip() or kb_count == 0:
        print("One or more input files are empty. Please check input folders.")
        return

    job_skills = extract_keywords(job_text)
    resume_skills = extract_keywords(resume_text)
    matched, missing, score = compare_skills(job_skills, resume_skills)
    top_terms = extract_top_terms(job_text)

    job_report = generate_job_analysis(job_text, job_skills, top_terms)
    gap_report = generate_skill_gap_report(job_skills, resume_skills, matched, missing, score)
    resume_suggestions = generate_resume_suggestions(job_skills, missing)
    interview_questions = generate_interview_questions(job_skills, kb_text)

    create_or_update_tracker()
    rows = load_applications()
    reminders = generate_reminders(rows)
    dashboard = generate_status_dashboard(rows)
    preparation_plan = generate_preparation_plan(missing, kb_text, rows)
    cover_letter = generate_cover_letter(job_text, resume_text)

    final_report = "CareerPrep Job-Hunting Agent Report\n"
    final_report += f"Generated on: {datetime.now().isoformat(timespec='seconds')}\n"
    final_report += f"Selected Job File: {job_file.name}\n"
    final_report += f"Selected Resume File: {resume_file.name}\n"
    final_report += "====================================\n\n"
    final_report += job_report + "\n"
    final_report += gap_report + "\n"
    final_report += resume_suggestions + "\n"
    final_report += interview_questions + "\n"
    final_report += preparation_plan + "\n"
    final_report += dashboard + "\n"
    final_report += reminders + "\n"

    save_text(OUTPUT_DIR / "job_analysis_report.txt", job_report)
    save_text(OUTPUT_DIR / "skill_gap_report.txt", gap_report)
    save_text(OUTPUT_DIR / "tailored_resume_suggestions.txt", resume_suggestions)
    save_text(OUTPUT_DIR / "interview_questions.txt", interview_questions)
    save_text(OUTPUT_DIR / "preparation_plan.txt", preparation_plan)
    save_text(OUTPUT_DIR / "cover_letter.txt", cover_letter)
    save_text(OUTPUT_DIR / "final_agent_report.txt", final_report)
    save_text(TRACKER_DIR / "reminders.txt", reminders)

    print("Agent completed successfully.")
    print(f"Job files found: {len(job_files)}")
    print(f"Resume files found: {len(resume_files)}")
    print(f"KB files found: {kb_count}")
    print(f"Match score: {score}%")
    print("Outputs saved in outputs/ and tracker/ folders.")


if __name__ == "__main__":
    run_agent()
