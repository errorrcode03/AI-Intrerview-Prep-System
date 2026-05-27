import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-3.5-flash')

def generate_first_question(interview_type: str, resume_skills: list = None):
    """Generates the very first interview question based on the interview type."""
    
    skills_context = f"The candidate has skills in: {', '.join(resume_skills)}." if resume_skills else ""
    
    prompt = f"""
    You are an expert AI Interviewer conducting a {interview_type} interview.
    {skills_context}
    
    Generate the very first question to start the interview. 
    Make it engaging but professional. 
    For an HR interview, a classic "Tell me about yourself" or something related to their skills is great.
    For Technical, ask a broad fundamental question.
    
    Return ONLY the question string, without any quotes or extra text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Could you tell me a little bit about yourself and your background?"

def evaluate_answer_and_generate_next(interview_type: str, conversation_history: list, current_answer: str):
    """
    Evaluates the candidate's answer and generates the next question.
    conversation_history should be a list of dicts: [{'q': '...', 'a': '...'}]
    """
    history_text = ""
    for idx, turn in enumerate(conversation_history):
        history_text += f"Turn {idx+1}:\nInterviewer: {turn.get('q')}\nCandidate: {turn.get('a')}\n\n"
        
    prompt = f"""
    You are an expert AI Interviewer conducting a {interview_type} interview.
    
    Here is the conversation history so far:
    {history_text}
    
    The candidate just gave this answer to your last question:
    "{current_answer}"
    
    Your task:
    1. Evaluate the candidate's latest answer. Give it a score out of 10 based on clarity, confidence, and accuracy.
    2. Provide brief, constructive feedback on how they could improve this specific answer.
    3. Generate the NEXT interview question. Make it a logical follow-up to their answer or move to a new relevant topic.
    
    Return the result EXACTLY as a valid JSON object with the following keys:
    "score" (integer out of 10)
    "feedback" (string)
    "next_question" (string)
    
    Do not include markdown blocks like ```json.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        result = json.loads(text.strip())
        return {
            "score": result.get("score", 5),
            "feedback": result.get("feedback", "Good effort, but try to be more specific."),
            "next_question": result.get("next_question", "Can you elaborate more on your previous experiences?")
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "score": 5,
            "feedback": "Unable to process feedback at this time.",
            "next_question": "Let's move on. Describe a challenge you recently faced."
        }
