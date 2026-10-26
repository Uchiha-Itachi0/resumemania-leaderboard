"""Every user-facing string in one place.

House rules (VMA Playbook): outcome first, short words, specific numbers, "you" over "we",
no em dashes, no AI filler words. One call to action per audience, worded the same everywhere:
coordinators "Start my campaign", students "Check my rank".
"""

APP_NAME = "ResumeMania"
CTA_COORD = "Start my campaign"
CTA_STUDENT = "Check my rank"

# ---------- landing ----------
HERO_BADGE = "Placement benchmarking for colleges."
HERO_TITLE = ("<span class='g1'>Do you</span> <span class='g2'>want to know</span> "
              "who's <em>ready to place?</em>")
HERO_SUB = "Post one job. Students send resumes. See who fits, ranked fairly and kept private."
HERO_TICKS = ("Every score shows its evidence", "Only the top students go public", "Below the bar stays private")

HERO_CTA_NOTE = "No account needed. The GitHub link in your resume is your ID."

HOW_EYEBROW = "How it works"
HOW_TITLE = "Three steps to see who's <em>ready.</em>"
HOW_STEPS = (
    ("Ready in 1 minute", "Post the job", "Paste one job description. It becomes the checklist every student is scored on."),
    ("Scored in 10 seconds", "Students send resumes", "Each student gets a private report with evidence and fixes."),
    ("Updates live", "See who's ready", "You get a ranked list. Only the top slice goes public, by GitHub name."),
)
FAQ = (
    ("Who sees a student's score?",
     "The student, right after uploading. Staff see students at or above the benchmark. "
     "Nobody else's score is ever shown."),
    ("Why a GitHub username?",
     "It's unique, so there's no account to make. We read it from the github.com link in your resume. "
     "Upload again with the same link to replace your entry."),
    ("Is the score a hiring decision?",
     "No. It's an estimate of how well a resume shows this job's requirements. Use it to guide, not to reject."),
    ("Does the AI decide the rank?",
     "No. The AI reads resumes and quotes evidence. Plain code adds up the score, applies the benchmark and ranks."),
    ("Can a resume trick the AI?",
     "Resume text is treated as data, never as instructions, and every quote is checked against the resume."),
)

# ---------- coordinator ----------
CAMPAIGNS_TITLE = "Your <em>campaigns.</em>"
CAMPAIGNS_SUB = "One job per campaign. Students pick it on the Check my rank page."
NEW_CAMPAIGN = "New campaign"
CAMP_TITLE = "Campaign title"
CAMP_TITLE_HINT = "e.g. Data Analyst Intern, CSE 2026"
CAMP_COHORT = "Cohort (optional)"
CAMP_COHORT_HINT = "e.g. CSE batch 2026, Pune campus"
CAMP_JD = "Job description"
CAMP_JD_HINT = "Paste the full job post: duties, must-haves and nice-to-haves."
CAMP_BENCHMARK = "Benchmark"
CAMP_BENCHMARK_HELP = "Students at or above this score are ranked. Everyone below sees their score privately."
WEIGHTS_TITLE = "How the score adds up"
WEIGHTS_SUB = ("Each part earns up to its points. Shown in the resume earns all of them, partly shown earns half. "
               "The five must add up to 100. Check them with your placement team.")
WEIGHT_FIELDS = {
    "required": ("Required skills", "Must-have skills from the job that the resume shows."),
    "evidence": ("Applied evidence", "Skills proved in an internship or project, not only listed under Skills."),
    "experience": ("Experience", "Asks like '1+ years' or 'internship in fintech'."),
    "preferred": ("Preferred skills", "Nice-to-have skills from the job."),
    "education": ("Education", "Degree and certification asks."),
}
WEIGHTS_OK = "Total {total} of 100"
WEIGHTS_BAD = "Total {total} of 100. Adjust the numbers so they add up to 100."
CAMP_PRIVACY = ("Students see their own score. You see students at or above the benchmark. "
                "Only the top slice you pick below appears on the public leaderboard.")
CAMP_CREATING = "Reading the job and building the checklist"
CAMP_CREATED = "Campaign ready. Students can now pick {title} and upload."
NO_CAMPAIGNS = "No campaigns yet. Start one with a job description."
OPEN_DASHBOARD = "Open dashboard"

DASH_EYEBROW = "Dashboard · {cohort}"
DASH_TITLE = "{title}: <em>who's ready.</em>"
DASH_SUB = "Benchmark {benchmark}%. Scores are estimates, not hiring decisions."
TILE_SUBMITTED = "Resumes in"
TILE_ELIGIBLE = "At or above benchmark"
TILE_PUBLIC = "On public board"
DIST_TITLE = "Score spread"
DIST_NOTE = "Readable, relevant resumes only."
RANKED_TITLE = "Ranked candidates"
RANKED_NOTE = ("Students at or above the benchmark. \"On public board\" means students see them on the Leaderboard; "
               "\"Staff only\" means they're ranked but only you see them. Change the split with "
               "\"Public leaderboard shows\" above. Use this list to plan guidance, not to reject.")
BADGE_PUBLIC = "On public board"
BADGE_PRIVATE = "Staff only"
RANKED_EMPTY = "Nobody is at the benchmark yet."
DASH_EMPTY = ("No resumes yet. Send students to the Check my rank page and ask them to pick this campaign. "
              "This page fills in as each resume is scored.")
PROBLEMS_TITLE = "Needs attention"
PROBLEMS_NOTE = "These resumes couldn't be scored. The student sees the same reason."
CHECKLIST_TITLE = "The checklist every resume is scored on"
EXPORT = "Download ranked list (.csv)"

# ---------- student ----------
STUDENT_TITLE = "Where do you <em>stand?</em>"
STUDENT_SUB = ("Pick the job and add your resume. The GitHub link in your resume is your ID. "
               "Results in about 10 seconds.")
GITHUB_FROM_RESUME = "Done. You're @{username}, from the GitHub link in your resume."
RESUME_GITHUB_NOTE = "Your resume needs a GitHub profile link, like github.com/your-username."
NO_CAMPAIGN_YET = "No campaigns yet. Ask your coordinator to start one."
PICK_CAMPAIGN = "Campaign"
RESUME_PASTE = "Paste"
RESUME_UPLOAD = "Upload"
RESUME_PASTE_HINT = "Paste your resume text here."
RESUME_UPLOAD_HELP = "PDF, DOCX or TXT, up to {mb} MB."
CONSENT = "Show my resume as an example to other students if I make the public board (contact details removed)"
RUNNING = "Scoring your resume"
RUN_DONE = "Done. Your private report is ready."
ERR_NEED_RESUME = "Add your resume first: upload a file or paste the text."
STATUS_HEAD = {
    "eligible": "You're ranked <em>#{rank}</em> of {total}.",
    "below": "You're at <em>{score}%.</em> The bar is {benchmark}%.",
    "irrelevant": "This resume doesn't match <em>this job</em> yet.",
    "invalid": "We couldn't <em>read</em> this resume.",
    "failed": "The AI was <em>busy.</em> Try again.",
}
PUBLIC_YES = "You're on the public leaderboard."
PUBLIC_NO = "You're ranked privately. Only the top {share} show publicly."
REUPLOAD_NOTE = "Improve your resume and upload it again. Same GitHub link, so your old entry is replaced."
BREAKDOWN_TITLE = "How your score adds up"
REQS_TITLE = "Requirement by requirement"
PLAN_TITLE = "Do these first"
REWRITES_TITLE = "Suggested rewrites"
REWRITES_NOTE = "Built only from your facts. Fill in every [N] and [CONFIRM] yourself before you use one."

# ---------- leaderboard ----------
BOARD_EYEBROW = "Leaderboard · {title}"
BOARD_TITLE = "The top <em>{share}.</em>"
BOARD_TITLE_ALL = "Everyone who made <em>the bar.</em>"
BOARD_SUB = "{eligible} of {submitted} reached the {benchmark}% bar. Showing the top {share}: {shown}."
SHARE_LABEL = "Public leaderboard shows"
SHARE_HELP = ("The PRD default is the top 10%. Everyone else at the benchmark is ranked privately. "
              "This is saved for the campaign, so everyone sees the same board.")
SHARE_OPTIONS = {0.10: "Top 10% (default)", 0.25: "Top 25%", 0.50: "Top 50%", 1.0: "Everyone at the benchmark"}
SHARE_SHORT = {0.10: "10%", 0.25: "25%", 0.50: "50%", 1.0: "100%"}
SHARE_FILTER = {0.10: "Top 10%", 0.25: "Top 25%", 0.50: "Top 50%", 1.0: "Everyone"}
SHARE_SAVED = "Saved. The public board now shows {label}."
TILE_PUBLIC_SUB = "{label}, rounded up"
BOARD_EMPTY = "Nobody is on the board yet. Check back after more resumes come in."
SEE_RESUME = "See their resume (contact details removed)"

# ---------- shared ----------
STATUS_TEXT = {"matched": "Shown", "partial": "Partly shown", "missing": "Not shown yet"}
STATUS_CLASS = {"matched": "good", "partial": "part", "missing": "miss"}
NEED_TEXT = {"must": "Must have", "nice": "Nice to have"}
SEVERITY_TEXT = {"high": "High impact", "medium": "Medium", "low": "Small fix"}
NO_EVIDENCE = "Nothing in the resume shows this yet."
SETUP_TITLE = "Add your Gemini key to start"
SETUP_BODY = "Scoring needs a key. It takes about 2 minutes and stays on this computer."
SETUP_STEPS = (
    "Get a free key at <code>aistudio.google.com/apikey</code>",
    "Copy <code>.env.example</code> to <code>.env</code> and paste it after <code>GEMINI_API_KEY=</code>",
    "Stop the app and run <code>streamlit run app.py</code> again",
)
