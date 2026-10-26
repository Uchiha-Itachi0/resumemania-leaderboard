"""Ten fictional student resumes for demos and workshops.

Every name, email, phone number, company project and GitHub username here is made up.
Each student fits one or two of the sample campaigns well and the others less, and a few
resumes are deliberately weaker (vague bullets, no numbers) so the feedback has work to do.
"""

from __future__ import annotations

import zlib

RESUMES: list[dict] = [
    {
        "file": "aarav-mehta-data-analyst",
        "name": "Aarav Mehta",
        "headline": "Data Analyst · SQL · Python · Power BI",
        "contact": "Pune · +91 90000 10001 · aarav.mehta@example.com · github.com/aarav-mehta-data",
        "summary": "Final-year Computer Engineering student who turns messy business data into dashboards and "
                   "decisions. Two analytics internships and a published A/B testing case study.",
        "experience": [
            ("Data Analyst Intern", "Kirana Kart (D2C grocery)", "Jan 2026 – Jun 2026", [
                "Wrote SQL with window functions and CTEs on 4M order rows to find the 3 cities driving 60% of repeat purchases.",
                "Built a Power BI dashboard on delivery delays used every Monday by a 12-person operations team.",
                "Analysed an A/B test on free-delivery thresholds; the winning variant lifted average order value by 9%.",
            ]),
            ("Business Analytics Intern", "Sahyadri Logistics", "May 2025 – Jul 2025", [
                "Automated a weekly Excel report with Python and Pandas, saving the finance team 5 hours a week.",
                "Cleaned 18 months of shipment data and flagged 240 duplicate invoices worth ₹11 lakh.",
            ]),
        ],
        "projects": [
            ("Campus Food Demand Forecast", "github.com/aarav-mehta-data/canteen-forecast", [
                "Forecast daily canteen orders with Python (Pandas, statsmodels); cut food waste 14% over a 6-week pilot.",
            ]),
        ],
        "skills": {
            "Analytics": "SQL (PostgreSQL, MySQL), Python (Pandas, NumPy), Excel, statistics, A/B testing",
            "BI": "Power BI, Tableau, Google Analytics 4",
            "Tools": "Git, Jupyter, dbt (basics)",
        },
        "education": [("B.E. Computer Engineering", "Savitribai Phule Pune University", "2022 – 2026", "CGPA 8.6/10")],
        "extras": ["Google Data Analytics Certificate, 2025", "Winner, Inter-college Data Hackathon, Pune 2025"],
    },
    {
        "file": "diya-iyer-ai-engineer",
        "name": "Diya Iyer",
        "headline": "AI Engineer · LLM apps · RAG · Python",
        "contact": "Bengaluru · +91 90000 10002 · diya.iyer@example.com · github.com/diya-iyer-ai",
        "summary": "Computer Science student building LLM products end to end: retrieval, agents, evals and the "
                   "APIs around them.",
        "experience": [
            ("AI Engineering Intern", "Lexora Legal AI", "Jan 2026 – Present", [
                "Built a RAG pipeline over 40,000 court judgments with pgvector and FastAPI; answer accuracy on our eval set rose from 61% to 84%.",
                "Set up Langfuse tracing and an LLM-as-judge eval suite of 300 questions that runs on every pull request.",
                "Cut cost per query by 38% by routing simple questions to a smaller model.",
            ]),
        ],
        "projects": [
            ("StudyBuddy Agent", "github.com/diya-iyer-ai/studybuddy", [
                "LangGraph agent that plans revision schedules and quizzes students from their own notes; 450 weekly users on campus.",
                "Deployed with Docker on AWS ECS; p95 latency under 2.5 seconds.",
            ]),
            ("Fine-tuned Hindi FAQ Bot", "github.com/diya-iyer-ai/hindi-faq", [
                "Fine-tuned an open-source 7B model with LoRA on 6,000 Hindi support questions.",
            ]),
        ],
        "skills": {
            "AI": "OpenAI, Anthropic and Gemini APIs, RAG, LangGraph, LangChain, evals, prompt engineering, LoRA",
            "Backend": "Python, FastAPI, PostgreSQL, pgvector, Redis",
            "Cloud": "Docker, AWS (ECS, S3, Lambda), GitHub Actions, Git",
        },
        "education": [("B.Tech Computer Science", "PES University, Bengaluru", "2022 – 2026", "CGPA 9.1/10")],
        "extras": ["Finalist, Smart India Hackathon 2025", "Speaker, PyCon India 2025 student track"],
    },
    {
        "file": "kabir-malhotra-frontend",
        "name": "Kabir Malhotra",
        "headline": "Frontend Developer · React · TypeScript",
        "contact": "Delhi · +91 90000 10003 · kabir.malhotra@example.com · github.com/kabir-builds-ui",
        "summary": "Frontend developer who cares about fast, accessible interfaces. Ships React and Next.js apps "
                   "with real users.",
        "experience": [
            ("Frontend Intern", "Paisa Patra (fintech)", "Jun 2025 – Dec 2025", [
                "Rebuilt the onboarding flow in React and TypeScript; completion rose from 52% to 71%.",
                "Cut Largest Contentful Paint from 4.1s to 1.8s with code splitting and image optimisation.",
                "Wrote 120+ unit tests with Jest and React Testing Library; added Playwright smoke tests to CI.",
            ]),
        ],
        "projects": [
            ("Hostel Mess Menu", "github.com/kabir-builds-ui/mess-menu", [
                "Next.js and Tailwind app with weekly menus and ratings; 1,200 monthly users across 3 hostels.",
            ]),
            ("A11y Checker Extension", "github.com/kabir-builds-ui/a11y-lens", [
                "Chrome extension that flags WCAG contrast and label issues; 300 installs.",
            ]),
        ],
        "skills": {
            "Frontend": "React, Next.js, TypeScript, JavaScript, HTML, CSS, Tailwind CSS, Redux Toolkit",
            "Quality": "Jest, React Testing Library, Playwright, Lighthouse, WCAG 2.1",
            "Tools": "Git, Figma, Vite, Vercel, REST APIs",
        },
        "education": [("B.Tech Information Technology", "Guru Gobind Singh Indraprastha University", "2022 – 2026",
                       "CGPA 8.2/10")],
        "extras": ["Open source: 14 merged pull requests to a popular React UI library"],
    },
    {
        "file": "sneha-reddy-backend-java",
        "name": "Sneha Reddy",
        "headline": "Backend Developer · Java · Spring Boot",
        "contact": "Hyderabad · +91 90000 10004 · sneha.reddy@example.com · github.com/sneha-reddy-dev",
        "summary": "Backend developer who likes clean APIs and boring, reliable systems. Java, Spring Boot and "
                   "SQL, with microservices in production.",
        "experience": [
            ("Software Engineering Intern", "Nirman ERP Solutions", "Jan 2026 – Jun 2026", [
                "Built 9 REST endpoints in Spring Boot for an invoicing service handling 30,000 invoices a day.",
                "Moved slow reports to Redis caching; p95 response time fell from 1.4s to 220ms.",
                "Wrote integration tests with JUnit 5 and Testcontainers; coverage rose from 41% to 78%.",
            ]),
        ],
        "projects": [
            ("Bus Pass Microservices", "github.com/sneha-reddy-dev/bus-pass", [
                "3 Spring Boot services (auth, passes, payments) talking over Kafka, deployed with Docker Compose.",
            ]),
            ("Library Management API", "github.com/sneha-reddy-dev/library-api", [
                "Java, Spring Data JPA and MySQL with JWT auth and role-based access.",
            ]),
        ],
        "skills": {
            "Backend": "Java 17, Spring Boot, Spring Data JPA, Hibernate, REST, JWT, Kafka",
            "Data": "MySQL, PostgreSQL, Redis",
            "Tools": "Docker, Git, Maven, JUnit 5, Testcontainers, Linux",
        },
        "education": [("B.Tech Computer Science", "JNTU Hyderabad", "2022 – 2026", "CGPA 8.4/10")],
        "extras": ["Oracle Certified Associate, Java SE 17", "3-star CodeChef (1720)"],
    },
    {
        "file": "rohan-gupta-ml-engineer",
        "name": "Rohan Gupta",
        "headline": "Machine Learning · PyTorch · Recommender Systems",
        "contact": "Kanpur · +91 90000 10005 · rohan.gupta@example.com · github.com/rohan-gupta-ml",
        "summary": "Mathematics and Computing student focused on ranking and recommendation models, from "
                   "feature pipelines to offline evaluation.",
        "experience": [
            ("Machine Learning Intern", "StreamVeda (OTT)", "May 2025 – Dec 2025", [
                "Trained a two-tower retrieval model in PyTorch on 50M watch events; recall@50 improved 11% over the baseline.",
                "Built Spark feature pipelines on Databricks for 30 user and title features.",
                "Designed the A/B test for the new home row; it lifted watch time per user by 3.2%.",
            ]),
        ],
        "projects": [
            ("Learning-to-Rank for News", "github.com/rohan-gupta-ml/news-ltr", [
                "LightGBM LambdaMART ranker; NDCG@10 of 0.47 on the MIND dataset. Experiments tracked in MLflow.",
            ]),
            ("Kaggle: H&M Recommendations", "github.com/rohan-gupta-ml/hm-recs", [
                "Top 4% (silver medal) with a candidate generation plus re-ranking pipeline.",
            ]),
        ],
        "skills": {
            "ML": "PyTorch, TensorFlow, scikit-learn, LightGBM, recommender systems, learning to rank",
            "Data": "Python, SQL, Spark, Databricks, Pandas",
            "MLOps": "MLflow, Docker, Kubernetes (basics), Git",
            "Maths": "Probability, statistics, hypothesis testing, linear algebra",
        },
        "education": [("Integrated M.Sc. Mathematics and Computing", "IIT Kanpur", "2021 – 2026", "CPI 8.8/10")],
        "extras": ["Paper: 'Cold-start re-ranking with side information', student workshop, CODS-COMAD 2025"],
    },
    {
        "file": "ananya-krishnan-product-analyst",
        "name": "Ananya Krishnan",
        "headline": "Product Analyst · SQL · Experiments · Mixpanel",
        "contact": "Chennai · +91 90000 10006 · ananya.k@example.com · github.com/ananya-k-analytics",
        "summary": "Economics graduate who connects product metrics to decisions. Comfortable with SQL, "
                   "experiments and talking to PMs.",
        "experience": [
            ("Product Analyst Intern", "Rangoli (social commerce app)", "Jan 2026 – Jun 2026", [
                "Defined the activation metric (3 orders in 14 days) now on the leadership dashboard.",
                "Ran funnel analysis in Mixpanel and SQL; found a payment step losing 18% of users, fixed in the next sprint.",
                "Analysed 6 product experiments and wrote decision memos for the PM team.",
            ]),
            ("Research Assistant", "Department of Economics, Stella Maris College", "Jul 2024 – Dec 2025", [
                "Cleaned and analysed survey data from 2,000 households in R and Excel.",
            ]),
        ],
        "projects": [
            ("Swiggy vs Zomato Pricing Study", "github.com/ananya-k-analytics/delivery-pricing", [
                "Scraped 5,000 menu prices and tested surge pricing differences with regression.",
            ]),
        ],
        "skills": {
            "Analytics": "SQL, Excel, R, Python (Pandas), A/B testing, cohort and funnel analysis",
            "Product": "Mixpanel, Amplitude, Google Analytics 4, Looker Studio",
            "Communication": "Decision memos, stakeholder presentations",
        },
        "education": [("B.A. Economics (Honours)", "Stella Maris College, Chennai", "2021 – 2024", "First class"),
                      ("PG Diploma, Business Analytics", "Great Lakes Institute of Management", "2024 – 2025", "")],
        "extras": ["Winner, Flipkart Product Case Challenge, 2025"],
    },
    {
        "file": "vihaan-joshi-devops",
        "name": "Vihaan Joshi",
        "headline": "Cloud & DevOps · AWS · Terraform · Kubernetes",
        "contact": "Ahmedabad · +91 90000 10007 · vihaan.joshi@example.com · github.com/vihaan-joshi-ops",
        "summary": "Electronics student turned cloud engineer. Automates infrastructure so deploys are boring.",
        "experience": [
            ("DevOps Intern", "Tarang Health (health-tech)", "Jun 2025 – Dec 2025", [
                "Wrote Terraform for 3 AWS environments (VPC, EKS, RDS); new environment setup went from 2 days to 40 minutes.",
                "Built GitHub Actions pipelines with tests, image scans and blue-green deploys for 6 services.",
                "Added Prometheus and Grafana alerts; mean time to detect incidents fell from 25 to 4 minutes.",
                "Wrote runbooks for the 5 most common alerts so on-call engineers could resolve them without escalation.",
            ]),
        ],
        "projects": [
            ("Home Lab Kubernetes", "github.com/vihaan-joshi-ops/homelab", [
                "3-node k3s cluster on Raspberry Pis running Argo CD, cert-manager and Loki.",
            ]),
        ],
        "skills": {
            "Cloud": "AWS (EC2, EKS, RDS, S3, IAM, CloudWatch), basic GCP",
            "Infra": "Terraform, Kubernetes, Helm, Docker, Argo CD, Ansible",
            "CI/CD and observability": "GitHub Actions, Jenkins, Prometheus, Grafana",
            "Scripting": "Bash, Python, Linux administration",
        },
        "education": [("B.E. Electronics and Communication", "Gujarat Technological University", "2022 – 2026",
                       "CGPA 7.9/10")],
        "extras": ["AWS Certified Solutions Architect – Associate, 2025", "Certified Kubernetes Administrator (CKA), 2026"],
    },
    {
        "file": "ishita-banerjee-android",
        "format": "docx",
        "name": "Ishita Banerjee",
        "headline": "Android Developer · Kotlin · Jetpack Compose",
        "contact": "Kolkata · +91 90000 10008 · ishita.b@example.com · github.com/ishita-codes-android",
        "summary": "Android developer with 2 apps on the Play Store and 25,000+ installs between them.",
        "experience": [
            ("Android Intern", "Yatri Rides (mobility)", "Jan 2026 – Jun 2026", [
                "Rebuilt the ride history screen in Jetpack Compose with MVVM; crash-free sessions rose to 99.6%.",
                "Added offline caching with Room so trips load without network.",
                "Shipped push notifications for driver arrival with Firebase Cloud Messaging; 2-star reviews about missed pickups fell by half.",
            ]),
        ],
        "projects": [
            ("PocketPG", "github.com/ishita-codes-android/pocketpg", [
                "Kotlin app to find paying-guest rooms near colleges; 18,000 installs, 4.5 rating on Play Store.",
                "Firebase Auth, Firestore and Cloud Messaging; Hilt for dependency injection.",
            ]),
            ("Bus Tracker Kolkata", "github.com/ishita-codes-android/bus-tracker", [
                "Live bus positions on Google Maps SDK with Retrofit and Coroutines; 7,000 installs.",
            ]),
        ],
        "skills": {
            "Android": "Kotlin, Java, Jetpack Compose, MVVM, Room, Retrofit, Coroutines, Flow, Hilt",
            "Backend": "Firebase (Auth, Firestore, FCM), REST APIs",
            "Tools": "Android Studio, Git, Gradle, Play Console",
        },
        "education": [("B.Tech Computer Science", "Heritage Institute of Technology, Kolkata", "2022 – 2026",
                       "CGPA 8.0/10")],
        "extras": ["Google Developer Student Club lead, 2024 – 2025"],
    },
    {
        "file": "arjun-nair-fullstack",
        "format": "docx",
        "name": "Arjun Nair",
        "headline": "Full-Stack Developer · MERN",
        "contact": "Kochi · +91 90000 10009 · arjun.nair@example.com · github.com/arjun-nair-mern",
        "summary": "Full-stack developer interested in web apps.",
        "experience": [
            ("Web Development Intern", "Local digital agency", "Jun 2025 – Aug 2025", [
                "Worked on websites for clients.",
                "Made APIs using Node and Express.",
                "Helped the team with bug fixing.",
            ]),
        ],
        "projects": [
            ("E-commerce Website", "github.com/arjun-nair-mern/shop", [
                "Made an e-commerce website using MongoDB, Express, React and Node.",
                "Added login and cart.",
            ]),
            ("Chat App", "github.com/arjun-nair-mern/chat", [
                "Real-time chat app using Socket.io.",
            ]),
        ],
        "skills": {
            "Web": "JavaScript, React, Node.js, Express, MongoDB, HTML, CSS, Bootstrap",
            "Tools": "Git, Postman, VS Code",
        },
        "education": [("B.Tech Computer Science", "Model Engineering College, Kochi", "2022 – 2026", "CGPA 7.2/10")],
        "extras": ["Completed a 6-month full-stack web development course"],
    },
    {
        "file": "meera-pillai-cybersecurity",
        "name": "Meera Pillai",
        "headline": "Security Analyst · Network Security · CTF Player",
        "contact": "Thiruvananthapuram · +91 90000 10010 · meera.pillai@example.com · github.com/meera-pillai-sec",
        "summary": "Security-minded CS student. Finds problems before attackers do, and writes them up clearly.",
        "experience": [
            ("Security Intern", "Kavach SOC Services", "Jan 2026 – Jun 2026", [
                "Triaged 600+ SIEM alerts in Splunk and wrote 12 new detection rules that cut false positives by 30%.",
                "Ran internal vulnerability scans with Nessus and tracked 85 findings to closure.",
            ]),
        ],
        "projects": [
            ("Web App Pentest Lab", "github.com/meera-pillai-sec/pentest-lab", [
                "Found and documented OWASP Top 10 issues (SQL injection, XSS, IDOR) in 5 deliberately vulnerable apps using Burp Suite.",
            ]),
            ("Phishing URL Detector", "github.com/meera-pillai-sec/phish-detect", [
                "Python and scikit-learn classifier with 96% precision on 20,000 URLs.",
            ]),
        ],
        "skills": {
            "Security": "Network security, OWASP Top 10, incident triage, threat hunting, vulnerability management",
            "Tools": "Wireshark, Nmap, Burp Suite, Metasploit, Splunk, Nessus",
            "Programming": "Python, Bash, SQL, Linux",
        },
        "education": [("B.Tech Computer Science", "College of Engineering Trivandrum", "2022 – 2026", "CGPA 8.5/10")],
        "extras": ["CompTIA Security+, 2025", "Top 50 of 1,800 teams, InCTF 2025",
                   "Responsible disclosure: 2 acknowledged bugs in university web portals"],
    },
]


# ---------- a bigger generated cohort for demos ----------

FIRST_NAMES = (
    "Aditi", "Rahul", "Sana", "Karan", "Pooja", "Nikhil", "Riya", "Siddharth", "Tanvi", "Yash",
    "Kavya", "Omkar", "Nisha", "Harsh", "Zara", "Manav", "Divya", "Pranav", "Ira", "Varun",
    "Shreya", "Aman", "Mitali", "Kunal", "Anjali", "Dev", "Simran", "Aryan", "Lavanya", "Ritesh",
    "Neha", "Farhan", "Gauri", "Ishaan", "Payal", "Tejas", "Bhavna", "Rohit", "Sakshi", "Vivek",
    "Aisha", "Chirag", "Esha", "Jay", "Komal", "Mohit", "Naina", "Parth", "Ruchi", "Suraj",
)
LAST_NAMES = (
    "Sharma", "Verma", "Patel", "Rao", "Nair", "Das", "Kulkarni", "Menon", "Bose", "Chopra",
    "Gill", "Desai", "Pandey", "Shetty", "Kapoor", "Saxena", "Pillai", "Mishra", "Bhat", "Sinha",
)
# A realistic class: most applicants are decent, a few are strong, a couple are weak.
LEVELS = ("strong", "strong", "solid", "solid", "good", "good", "medium", "weak")
VARIANTS_PER_ARCHETYPE = len(LEVELS)


def _trim(text: str, keep: float, rng) -> str:
    """Keep roughly `keep` of the comma-separated items in a skills line."""
    items = [i.strip() for i in text.split(",")]
    count = max(1, round(len(items) * keep))
    return ", ".join(sorted(rng.sample(items, count), key=items.index))


def _variant(base: dict, level: str, first: str, last: str, rng) -> dict:
    # Stable username from the name, so tweaking the variation never renames a student.
    handle = f"{first}-{last}-{zlib.crc32(f'{first}{last}'.encode()) % 90 + 10}".lower()
    keep_bullets = {"strong": 99, "solid": 99, "good": 2, "medium": 1, "weak": 0}[level]
    keep_skills = {"strong": 1.0, "solid": 0.85, "good": 0.75, "medium": 0.6, "weak": 0.35}[level]
    # Natural variation so two students at the same level don't score identically.
    keep_skills = max(0.2, keep_skills - rng.uniform(0, 0.25))
    experience = [] if level == "weak" else [
        (t, o, d, rng.sample(b, max(1, min(len(b), keep_bullets) - rng.randint(0, 1))))
        for t, o, d, b in base["experience"]
    ]
    projects = rng.sample(base["projects"], min(len(base["projects"]), rng.choice((1, 2)) if level != "weak" else 1))
    projects = [(n, link.replace(link.split("/")[1], handle), b[:max(1, keep_bullets)]) for n, link, b in projects]
    return base | {
        "file": f"{first}-{last}".lower(),
        "name": f"{first} {last}",
        "contact": f"{base['contact'].split(' · ')[0]} · +91 90000 2{rng.randint(1000, 9999)} · "
                   f"{first.lower()}.{last.lower()}@example.com · github.com/{handle}",
        "summary": base["summary"] if experience else
                   f"Final-year student looking for {base['headline'].split(' · ')[0]} roles. Learning by building projects.",
        "experience": experience,
        "projects": projects,
        "skills": {k: _trim(v, keep_skills, rng) for k, v in base["skills"].items()},
        "extras": base["extras"][:1] if level in ("strong", "solid") else [],
    }


def generated_cohort(seed: int = 2026) -> list[dict]:
    """Eighty extra fictional students: eight per archetype, mostly decent, a few strong or weak."""
    import itertools
    import random

    rng = random.Random(seed)
    pairs = list(itertools.product(FIRST_NAMES, LAST_NAMES))
    rng.shuffle(pairs)
    names = iter(pairs)
    cohort = []
    for base in RESUMES:
        for level in LEVELS:
            first, last = next(names)
            cohort.append(_variant(base, level, first, last, rng))
    return cohort


def to_text(r: dict) -> str:
    """The same resume as plain text, the way a PDF reads after extraction."""
    lines = [r["name"], r["headline"], r["contact"], "SUMMARY", r["summary"]]
    if r["experience"]:
        lines.append("EXPERIENCE")
        for title, org, dates, bullets in r["experience"]:
            lines += [f"{title} · {org}", dates, *[f"• {b}" for b in bullets]]
    lines.append("PROJECTS")
    for name, link, bullets in r["projects"]:
        lines += [name, link, *[f"• {b}" for b in bullets]]
    lines.append("SKILLS")
    lines += [f"{k}: {v}" for k, v in r["skills"].items()]
    lines.append("EDUCATION")
    lines += [f"{deg} · {school} · {dates}" + (f" · {extra}" if extra else "")
              for deg, school, dates, extra in r["education"]]
    if r["extras"]:
        lines.append("CERTIFICATIONS AND ACHIEVEMENTS")
        lines += [f"• {x}" for x in r["extras"]]
    return "\n".join(lines)
