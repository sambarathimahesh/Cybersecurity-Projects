#!/usr/bin/env python3
"""Simple runnable job-requirement extraction + resume alignment tool.

Usage:
  python3 job_portal_resume_aligner.py --job job.txt --resume resume.txt
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STOPWORDS = {
    "and", "the", "with", "for", "you", "your", "our", "are", "this", "that", "will", "from",
    "have", "has", "been", "into", "than", "their", "they", "job", "role", "candidate", "years",
}

COMMON_SKILLS = {
    "python", "java", "javascript", "sql", "aws", "azure", "gcp", "linux", "splunk", "siem",
    "incident response", "threat hunting", "vulnerability management", "ids", "firewall", "docker",
    "kubernetes", "git", "network security", "penetration testing", "soc", "edr",
}


@dataclass
class MatchReport:
    score: float
    missing_skills: list[str]
    matched_skills: list[str]
    keyword_gaps: list[str]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z\-\+\.]{1,}", text.lower())


def extract_phrases(text: str, phrases: Iterable[str]) -> list[str]:
    t = normalize(text)
    return sorted({p for p in phrases if p in t})


def extract_requirements(job_description: str) -> dict:
    skills = extract_phrases(job_description, COMMON_SKILLS)

    years_match = re.search(r"(\d+)\+?\s+years?", job_description.lower())
    experience_years = years_match.group(1) + "+" if years_match else "not specified"

    certs = []
    for cert in ("security+", "cissp", "ceh", "oscp", "aws certified"):
        if cert in job_description.lower():
            certs.append(cert.upper())

    keywords = [w for w in tokenize(job_description) if w not in STOPWORDS and len(w) > 3]
    keywords = sorted(set(keywords))[:30]

    return {
        "must_have_skills": skills,
        "experience_years": experience_years,
        "certifications": certs,
        "keywords": keywords,
    }


def compare_resume(job_reqs: dict, resume_text: str) -> MatchReport:
    resume_skills = set(extract_phrases(resume_text, COMMON_SKILLS))
    must_have = set(job_reqs["must_have_skills"])

    matched = sorted(must_have & resume_skills)
    missing = sorted(must_have - resume_skills)

    skill_score = (len(matched) / len(must_have) * 100) if must_have else 70

    resume_tokens = set(tokenize(resume_text))
    gaps = [k for k in job_reqs["keywords"] if k not in resume_tokens][:15]
    keyword_score = max(0, 100 - (len(gaps) * 4))

    final_score = round(skill_score * 0.7 + keyword_score * 0.3, 1)

    return MatchReport(
        score=final_score,
        missing_skills=missing,
        matched_skills=matched,
        keyword_gaps=gaps,
    )


def rewrite_resume(resume_text: str, job_reqs: dict, report: MatchReport) -> str:
    lines = [l.rstrip() for l in resume_text.splitlines()]
    summary = (
        "Professional Summary: Security-focused candidate aligned with role requirements "
        f"including {', '.join(report.matched_skills[:5]) or 'relevant security operations skills'}."
    )

    additions = []
    if report.missing_skills:
        additions.append(
            "Target Skills to Emphasize (only if truthful): " + ", ".join(report.missing_skills)
        )

    jd_keywords = ", ".join(job_reqs["keywords"][:12])
    additions.append(f"ATS Keywords to Reflect in Experience Bullets: {jd_keywords}")

    return "\n".join([summary, ""] + lines + ["", *additions])


def run(job_path: Path, resume_path: Path, output_path: Path | None) -> dict:
    job_text = job_path.read_text(encoding="utf-8")
    resume_text = resume_path.read_text(encoding="utf-8")

    requirements = extract_requirements(job_text)
    report = compare_resume(requirements, resume_text)
    revised_resume = rewrite_resume(resume_text, requirements, report)

    result = {
        "requirements": requirements,
        "match_report": {
            "score": report.score,
            "matched_skills": report.matched_skills,
            "missing_skills": report.missing_skills,
            "keyword_gaps": report.keyword_gaps,
        },
        "revised_resume": revised_resume,
    }

    if output_path:
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="Path to job description text file")
    parser.add_argument("--resume", required=True, help="Path to resume text file")
    parser.add_argument("--out", help="Optional output JSON path")
    args = parser.parse_args()

    result = run(Path(args.job), Path(args.resume), Path(args.out) if args.out else None)

    print("Match Score:", result["match_report"]["score"])
    print("Matched Skills:", ", ".join(result["match_report"]["matched_skills"]) or "None")
    print("Missing Skills:", ", ".join(result["match_report"]["missing_skills"]) or "None")
    print("Keyword Gaps:", ", ".join(result["match_report"]["keyword_gaps"][:8]) or "None")


if __name__ == "__main__":
    main()
