from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
import os
import shutil
import PyPDF2
from .services import ai_engine, interview_engine, coding_engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview System API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Interview Preparation System API"}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In a real app, hash the password here
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password # Mock: storing plain text for prototype
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # In a real app, verify hashed password here
    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username
    }

@app.post("/upload_resume", response_model=schemas.ResumeResponse)
async def upload_resume(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported")
    
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Extract text from PDF
    parsed_text = ""
    try:
        if file.filename.endswith('.pdf'):
            with open(file_location, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        parsed_text += text + "\n"
        else:
            # For DOCX, we would use python-docx, but let's stick to simple text for now or just mock docx
            parsed_text = f"Mock parsed text from DOCX: {file.filename}"
    except Exception as e:
        print(f"Error parsing file: {e}")
        parsed_text = "Failed to parse document text."
    
    # Use Gemini AI integration to get ATS Score and Skills
    ai_result = ai_engine.analyze_resume(parsed_text)
    ats_score = ai_result.get("ats_score", 0)
    skills = ai_result.get("skills", [])

    db_resume = models.Resume(
        user_id=user_id,
        file_path=file_location,
        parsed_text=parsed_text,
        ats_score=ats_score,
        skills=skills
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return db_resume

@app.post("/start_interview")
async def start_interview(request: schemas.InterviewStartRequest, db: Session = Depends(get_db)):
    db_interview = models.Interview(
        user_id=request.user_id,
        interview_type=request.interview_type
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    # Retrieve user's resume skills if available
    user_resume = db.query(models.Resume).filter(models.Resume.user_id == request.user_id).order_by(models.Resume.created_at.desc()).first()
    skills = user_resume.skills if user_resume and user_resume.skills else []
    
    # Generate first AI question and add to dialogues table
    first_q_text = interview_engine.generate_first_question(request.interview_type, skills)
    
    db_dialogue = models.Dialogue(
        interview_id=db_interview.id,
        question=first_q_text
    )
    db.add(db_dialogue)
    db.commit()
    db.refresh(db_dialogue)
    
    return {
        "interview_id": db_interview.id,
        "first_dialogue_id": db_dialogue.id,
        "question": db_dialogue.question
    }

@app.post("/submit_answer")
async def submit_answer(request: schemas.AnswerRequest, db: Session = Depends(get_db)):
    # Find the current dialogue
    db_dialogue = db.query(models.Dialogue).filter(models.Dialogue.id == request.dialogue_id).first()
    if not db_dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
        
    db_interview = db_dialogue.interview
    
    # Get all previous dialogues for this interview to build history
    all_dialogues = db.query(models.Dialogue).filter(
        models.Dialogue.interview_id == db_interview.id,
        models.Dialogue.answer != None
    ).order_by(models.Dialogue.created_at).all()
    
    history = [{"q": d.question, "a": d.answer} for d in all_dialogues]
    
    # Generate evaluation and next question
    ai_response = interview_engine.evaluate_answer_and_generate_next(
        interview_type=db_interview.interview_type,
        conversation_history=history,
        current_answer=request.answer_text
    )
    
    # Update current dialogue with answer and evaluation
    db_dialogue.answer = request.answer_text
    db_dialogue.feedback = ai_response.get("feedback")
    db_dialogue.score = ai_response.get("score")
    db.commit()
    
    # Create next dialogue row
    new_dialogue = models.Dialogue(
        interview_id=db_interview.id,
        question=ai_response.get("next_question")
    )
    db.add(new_dialogue)
    db.commit()
    db.refresh(new_dialogue)
    
    return {
        "feedback": db_dialogue.feedback,
        "score": db_dialogue.score,
        "next_dialogue_id": new_dialogue.id,
        "next_question": new_dialogue.question
    }

@app.post("/submit_code", response_model=schemas.CodeSubmitResponse)
async def submit_code(request: schemas.CodeSubmitRequest, db: Session = Depends(get_db)):
    # Process the code using the engine (Judge0 + Gemini analysis)
    result = coding_engine.process_code_submission(
        code=request.code,
        language_id=request.language_id,
        question_title=request.question_title
    )
    
    # Save the attempt to the database
    db_attempt = models.CodingAttempt(
        user_id=request.user_id,
        question_title=request.question_title,
        code=request.code,
        language=str(request.language_id),
        status=result["status"],
        ai_feedback=result["feedback"],
        time_complexity=result["time_complexity"]
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    return {
        "id": db_attempt.id,
        "status": result["status"],
        "output": result["output"],
        "ai_feedback": result["feedback"],
        "time_complexity": result["time_complexity"]
    }

@app.post("/run_code", response_model=schemas.RunCodeResponse)
async def run_code(request: schemas.RunCodeRequest):
    result = coding_engine.simulate_run_code(
        code=request.code,
        language_id=request.language_id,
        question_title=request.question_title
    )
    return {
        "output": result["output"],
        "status": result["status"]
    }

@app.get("/dashboard_stats/{user_id}", response_model=schemas.DashboardResponse)
async def dashboard_stats(user_id: str, db: Session = Depends(get_db)):
    interviews = db.query(models.Interview).filter(models.Interview.user_id == user_id).all()
    coding_attempts = db.query(models.CodingAttempt).filter(models.CodingAttempt.user_id == user_id).order_by(models.CodingAttempt.created_at.desc()).all()
    
    # Calculate scores from all dialogues
    all_scores = []
    low_scoring_answers = []
    
    for interview in interviews:
        for dialogue in interview.dialogues:
            if dialogue.score is not None:
                all_scores.append(dialogue.score)
                if dialogue.score < 6:
                    low_scoring_answers.append({
                        "question": dialogue.question,
                        "answer": dialogue.answer,
                        "feedback": dialogue.feedback
                    })
                    
    average_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    # Recent data for charts
    recent_scores = all_scores[-10:] if len(all_scores) > 10 else all_scores
    recent_coding_status = [att.status for att in coding_attempts[:10]]
    
    # Generate weak topics
    weak_topics = "No data yet. Complete more interviews to get personalized weak topics!"
    if low_scoring_answers:
        prompt = f"Analyze these low-scoring interview answers and summarize the candidate's WEAK TOPICS in 2-3 short bullet points. Data: {low_scoring_answers}"
        try:
            from .services.ai_engine import model
            res = model.generate_content(prompt)
            weak_topics = res.text
        except:
            weak_topics = "Failed to generate weak topics due to AI error."
            
    return {
        "total_interviews": len(interviews),
        "total_coding_attempts": len(coding_attempts),
        "average_score": round(average_score, 1),
        "weak_topics": weak_topics,
        "recent_scores": recent_scores,
        "recent_coding_status": recent_coding_status
    }
