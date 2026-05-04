# Job Portal + Resume Alignment Workflow

This guide helps you automate three things:

1. Collect job postings from job portals across the internet.
2. Extract candidate requirements from each job description.
3. Compare a resume against the requirement, then rewrite the resume so it aligns with the target job.

---

## 1) Job portals to monitor

Use a mix of global and regional portals:

- LinkedIn Jobs
- Indeed
- Glassdoor
- Monster
- ZipRecruiter
- SimplyHired
- Wellfound (AngelList)
- Dice (tech jobs)
- Remote OK (remote jobs)
- We Work Remotely
- FlexJobs
- Google Jobs index
- Company career pages (direct source)

> Best practice: always keep the original posting URL, title, company, location, posted date, and full description text.

---

## 2) Data model for each job

Store each job in structured JSON:

```json
{
  "source": "LinkedIn",
  "url": "https://...",
  "company": "Example Corp",
  "job_title": "Security Analyst",
  "location": "Remote",
  "posted_date": "2026-05-04",
  "description_raw": "full text...",
  "requirements": {
    "must_have_skills": ["SIEM", "Python", "Incident Response"],
    "nice_to_have_skills": ["AWS", "Splunk"],
    "experience_years": "3+",
    "education": "Bachelor's in CS or related",
    "certifications": ["Security+"],
    "keywords": ["threat hunting", "IDS", "vulnerability management"]
  }
}
```

---

## 3) Resume alignment logic

For each resume + job pair:

1. Parse resume into sections:
   - Summary
   - Skills
   - Experience
   - Projects
   - Certifications
   - Education
2. Extract normalized keywords from resume and JD.
3. Score match by weighted categories.

### Suggested scoring

- Core technical skills: **40%**
- Relevant experience responsibilities: **30%**
- Domain keywords and tools: **15%**
- Certifications/education: **10%**
- Location/work authorization constraints: **5%**

### Thresholds

- **80–100**: High match (submit with light edits)
- **60–79**: Medium match (rewrite targeted bullets)
- **<60**: Low match (major rewrite or skip job)

---

## 4) Rewrite rules (safe + truthful)

When resume is not aligned:

- Keep facts truthful (no fake employers, dates, or skills).
- Reorder bullets to prioritize JD-relevant achievements.
- Replace vague wording with measurable impact.
- Mirror job-description terminology naturally.
- Add missing relevant tools only if actually used by candidate.
- Tailor summary to role title, company, and domain.

### Bullet transformation pattern

Use:

**Action + Tool + Scope + Result**

Example:

- Before: "Worked on security monitoring."
- After: "Monitored SIEM alerts across 120+ endpoints and reduced incident triage time by 35% using Splunk correlation rules."

---

## 5) Prompt template for LLM automation

Use this prompt when candidate uploads a resume:

```text
You are an expert resume optimizer.

INPUTS:
1) Job Description (JD)
2) Candidate Resume

TASKS:
A) Extract JD requirements into:
- must-have skills
- nice-to-have skills
- years of experience
- certifications
- responsibilities
- keywords

B) Compare resume vs JD and provide:
- match score (0-100)
- missing skills list
- weak sections list
- ATS keyword gaps

C) Rewrite the resume to improve alignment while staying truthful:
- optimize summary
- optimize skills section
- rewrite experience bullets with measurable impact
- preserve real experience and dates
- do not invent qualifications

D) Output:
1) Match Report
2) Revised Resume
3) ATS Keyword Checklist
```

---

## 6) End-to-end pipeline

1. Fetch jobs from multiple portals (API/scraper depending on terms of use).
2. Deduplicate by URL + title + company.
3. Extract requirement fields from JD.
4. Candidate uploads resume (PDF/DOCX/TXT).
5. Parse resume text.
6. Run JD-vs-resume matching.
7. Generate revised resume + match report.
8. Export to DOCX/PDF and log version history.

---

## 7) Compliance and ethics

- Follow each portal's Terms of Service.
- Respect robots.txt and API usage limits.
- Never fabricate candidate credentials.
- Protect personal data (PII) in storage and logs.

---

## 8) Minimum deliverables for your system

- Multi-portal job ingestion module.
- Requirement extraction module.
- Resume parser.
- Match scoring engine.
- Resume rewriter with truthfulness constraints.
- Dashboard showing:
  - job count by portal,
  - candidate match scores,
  - before/after resume versions,
  - submission-ready status.
