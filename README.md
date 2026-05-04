# Cybersecurity-Projects

## Job/Resume Alignment Runner

You can now run a simple CLI tool that:
- extracts job requirements from a job description,
- compares a resume against those requirements,
- outputs a match report,
- produces a revised resume draft.

### Run

```bash
python3 job_portal_resume_aligner.py --job sample_job.txt --resume sample_resume.txt --out output.json
```

### Files

- `job_portal_resume_aligner.py`: runnable alignment script
- `sample_job.txt`: sample job description input
- `sample_resume.txt`: sample resume input
- `output.json`: generated output sample
