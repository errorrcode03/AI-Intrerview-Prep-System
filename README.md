# 🚀 AI Interview Preparation System

An end-to-end, AI-powered interview preparation platform built to help candidates ace HR, Technical, and DSA coding interviews. The system leverages Google's Gemini 3.5 Flash LLM to conduct real-time voice and text interviews, analyze resumes, evaluate coding logic, and track performance over time.

---

## ✨ Features

- **📄 Resume Analyzer**: Upload a PDF resume to instantly extract key skills and generate an ATS compatibility score. The AI uses this data to tailor interview questions specifically to your background.
- **💬 AI Interview Engine**: Participate in stateful, multi-turn HR and Technical interviews. The AI dynamically generates follow-up questions, grades your answers on a 1-10 scale, and provides constructive feedback.
- **🎙️ Voice Integration**: Built using native Web Speech APIs (`SpeechRecognition` & `SpeechSynthesis`). Speak your answers out loud for automatic transcription, and listen as the AI interviewer reads its responses back to you.
- **💻 DSA Coding Environment**: A LeetCode-style split-pane IDE integrated with the **Monaco Editor** (supporting Python, C++, Java, and JavaScript). Submit your code to have Gemini analyze your logic, determine the Big-O Time Complexity, and detect edge case bugs.
- **📊 Personalized Learning Dashboard**: A centralized analytics hub powered by **Chart.js**. Track your average interview scores and coding success rates over time, and receive an AI-generated roadmap highlighting your "Weak Topics".

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism UI), Vanilla JavaScript, Chart.js, Monaco Editor.
- **Backend**: Python 3, FastAPI, Uvicorn.
- **Database**: SQLite (SQLAlchemy ORM).
- **AI Models**: Google Gemini API (`gemini-3.5-flash`).
- **File Parsing**: PyPDF2.

---

## ⚙️ Local Setup & Installation

### Prerequisites
- Python 3.10+ installed on your machine.
- A free Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

### 1. Clone & Configure
1. Clone the repository to your local machine.
2. Create a `.env` file in the root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### 2. Backend Setup
1. Open a terminal and navigate to the project directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *(The SQLite database `interview.db` will be automatically generated upon startup).*

### 3. Frontend Setup
1. The frontend uses Vanilla HTML/JS and relies on relative paths. 
2. Simply open `frontend/index.html` in your web browser (Google Chrome or Microsoft Edge recommended for full Voice API support) to start using the app!
3. Alternatively, you can use a simple live server (like the VS Code Live Server extension) to serve the `frontend/` directory.

---

## 📂 Project Structure

```text
├── backend/
│   ├── main.py                # FastAPI application & endpoints
│   ├── models.py              # SQLAlchemy database schemas
│   ├── schemas.py             # Pydantic validation models
│   ├── requirements.txt       # Python dependencies
│   └── services/
│       ├── ai_engine.py       # Resume parsing & ATS scoring
│       ├── interview_engine.py# Conversational chat logic
│       └── coding_engine.py   # DSA simulation & Time Complexity eval
├── frontend/
│   ├── index.html             # Landing page & Resume upload
│   ├── interview.html         # Chat UI with Voice Integration
│   ├── coding.html            # Monaco Editor IDE UI
│   ├── dashboard.html         # Analytics & Charts UI
│   ├── css/                   # Stylesheets
│   └── js/                    # Client-side logic & API calls
└── .env                       # Environment variables
```

## 📝 License
This project is for educational and portfolio purposes. Feel free to fork, modify, and expand upon it!
