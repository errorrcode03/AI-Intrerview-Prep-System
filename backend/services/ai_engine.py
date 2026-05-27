import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Use the recommended model for text tasks
model = genai.GenerativeModel('gemini-3.5-flash')

def analyze_resume(resume_text: str):
    """
    Analyzes the resume text using Gemini and returns an ATS score and a list of skills.
    """
    if not API_KEY:
        return {"ats_score": 0, "skills": ["API Key Missing"]}

    prompt = f"""
    You are an expert HR ATS (Applicant Tracking System).
    Analyze the following resume text and provide:
    1. An ATS match score out of 100 based on general professional quality and clarity.
    2. A list of up to 10 key technical and soft skills extracted from the text.

    Resume Text:
    {resume_text}

    Return the result EXACTLY as a valid JSON object with the following keys:
    "ats_score" (integer)
    "skills" (list of strings)
    
    Do NOT include any markdown formatting like ```json or ``` in your response, just the raw JSON object.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Sometimes the model might wrap in markdown despite instructions, so clean it up
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return {
            "ats_score": result.get("ats_score", 50),
            "skills": result.get("skills", [])
        }
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"ats_score": 0, "skills": ["Error parsing resume"]}
