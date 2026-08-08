# AI Usage Log — InterviewPilot AI

## Project
InterviewPilot AI — Adaptive AI-powered technical interview platform

## AI tools used
- ChatGPT — used for project planning, debugging, code assistance, architecture decisions, Git/GitHub guidance, and troubleshooting.
- OpenAI API — integrated into the application for optional AI-generated interview questions and final candidate feedback.

## Development prompts / assistance

### 1. Project architecture
Used AI assistance to plan an adaptive technical interview system with:
- FastAPI backend
- Interactive frontend
- Candidate profile collection
- Adaptive technical questions
- Eight-question interview flow
- Automated final feedback
- Local fallback when the OpenAI API is unavailable

### 2. Adaptive interview logic
AI assistance was used to design logic that:
- evaluates the candidate's previous answer
- adjusts question difficulty
- avoids repeating topics where possible
- covers multiple technical areas
- completes the interview after eight answers

### 3. OpenAI integration
AI assistance was used to integrate the OpenAI API for:
- generating interview questions
- adapting questions based on the conversation
- generating structured final feedback

The application also contains a local fallback interviewer so that the core demonstration can continue when an API key, quota, or network connection is unavailable.

### 4. Backend development
AI assistance was used while developing and debugging:
- FastAPI endpoints
- Pydantic request models
- JSON data loading
- interview session management
- error handling
- CORS configuration
- local development with Uvicorn

### 5. Frontend development
AI assistance was used to build and troubleshoot:
- candidate input form
- interview question display
- answer submission
- eight-question progress flow
- final feedback screen
- frontend/backend API communication

### 6. Git and GitHub
AI assistance was used for:
- Git repository setup
- branch management
- GitHub authentication
- committing project changes
- pushing the project to a public GitHub repository

## Human contribution

The project was developed and tested by the project participant during the hackathon. AI assistance was used as a development aid for planning, implementation, debugging, and documentation. The resulting application was locally tested end-to-end, including candidate input, adaptive questions, eight responses, and final feedback.

## Important implementation note

The application supports two question/feedback paths:

1. OpenAI-powered generation when an API key is available.
2. A local adaptive question and feedback engine as a fallback.

This allows the core interview demonstration to remain functional without depending entirely on external API availability.