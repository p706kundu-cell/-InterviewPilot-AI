import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# OpenAI is optional.
# If API credits are available, we can use it.
# If not, the local interviewer below keeps the demo working.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# OPTIONAL OPENAI CLIENT
# ---------------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

client = None

if OpenAI and api_key:
    client = OpenAI(api_key=api_key)


# ---------------------------------------------------------
# APP
# ---------------------------------------------------------

app = FastAPI(title="InterviewPilot AI")


# ---------------------------------------------------------
# IN-MEMORY INTERVIEW SESSIONS
# ---------------------------------------------------------

sessions: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------------

class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[dict] = None
    message: Optional[str] = None


# ---------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------

def load_json_file(filename: str):
    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


CURRICULUM = load_json_file("curriculum.json")


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "InterviewPilot AI is running!"
    }


# ---------------------------------------------------------
# LOCAL QUESTION BANK
# ---------------------------------------------------------

QUESTION_BANK = [
    {
        "topic": "Embeddings",
        "keywords": ["embedding", "vector", "semantic"],
        "weak": "What is an embedding, and why is it useful for representing text?",
        "strong": "How would you choose an embedding model for a production semantic-search system?"
    },
    {
        "topic": "Vector Databases",
        "keywords": ["vector", "database", "similarity", "index"],
        "weak": "What problem does a vector database solve in an AI application?",
        "strong": "How would you design indexing and similarity search for a large-scale vector database?"
    },
    {
        "topic": "RAG",
        "keywords": ["rag", "retrieval", "generation", "knowledge", "grounded"],
        "weak": "What is RAG and why would you use it instead of relying only on an LLM?",
        "strong": "How would you reduce hallucinations and improve retrieval quality in a production RAG pipeline?"
    },
    {
        "topic": "Prompt Engineering",
        "keywords": ["prompt", "instruction", "system", "few-shot"],
        "weak": "What makes a good prompt for an AI application?",
        "strong": "How would you design and evaluate prompts for a production LLM workflow?"
    },
    {
        "topic": "APIs",
        "keywords": ["api", "rest", "endpoint", "backend"],
        "weak": "How would you design an API endpoint for an AI-powered application?",
        "strong": "How would you make an AI API reliable, scalable, and observable in production?"
    },
    {
        "topic": "Multi-Agent Systems",
        "keywords": ["agent", "multi-agent", "orchestration"],
        "weak": "What is a multi-agent AI system?",
        "strong": "How would you decide which tasks should be handled by separate agents in a multi-agent architecture?"
    },
    {
        "topic": "MCP",
        "keywords": ["mcp", "model context protocol", "tool"],
        "weak": "What problem does Model Context Protocol solve?",
        "strong": "How would you use MCP to safely connect an AI model with external tools or data sources?"
    },
    {
        "topic": "Docker",
        "keywords": ["docker", "container", "image"],
        "weak": "Why would you use Docker for deploying an AI application?",
        "strong": "How would you containerize and deploy an AI backend reliably?"
    },
    {
        "topic": "Kubernetes",
        "keywords": ["kubernetes", "k8s", "pod", "deployment"],
        "weak": "What problem does Kubernetes solve?",
        "strong": "How would you scale an AI inference service using Kubernetes?"
    },
    {
        "topic": "Observability",
        "keywords": ["monitoring", "logging", "observability", "metrics"],
        "weak": "Why is observability important for an AI application?",
        "strong": "Which metrics would you monitor to detect quality, latency, and reliability problems in an AI application?"
    }
]


# ---------------------------------------------------------
# LOCAL ADAPTIVE ENGINE
# ---------------------------------------------------------

def local_question(session: Dict[str, Any]) -> str:

    candidate = session["candidate"]
    messages = session["messages"]

    candidate_role = candidate.get(
        "jobRole",
        "technical professional"
    )

    # Find topics already used
    used_topics = set()

    for message in messages:
        if message["role"] == "interviewer":
            text = message["content"].lower()

            for q in QUESTION_BANK:
                if q["topic"].lower() in text:
                    used_topics.add(q["topic"])

    # Select next unused topic
    available = [
        q for q in QUESTION_BANK
        if q["topic"] not in used_topics
    ]

    if not available:
        available = QUESTION_BANK

    question = available[0]

    # Difficulty based on previous answer quality
    if messages:

        last_answer = ""

        for message in reversed(messages):
            if message["role"] == "candidate":
                last_answer = message["content"].lower()
                break

        technical_words = [
            "because",
            "architecture",
            "trade-off",
            "latency",
            "scalability",
            "security",
            "index",
            "retrieval",
            "embedding",
            "api",
            "database",
            "deployment",
            "monitoring"
        ]

        score = sum(
            1 for word in technical_words
            if word in last_answer
        )

        if len(last_answer) > 150 and score >= 2:
            question_text = question["strong"]
        else:
            question_text = question["weak"]

    else:
        question_text = question["weak"]

    return (
        f"Considering your experience as a {candidate_role}, "
        f"{question_text}"
    )


# ---------------------------------------------------------
# LOCAL FEEDBACK ENGINE
# ---------------------------------------------------------

def generate_local_feedback(session: Dict[str, Any]) -> dict:

    candidate = session["candidate"]

    answers = [
        message["content"]
        for message in session["messages"]
        if message["role"] == "candidate"
    ]

    if not answers:
        return {
            "summary": "The interview was completed with limited candidate responses.",
            "strengths": [],
            "gaps": [
                "Provide detailed technical explanations."
            ],
            "next": [
                "Practice explaining technical concepts with concrete examples."
            ]
        }

    average_length = sum(
        len(answer.split())
        for answer in answers
    ) / len(answers)

    technical_terms = [
        "architecture",
        "api",
        "database",
        "vector",
        "embedding",
        "retrieval",
        "scalability",
        "security",
        "latency",
        "docker",
        "kubernetes",
        "monitoring",
        "model",
        "prompt"
    ]

    technical_hits = 0

    for answer in answers:
        text = answer.lower()

        technical_hits += sum(
            1 for term in technical_terms
            if term in text
        )

    strengths = []

    if average_length >= 40:
        strengths.append(
            "Provides reasonably detailed technical explanations."
        )

    if technical_hits >= 5:
        strengths.append(
            "Demonstrates familiarity with relevant technical concepts."
        )

    if not strengths:
        strengths.append(
            "Engaged consistently with the interview questions."
        )

    gaps = []

    if average_length < 25:
        gaps.append(
            "Give more detailed explanations and supporting examples."
        )

    if technical_hits < 5:
        gaps.append(
            "Strengthen explanations of architecture and implementation trade-offs."
        )

    if not gaps:
        gaps.append(
            "Continue improving depth and precision in system-design explanations."
        )

    next_steps = [
        "Practice explaining technical decisions using concrete real-world examples.",
        "Review system design, scalability, and production AI architecture."
    ]

    return {
        "summary": (
            f"{candidate.get('name', 'The candidate')} completed "
            "the adaptive technical interview."
        ),
        "strengths": strengths,
        "gaps": gaps,
        "next": next_steps
    }


# ---------------------------------------------------------
# OPTIONAL OPENAI QUESTION
# ---------------------------------------------------------

def ask_openai(prompt: str) -> Optional[str]:

    if not client:
        return None

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        return response.output_text.strip()

    except Exception:
        # If the API has no credits, quota, or another API problem,
        # automatically fall back to the local interviewer.
        return None


# ---------------------------------------------------------
# INTERVIEW ENDPOINT
# ---------------------------------------------------------

@app.post("/api/interview")
def interview(request: InterviewRequest):

    session_id = request.sessionId

    # =====================================================
    # START INTERVIEW
    # =====================================================

    if session_id not in sessions:

        if not request.candidate:
            return {
                "reply": "Candidate information is required to start the interview.",
                "done": False
            }

        sessions[session_id] = {
            "candidate": request.candidate,
            "messages": [],
            "question_count": 0
        }

        candidate = request.candidate

        candidate_name = candidate.get(
            "name",
            "Candidate"
        )

        prompt = f"""
You are InterviewPilot AI, an adaptive technical interviewer.

Candidate:
{json.dumps(candidate, indent=2)}

Curriculum:
{json.dumps(CURRICULUM, indent=2)[:12000]}

Start the technical interview.

Rules:
- Ask ONE question only.
- Base the question on the candidate's background and curriculum.
- Do not ask generic questions.
- Start at an appropriate difficulty.
- Be conversational.
- Do not provide the answer.

Return only the interviewer's question.
"""

        # Try OpenAI first.
        question = ask_openai(prompt)

        # If OpenAI is unavailable/no credits, use local engine.
        if not question:
            question = local_question(
                sessions[session_id]
            )

        sessions[session_id]["messages"].append({
            "role": "interviewer",
            "content": question
        })

        return {
            "reply": f"Welcome {candidate_name}. {question}",
            "done": False
        }

    # =====================================================
    # CONTINUE INTERVIEW
    # =====================================================

    if request.message:

        session = sessions[session_id]

        session["messages"].append({
            "role": "candidate",
            "content": request.message
        })

        session["question_count"] += 1

        # =================================================
        # FINAL FEEDBACK AFTER 8 ANSWERS
        # =================================================

        if session["question_count"] >= 8:

            conversation = "\n".join(
                f"{message['role']}: {message['content']}"
                for message in session["messages"]
            )

            feedback_prompt = f"""
You are an expert technical interviewer.

Candidate:
{json.dumps(session["candidate"], indent=2)}

Interview conversation:
{conversation}

Evaluate the candidate.

Return ONLY valid JSON in exactly this structure:

{{
    "summary": "short overall assessment",
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "gaps": [
        "gap 1",
        "gap 2"
    ],
    "next": [
        "recommended next step 1",
        "recommended next step 2"
    ]
}}

Keep every point concise and actionable.
"""

            feedback = None

            # Try OpenAI feedback first.
            feedback_text = ask_openai(feedback_prompt)

            if feedback_text:

                try:
                    feedback = json.loads(feedback_text)

                except json.JSONDecodeError:
                    feedback = None

            # Local fallback.
            if feedback is None:
                feedback = generate_local_feedback(session)

            return {
                "reply": "Interview completed.",
                "done": True,
                "feedback": feedback
            }

        # =================================================
        # GENERATE NEXT ADAPTIVE QUESTION
        # =================================================

        conversation = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in session["messages"]
        )

        question_prompt = f"""
You are InterviewPilot AI, an adaptive technical interviewer.

Candidate:
{json.dumps(session["candidate"], indent=2)}

Curriculum:
{json.dumps(CURRICULUM, indent=2)[:12000]}

Interview so far:
{conversation}

The candidate has just answered the latest question.

Generate the NEXT technical interview question.

Rules:
- Ask exactly ONE question.
- Adapt difficulty based on the candidate's latest answer.
- If the answer was weak, ask a clarifying/fundamental follow-up.
- If the answer was strong, increase the difficulty.
- Cover different relevant curriculum topics.
- Avoid repeating previous questions.
- Do not give the answer.
- Keep it conversational.

Return ONLY the question.
"""

        # Try OpenAI.
        next_question = ask_openai(question_prompt)

        # Local fallback.
        if not next_question:
            next_question = local_question(session)

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
        "reply": "Please provide your interview response.",
        "done": False
    }