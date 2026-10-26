# ResumeMania Leaderboard

**Do you want to know who's ready to place?**

Post one job. Students send resumes. See who fits, ranked fairly and kept private.

- Every score shows its evidence: the exact line in the resume behind each requirement
- Only the top students go public (top 10% by default, set per campaign), and only by GitHub username
- Below the bar stays private: a student's score is shown to that student and nobody else

No accounts. A student's ID is the `github.com/username` link in their resume. Uploading again with the same link replaces their old entry. A resume without a GitHub link is turned away with a clear message.

This is the cohort version of [ResumeMania Personal](https://github.com/Uchiha-Itachi0/resumemania-personal). It uses the same agents, validation gate and design, and adds campaigns, weighted scoring, eligibility and a leaderboard.

## Setup

### 1. What you need

| | How to check | Get it |
|---|---|---|
| Python 3.11 or newer | `python3 --version` (Windows: `py --version`) | [python.org/downloads](https://www.python.org/downloads/) |
| Git | `git --version` | [git-scm.com](https://git-scm.com/downloads) |
| A free Gemini API key | | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

### 2. Download the code

```bash
git clone https://github.com/Uchiha-Itachi0/resumemania-leaderboard.git
cd resumemania-leaderboard
```

### 3. Create a virtual environment and install

**macOS or Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell says running scripts is disabled, skip `Activate.ps1` and put `.venv\Scripts\` in front of each command instead, for example `.venv\Scripts\python -m streamlit run app.py`.

### 4. Add your Gemini key

Copy the example settings file:

```bash
cp .env.example .env
```

On Windows: `copy .env.example .env`

Open `.env` in any editor and paste your key after `GEMINI_API_KEY=` (no quotes, no spaces). `.env` is git-ignored, so your key is never committed.

### 5. Run it

```bash
streamlit run app.py
```

Your browser opens http://localhost:8501.

### 6. Load the sample data (optional, recommended)

This creates ten sample job campaigns and fills them with 90 fictional students, so every page has something to show:

```bash
python scripts/seed_campaigns.py
python scripts/seed_resumes.py
```

The first command reads the ten job descriptions in `samples/jds/` with Gemini (10 quick calls). The second runs **offline with no AI calls** in about 10 seconds. Both are safe to run again. See [Sample data](#sample-data) for details.

### Using the app

1. **Coordinator:** open **Campaigns**, paste a job description, choose the benchmark, the scoring weights and how many students the public board shows, then press **Start my campaign**. The job is read once, and that one checklist is used for every student.
2. **Students:** open **Check my rank**, pick the campaign, upload a resume that includes a `github.com/your-username` link and press **Check my rank**.
3. **Everyone:** **Leaderboard** shows the top students. **Dashboard** shows the coordinator the full ranked list, the score spread and any resumes that couldn't be read.

### Next time

You only install once. To start the app again, open a terminal in the project folder and run:

```bash
source .venv/bin/activate
streamlit run app.py
```

On Windows: `.venv\Scripts\Activate.ps1`, then `streamlit run app.py`.

### Get the latest version

```bash
git pull
pip install -r requirements.txt
```

## Sample data

Ten sample job descriptions and ten fictional student resumes come with the repo. Every name, email, phone number and GitHub username in them is made up.

```bash
python scripts/seed_campaigns.py
```

That creates ten campaigns, each showing the top 25% on its public board (Data Analyst, AI Engineer, Frontend, Java Backend, ML, Product Analyst, DevOps, Android, MERN and Cybersecurity) from `samples/jds/`. It takes a few seconds and is safe to run twice.

To fill every campaign with results, submit the ten sample resumes plus 80 generated students (eight per job, from strong to weak) to all ten campaigns. By default this runs **offline, with no AI calls**: a keyword-matching stand-in (`scripts/offline_llm.py`) replaces Gemini, and everything after it (validation gate, scoring, ranking, leaderboard) is the real code. It takes about 2 seconds:

```bash
python scripts/seed_resumes.py
```

Add `--live` to score them with real Gemini instead (about 400 calls, roughly 10 minutes on a free key). Offline scores are rougher than Gemini's, so use them for demos, never to judge real students.

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
| Public | Top share of eligible (10% by default; 25%, 50% or everyone per campaign), rounded up, at least 1 | Shown on the leaderboard by GitHub username |

**Ties:** higher score first, then a higher required-skills component, then the earlier upload.
**Recalculation:** every upload recalculates the campaign's ranking and saves a snapshot.
**Sharing:** a resume is shown on the leaderboard only if the student ticked the consent box. Emails, phone numbers, links, ID numbers, addresses and the student's name are removed first.

These rules live in `resumemania/ranking.py` and `resumemania/service.py`, outside the UI, and are covered by tests.

## Project layout

```
app.py                     Navigation: Home, Check my rank, Leaderboard, Campaigns, Dashboard
resumemania/               Engine (shared with ResumeMania Personal, plus the files below)
  weighted.py              Five-part weighted score with weight redistribution
  ranking.py               Eligibility, public-share rounding, tie-breaks
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

With the virtual environment active:

```bash
pip install -r requirements-dev.txt
pytest --cov
ruff check .
```

## Troubleshooting

| You see | Do this |
|---|---|
| `python3: command not found` | Install Python 3.11+. On Windows use `py` instead of `python3` |
| `streamlit: command not found` | The virtual environment isn't active. Run `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with the virtual environment active |
| `Port 8501 is already in use` | Another copy is running. Stop it, or run `streamlit run app.py --server.port 8502` |
| "Add your Gemini key to start" | Create `.env` from `.env.example`, add your key, restart the app |
| "Gemini is busy" | Google is overloaded or you hit the free rate limit. Wait a minute and try again |
| "Add your GitHub profile link to your resume" | The resume needs a `github.com/your-username` link. It is the student's ID |

## Before real student data

This build is made for workshops and demos on one machine. Before you use it with a real cohort:

- **Access:** there are no accounts, so anyone who can open the app can open the Dashboard and create campaigns. Run it on a machine only staff can reach, or put it behind your college's sign-in (for example Supabase Auth).
- **Identity:** anyone can put any GitHub link in a resume. If that matters, verify ownership (for example, ask students to add a code to their GitHub bio).
- **Consent:** tell students what is stored, who sees it and how long you keep it. Delete `data/` when the drive ends.
- **Use:** scores estimate how well a resume shows a job's requirements. They are not hiring decisions and must never use protected characteristics.
