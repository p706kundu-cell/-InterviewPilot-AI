import os
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


# =========================================================
# OPTIONAL OPENAI
# =========================================================

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


# =========================================================
# OPENAI CLIENT
# =========================================================

api_key = os.getenv("OPENAI_API_KEY")

client = None

if OpenAI and api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="InterviewPilot AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# INTERVIEW SESSIONS
# =========================================================

sessions: Dict[str, Dict[str, Any]] = {}


# =========================================================
# REQUEST MODEL
# =========================================================

class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[dict] = None
    message: Optional[str] = None


# =========================================================
# LOAD JSON
# =========================================================

def load_json_file(filename: str):

    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


try:
    CURRICULUM = load_json_file("curriculum.json")
except Exception:
    CURRICULUM = {}


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/")
def home():

    frontend_path = BASE_DIR / "frontend" / "index.html"

    return FileResponse(str(frontend_path))


# =========================================================
# ROLE-SPECIFIC LOCAL QUESTION TOPICS
# =========================================================

ROLE_TOPICS = {

    "java": [
        "Core Java and OOP",
        "Java Collections",
        "Exception Handling",
        "Multithreading",
        "Java Memory Management",
        "Java 8+ Features",
        "JDBC and Databases",
        "Spring Boot and REST APIs",
        "Design Patterns",
        "Java Performance"
    ],

    "python": [
        "Python Fundamentals",
        "Object-Oriented Programming",
        "Python Collections",
        "Exception Handling",
        "Decorators and Generators",
        "Concurrency",
        "APIs",
        "Databases",
        "Testing",
        "Python Performance"
    ],

    "javascript": [
        "JavaScript Fundamentals",
        "DOM and Browser APIs",
        "Asynchronous JavaScript",
        "Promises and Async Await",
        "Closures",
        "JavaScript Objects",
        "Frontend Architecture",
        "APIs",
        "Performance",
        "Security"
    ],

    "frontend": [
        "HTML and CSS",
        "JavaScript",
        "Responsive Design",
        "DOM",
        "Browser APIs",
        "State Management",
        "Frontend Architecture",
        "Accessibility",
        "Performance",
        "Web Security"
    ],

    "backend": [
        "Backend Architecture",
        "REST APIs",
        "Databases",
        "Authentication",
        "Caching",
        "Scalability",
        "Concurrency",
        "Error Handling",
        "Security",
        "Monitoring"
    ],

    "full stack": [
        "Frontend Architecture",
        "Backend Architecture",
        "REST APIs",
        "Databases",
        "Authentication",
        "State Management",
        "Caching",
        "Scalability",
        "Security",
        "Deployment"
    ],

    "data analyst": [
        "SQL",
        "Data Cleaning",
        "Statistics",
        "Data Visualization",
        "Python and Pandas",
        "Excel",
        "Data Interpretation",
        "Business Metrics",
        "Data Quality",
        "Analytical Problem Solving"
    ],

    "data scientist": [
        "Statistics",
        "Machine Learning",
        "Feature Engineering",
        "Model Evaluation",
        "Data Cleaning",
        "Python",
        "SQL",
        "Experimentation",
        "Model Deployment",
        "Data Science Projects"
    ],

    "machine learning": [
        "Machine Learning Fundamentals",
        "Supervised Learning",
        "Unsupervised Learning",
        "Feature Engineering",
        "Model Evaluation",
        "Overfitting",
        "Model Selection",
        "Deep Learning",
        "Model Deployment",
        "ML System Design"
    ],

    "ai": [
        "LLMs",
        "Embeddings",
        "RAG",
        "Vector Databases",
        "Prompt Engineering",
        "AI Agents",
        "Model Evaluation",
        "AI Security",
        "AI Deployment",
        "AI System Design"
    ],

    "devops": [
        "CI/CD",
        "Docker",
        "Kubernetes",
        "Linux",
        "Cloud Infrastructure",
        "Monitoring",
        "Networking",
        "Infrastructure as Code",
        "Security",
        "Deployment"
    ],

    "cloud": [
        "Cloud Fundamentals",
        "Compute",
        "Storage",
        "Networking",
        "Databases",
        "Security",
        "Scalability",
        "Monitoring",
        "Cost Optimization",
        "Cloud Architecture"
    ],

    "cybersecurity": [
        "Network Security",
        "Authentication",
        "Authorization",
        "Encryption",
        "Vulnerability Assessment",
        "Web Security",
        "Threat Modeling",
        "Incident Response",
        "Security Monitoring",
        "Security Architecture"
    ],

    "android": [
        "Android Fundamentals",
        "Kotlin/Java",
        "Activities and Fragments",
        "Android Lifecycle",
        "UI Development",
        "Networking",
        "Local Storage",
        "Architecture",
        "Performance",
        "Security"
    ],

    "ios": [
        "iOS Fundamentals",
        "Swift",
        "UIKit/SwiftUI",
        "Application Lifecycle",
        "Networking",
        "Persistence",
        "Architecture",
        "Performance",
        "Security",
        "Testing"
    ],

    "qa": [
        "Software Testing",
        "Unit Testing",
        "Integration Testing",
        "API Testing",
        "Automation",
        "Test Cases",
        "Regression Testing",
        "Performance Testing",
        "Bug Reporting",
        "CI/CD Testing"
    ],

    "database": [
        "SQL",
        "Database Design",
        "Normalization",
        "Indexes",
        "Transactions",
        "Concurrency",
        "Query Optimization",
        "Replication",
        "Backup and Recovery",
        "Database Security"
    ],

    "blockchain": [
        "Blockchain Fundamentals",
        "Cryptography",
        "Consensus",
        "Smart Contracts",
        "Ethereum",
        "Wallets",
        "Security",
        "Decentralization",
        "Scalability",
        "Blockchain Architecture"
    ]
}


# =========================================================
# GENERIC TOPICS FOR UNKNOWN ROLES
# =========================================================

GENERIC_TOPICS = [
    "Core Concepts",
    "Problem Solving",
    "Architecture",
    "APIs and Integration",
    "Databases and Data",
    "Security",
    "Scalability",
    "Testing",
    "Performance",
    "Production and Deployment"
]


# =========================================================
# ROLE DETECTION
# =========================================================

def get_role_topics(job_role: str):

    role = job_role.lower().strip()

    # Most specific matches first
    matches = []

    for key, topics in ROLE_TOPICS.items():

        if key in role:
            matches.append((len(key), topics))

    if matches:
        matches.sort(reverse=True, key=lambda item: item[0])
        return matches[0][1]

    # General technology keyword detection
    keyword_map = {
        "software": GENERIC_TOPICS,
        "engineer": GENERIC_TOPICS,
        "developer": GENERIC_TOPICS,
        "programming": GENERIC_TOPICS,
        "technology": GENERIC_TOPICS,
        "technical": GENERIC_TOPICS
    }

    for key, topics in keyword_map.items():

        if key in role:
            return topics

    return GENERIC_TOPICS


# =========================================================
# LOCAL QUESTION GENERATOR
# =========================================================

def generate_local_question(
    session: Dict[str, Any],
    topic: str
) -> str:

    candidate = session["candidate"]

    role = candidate.get(
        "jobRole",
        "technical professional"
    )

    experience = candidate.get(
        "experience",
        "not specified"
    )

    skills = candidate.get(
        "skills",
        "not specified"
    )

    # Question templates deliberately vary.
    templates = [

        f"For a {role} role, can you explain the fundamentals of {topic}?",

        f"Considering your experience as a {role}, how would you approach a real-world problem involving {topic}?",

        f"How would you use {topic} when working as a {role}?",

        f"What are the main challenges you would consider when working with {topic} as a {role}?",

        f"Can you give a practical example of how {topic} could be used in a {role} project?",

        f"How would you design or implement a solution involving {topic}?",

        f"What trade-offs would you consider when choosing an approach related to {topic}?",

        f"How would you troubleshoot a production issue related to {topic}?"
    ]

    question = random.choice(templates)

    return (
        f"Considering your experience as a {role} "
        f"({experience}) and your skills in {skills}, "
        f"{question}"
    )


# =========================================================
# LOCAL ADAPTIVE QUESTION
# =========================================================

def local_question(session: Dict[str, Any]) -> str:

    candidate = session["candidate"]

    job_role = candidate.get(
        "jobRole",
        "technical professional"
    )

    topics = get_role_topics(job_role)

    used_topics = session.get(
        "asked_topics",
        []
    )

    available_topics = [
        topic
        for topic in topics
        if topic not in used_topics
    ]

    # If all topics have been used, create another randomized
    # order rather than always starting from the first question.
    if not available_topics:
        available_topics = topics.copy()

        random.shuffle(available_topics)

    # Randomly select an unused topic.
    topic = random.choice(available_topics)

    session.setdefault(
        "asked_topics",
        []
    ).append(topic)

    question = generate_local_question(
        session,
        topic
    )

    return question


# =========================================================
# OPENAI QUESTION GENERATOR
# =========================================================

def ask_openai(prompt: str) -> Optional[str]:

    if not client:
        return None

    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        result = response.output_text.strip()

        if result:
            return result

    except Exception:
        pass

    return None


# =========================================================
# CHECK QUESTION DUPLICATION
# =========================================================

def question_already_asked(
    question: str,
    asked_questions: list
) -> bool:

    normalized = " ".join(
        question.lower().strip().split()
    )

    for old_question in asked_questions:

        old_normalized = " ".join(
            old_question.lower().strip().split()
        )

        if normalized == old_normalized:
            return True

    return False


# =========================================================
# GENERATE AI QUESTION
# =========================================================

def generate_ai_question(
    session: Dict[str, Any]
) -> Optional[str]:

    candidate = session["candidate"]

    asked_questions = session.get(
        "asked_questions",
        []
    )

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in session["messages"]
    )

    prompt = f"""
You are InterviewPilot AI, a professional adaptive technical interviewer.

Your job is to conduct a realistic technical interview.

CANDIDATE PROFILE:
{json.dumps(candidate, indent=2)}

TARGET JOB ROLE:
{candidate.get("jobRole", "technical professional")}

EXPERIENCE:
{candidate.get("experience", "not specified")}

SKILLS:
{candidate.get("skills", "not specified")}

QUESTIONS ALREADY ASKED:
{json.dumps(asked_questions, indent=2)}

INTERVIEW SO FAR:
{conversation}

QUESTION NUMBER:
{session.get("question_count", 0) + 1} of 8

IMPORTANT RULES:

1. The candidate's target job role is the PRIMARY domain.
2. Generate a question specifically relevant to that role.
3. Do NOT assume the candidate is an AI engineer unless they selected an AI-related role.
4. Do NOT repeat any previous question.
5. Do not ask a generic software-engineering question when a role-specific question is possible.
6. Consider the candidate's stated skills.
7. Consider the candidate's experience level.
8. Consider the candidate's previous answer.
9. If the previous answer was weak, ask a useful fundamental or clarifying question.
10. If the previous answer was strong, increase the difficulty.
11. Cover different technical areas throughout the interview.
12. Ask exactly ONE question.
13. Do not give the answer.
14. Do not number the question.
15. Return ONLY the question text.

Create the next question now.
"""

    question = ask_openai(prompt)

    if not question:
        return None

    # Remove accidental quotation marks.
    question = question.strip().strip('"')

    # Safety check against exact repetition.
    if question_already_asked(
        question,
        asked_questions
    ):
        return None

    return question


# =========================================================
# LOCAL FEEDBACK ENGINE
# =========================================================

def generate_local_feedback(
    session: Dict[str, Any]
) -> dict:

    candidate = session["candidate"]

    answers = [
        message["content"]
        for message in session["messages"]
        if message["role"] == "candidate"
    ]

    if not answers:

        return {
            "summary": (
                "The interview was completed with "
                "limited candidate responses."
            ),
            "strengths": [],
            "gaps": [
                "Provide detailed technical explanations."
            ],
            "next": [
                "Practice explaining technical concepts "
                "with concrete examples."
            ]
        }

    average_length = (
        sum(
            len(answer.split())
            for answer in answers
        )
        / len(answers)
    )

    technical_terms = [
        "architecture",
        "api",
        "database",
        "security",
        "scalability",
        "latency",
        "deployment",
        "testing",
        "performance",
        "monitoring",
        "design",
        "implementation",
        "framework",
        "algorithm",
        "data",
        "system"
    ]

    technical_hits = 0

    for answer in answers:

        text = answer.lower()

        technical_hits += sum(
            1
            for term in technical_terms
            if term in text
        )

    strengths = []

    if average_length >= 40:

        strengths.append(
            "Provides reasonably detailed technical explanations."
        )

    if technical_hits >= 5:

        strengths.append(
            "Demonstrates familiarity with relevant "
            "technical concepts."
        )

    if not strengths:

        strengths.append(
            "Engaged consistently with the interview questions."
        )

    gaps = []

    if average_length < 25:

        gaps.append(
            "Give more detailed explanations and "
            "supporting examples."
        )

    if technical_hits < 5:

        gaps.append(
            "Strengthen explanations of architecture, "
            "implementation, and technical trade-offs."
        )

    if not gaps:

        gaps.append(
            "Continue improving depth and precision "
            "in technical explanations."
        )

    role = candidate.get(
        "jobRole",
        "your target role"
    )

    next_steps = [
        f"Practice explaining real-world {role} technical decisions.",
        "Work on explaining trade-offs using concrete examples."
    ]

    return {
        "summary": (
            f"{candidate.get('name', 'The candidate')} completed "
            f"the adaptive {role} technical interview."
        ),
        "strengths": strengths,
        "gaps": gaps,
        "next": next_steps
    }


# =========================================================
# INTERVIEW ENDPOINT
# =========================================================

@app.post("/api/interview")
def interview(request: InterviewRequest):

    session_id = request.sessionId


    # =====================================================
    # START INTERVIEW
    # =====================================================

    if session_id not in sessions:

        if not request.candidate:

            return {
                "reply": (
                    "Candidate information is required "
                    "to start the interview."
                ),
                "done": False
            }

        sessions[session_id] = {

            "candidate": request.candidate,

            "messages": [],

            "question_count": 0,

            "asked_questions": [],

            "asked_topics": []
        }

        session = sessions[session_id]

        candidate = request.candidate

        candidate_name = candidate.get(
            "name",
            "Candidate"
        )


        # =================================================
        # FIRST AI QUESTION
        # =================================================

        question = generate_ai_question(
            session
        )


        # =================================================
        # LOCAL FALLBACK
        # =================================================

        if not question:

            question = local_question(
                session
            )


        session["asked_questions"].append(
            question
        )

        session["messages"].append({

            "role": "interviewer",

            "content": question
        })


        return {

            "reply": (
                f"Welcome {candidate_name}. "
                f"{question}"
            ),

            "done": False
        }


    # =====================================================
    # CONTINUE INTERVIEW
    # =====================================================

    if request.message:

        session = sessions[session_id]

        answer = request.message.strip()

        session["messages"].append({

            "role": "candidate",

            "content": answer
        })

        session["question_count"] += 1


        # =================================================
        # FINAL FEEDBACK AFTER 8 ANSWERS
        # =================================================

        if session["question_count"] >= 8:

            conversation = "\n".join(

                f"{message['role']}: "
                f"{message['content']}"

                for message in session["messages"]
            )


            feedback_prompt = f"""
You are an expert technical interviewer.

Evaluate this candidate's completed interview.

Candidate:
{json.dumps(session["candidate"], indent=2)}

Interview conversation:
{conversation}

Target role:
{session["candidate"].get("jobRole", "technical professional")}

Return ONLY valid JSON using exactly this structure:

{{
    "summary": "short overall assessment",
    "strengths": [
        "strength 1",
        "strength 2",
        "strength 3"
    ],
    "gaps": [
        "gap 1",
        "gap 2",
        "gap 3"
    ],
    "next": [
        "recommended next step 1",
        "recommended next step 2",
        "recommended next step 3"
    ]
}}

Make the feedback specific to the candidate's selected role.
Keep every point concise and actionable.
"""


            feedback = None

            feedback_text = ask_openai(
                feedback_prompt
            )


            if feedback_text:

                try:

                    feedback = json.loads(
                        feedback_text
                    )

                except json.JSONDecodeError:

                    feedback = None


            # Local fallback

            if feedback is None:

                feedback = generate_local_feedback(
                    session
                )


            return {

                "reply": "Interview completed.",

                "done": True,

                "feedback": feedback
            }


        # =================================================
        # GENERATE NEXT QUESTION
        # =================================================

        next_question = generate_ai_question(
            session
        )


        # =================================================
        # LOCAL FALLBACK
        # =================================================

        if not next_question:

            next_question = local_question(
                session
            )


        # =================================================
        # EXTRA DUPLICATE PROTECTION
        # =================================================

        attempts = 0

        while (
            question_already_asked(
                next_question,
                session["asked_questions"]
            )
            and attempts < 3
        ):

            next_question = local_question(
                session
            )

            attempts += 1


        session["asked_questions"].append(
            next_question
        )


        session["messages"].append({

            "role": "interviewer",

            "content": next_question
        })


        return {

            "reply": next_question,

            "done": False
        }


    # =====================================================
    # NO MESSAGE
    # =====================================================

    return {

        "reply": (
            "Please provide your interview response."
        ),

        "done": False
    }