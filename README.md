# ResumeMania Leaderboard

**Do you want to know who's ready to place?**

Post one job. Students send resumes. See who fits, ranked fairly and kept private.

- Every score shows its evidence: the exact line in the resume behind each requirement
- Only the top 10% go public, and only by GitHub username
- Below the bar stays private: a student's score is shown to that student and nobody else

No accounts. A student's ID is the `github.com/username` link in their resume. Uploading again with the same link replaces their old entry. A resume without a GitHub link is turned away with a clear message.

This is the cohort version of [ResumeMania Personal](https://github.com/Uchiha-Itachi0/resumemania-personal). It uses the same agents, validation gate and design, and adds campaigns, weighted scoring, eligibility and a leaderboard.

## Start in 3 minutes

You need Python 3.10 or newer and a free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/Uchiha-Itachi0/resumemania-leaderboard.git
cd resumemania-leaderboard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Paste your key after `GEMINI_API_KEY=` in `.env`, then:

```bash
streamlit run app.py
```

1. **Coordinator:** open **Campaigns**, paste a job description and press **Start my campaign**. The job is read once, and that one checklist is used for every student.
2. **Students:** open **Check my rank**, pick the campaign, upload a resume that includes a `github.com/your-username` link and press **Check my rank**.
3. **Everyone:** **Leaderboard** shows the top 10%. **Dashboard** shows the coordinator the full ranked list, the score spread and any resumes that couldn't be read.

## Try it with sample data

Ten sample job descriptions and ten fictional student resumes come with the repo. Every name, email, phone number and GitHub username in them is made up.

```bash
python scripts/seed_campaigns.py
```

That creates ten campaigns (Data Analyst, AI Engineer, Frontend, Java Backend, ML, Product Analyst, DevOps, Android, MERN and Cybersecurity) from `samples/jds/`. It takes a few seconds and is safe to run twice.

To fill every campaign with results, submit all ten sample resumes to all ten campaigns (100 real checks, about 10 minutes):

```bash
python scripts/seed_resumes.py
```

The resumes are in `samples/resumes/` (eight PDFs, two DOCX). Each student fits one or two jobs well, and one is deliberately weak, so you see every status. To regenerate them somewhere else:

```bash
python scripts/make_sample_resumes.py ~/Downloads/resumemania-sample-resumes
```

## How a resume is scored

The AI reads and quotes. Plain Python does the maths.

| Component | Default weight | What counts |
|---|---|---|
| Required skills | 40% | Must-have skills shown in the resume |
| Evidence in projects and work | 25% | Requirements proved in Experience or Projects, not only listed under Skills |
| Experience | 15% | Experience asks (years, internships, domain work) |
| Preferred skills | 10% | Nice-to-have skills |
| Education and certifications | 10% | Degree and certification asks |

Shown = full credit, partly shown = half, not shown = none. If a job has no asks for a component (say, no education requirement), its weight is shared across the others, so nobody loses points for it. Coordinators can change the weights per campaign. Check them with your placement team before real use.

## Who appears where

| Status | Rule | What happens |
|---|---|---|
| Invalid | Unreadable, too short or not a resume | Not ranked. The student and the dashboard see the reason |
| Irrelevant | Shows none of the job's requirements | Not ranked. Private explanation |
| Below | Under the benchmark (default 60%) | Score visible to the student only. Never named anywhere |
| Eligible | At or above the benchmark | Ranked. The dashboard lists them for guidance |
| Public | Top 10% of eligible, rounded up, at least 1 | Shown on the leaderboard by GitHub username |

**Ties:** higher score first, then a higher required-skills component, then the earlier upload.
**Recalculation:** every upload recalculates the campaign's ranking and saves a snapshot.
**Sharing:** a resume is shown on the leaderboard only if the student ticked the consent box. Emails, phone numbers, links, ID numbers, addresses and the student's name are removed first.

These rules live in `resumemania/ranking.py` and `resumemania/service.py`, outside the UI, and are covered by tests.

## Project layout

```
app.py                     Navigation: Home, Check my rank, Leaderboard, Campaigns, Dashboard
resumemania/               Engine (shared with ResumeMania Personal, plus the files below)
  weighted.py              Five-part weighted score with weight redistribution
  ranking.py               Eligibility, top 10% rounding, tie-breaks
  service.py               Campaigns, uploads, leaderboard and dashboard, with the privacy rules
  storage.py               SQLite: campaigns, submissions, evaluations, leaderboard snapshots
  github.py                Reads the student's GitHub username from their resume
  redact.py                Removes contact details before a resume is shared
ui/                        Streamlit pages, theme (matched to vibemyad.com) and all copy (ui/copy.py)
scripts/                   Seed the sample campaigns and generate the sample resumes
samples/                   Ten job descriptions and ten fictional resumes
tests/                     Unit, integration and end-to-end UI tests (no API key needed)
```

## Settings (`.env`)

| Variable | Default | What it does |
|---|---|---|
| `GEMINI_API_KEY` | (required) | Your Gemini key |
| `GEMINI_MODEL_FAST` | `gemini-3.5-flash-lite` | Reads resumes and job descriptions |
| `GEMINI_MODEL_SMART` | `gemini-3.5-flash-lite` | Matches evidence, reviews writing, writes feedback. Set `gemini-3.8-flash` for deeper answers once Google's capacity issues are fixed |
| `GEMINI_MODEL_FALLBACKS` | `gemini-3.5-flash` | Tried in order when a model is busy, rate limited or too slow |
| `GEMINI_TIMEOUT_SECONDS` | `45` | Give up on one AI call after this long and try the next model |
| `RESUMEMANIA_DB_PATH` | `data/resumemania.db` | Where campaigns and results are saved |
| `RESUMEMANIA_MAX_UPLOAD_MB` | `5` | Largest resume file allowed |

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest --cov
ruff check .
```

## Before real student data

This build is made for workshops and demos on one machine. Before you use it with a real cohort:

- **Access:** there are no accounts, so anyone who can open the app can open the Dashboard and create campaigns. Run it on a machine only staff can reach, or put it behind your college's sign-in (for example Supabase Auth).
- **Identity:** anyone can put any GitHub link in a resume. If that matters, verify ownership (for example, ask students to add a code to their GitHub bio).
- **Consent:** tell students what is stored, who sees it and how long you keep it. Delete `data/` when the drive ends.
- **Use:** scores estimate how well a resume shows a job's requirements. They are not hiring decisions and must never use protected characteristics.
