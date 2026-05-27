import os
import json
import requests
import base64
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-3.5-flash')

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com" # Or public alternative if available without RapidAPI. We will use a public one if possible, or mock it if unavailable.
# Actually, the most reliable free public instance without RapidAPI auth is often hosted at:
PUBLIC_JUDGE0_URL = "https://judge0-ce.p.rapidapi.com" # Wait, RapidAPI requires a key.
# A common truly free one used for development (though sometimes down):
FREE_JUDGE0_URL = "https://judge0-extra.p.rapidapi.com"

# For this MVP, to guarantee it works without requiring the user to sign up for RapidAPI,
# we will simulate the code execution (like Judge0 does) using python's built-in tools for Python,
# OR we can just use Gemini to evaluate if the code is correct as a fallback!
# Wait, let's try a known public unauthenticated Judge0 instance if possible, 
# else we'll simulate the execution using Gemini to evaluate correctness since it's an AI interview!
# Since the prompt asked for Judge0, I'll write the Judge0 integration code, but add a robust fallback to Gemini.

def execute_code_judge0(code: str, language_id: int, expected_output: str = None):
    """
    Attempts to execute code using Judge0. 
    NOTE: Public unauthenticated Judge0 instances are rare. 
    This is stubbed to use a RapidAPI key if provided, else falls back to AI execution simulation.
    """
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    
    if not rapidapi_key:
        return None # Trigger AI fallback
        
    url = f"https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=false"
    payload = {
        "language_id": language_id,
        "source_code": base64.b64encode(code.encode()).decode('utf-8'),
    }
    if expected_output:
        payload["expected_output"] = base64.b64encode(expected_output.encode()).decode('utf-8')
        
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            return None
            
        token = response.json()['token']
        
        # Poll for result
        for _ in range(10):
            time.sleep(1)
            get_url = f"https://judge0-ce.p.rapidapi.com/submissions/{token}?base64_encoded=true"
            res = requests.get(get_url, headers=headers)
            data = res.json()
            if data['status']['id'] > 2: # 1 In Queue, 2 Processing
                status = data['status']['description']
                stdout = base64.b64decode(data['stdout']).decode('utf-8') if data.get('stdout') else ""
                stderr = base64.b64decode(data['stderr']).decode('utf-8') if data.get('stderr') else ""
                return {"status": status, "output": stdout or stderr}
    except Exception as e:
        print(f"Judge0 Error: {e}")
        return None

def analyze_code_with_ai(code: str, language: str, question: str):
    """
    Uses Gemini to analyze the submitted code for correctness, time complexity, and feedback.
    """
    prompt = f"""
    You are an expert technical interviewer evaluating a candidate's code submission.
    
    Interview Question: {question}
    Language: {language}
    Candidate's Code:
    {code}
    
    Your task:
    1. Determine if the code correctly solves the problem (Status: "Accepted" or "Wrong Answer" or "Compilation Error").
    2. Provide the Time Complexity (e.g., O(N)).
    3. Provide brief, constructive feedback on edge cases, bugs, or optimizations.
    
    Return EXACTLY as a JSON object:
    "status" (string)
    "time_complexity" (string)
    "feedback" (string)
    "simulated_output" (string - what the code would output if run, or error message)
    
    Do NOT include markdown like ```json.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        result = json.loads(text.strip())
        return {
            "status": result.get("status", "Unknown"),
            "time_complexity": result.get("time_complexity", "O(?)"),
            "feedback": result.get("feedback", "No feedback available."),
            "output": result.get("simulated_output", "Output simulation unavailable.")
        }
    except Exception as e:
        print(f"AI Eval Error: {e}")
        return {
            "status": "Error",
            "time_complexity": "Unknown",
            "feedback": "AI evaluation failed.",
            "output": ""
        }

def process_code_submission(code: str, language_id: int, question_title: str):
    # Mapping for prompt context
    lang_map = {71: "Python", 54: "C++", 62: "Java", 63: "JavaScript"}
    language_name = lang_map.get(language_id, "Unknown Language")
    
    # Try Judge0 first (if configured)
    execution_result = execute_code_judge0(code, language_id)
    
    # Always use AI for feedback & time complexity, and for execution fallback if Judge0 isn't configured
    ai_analysis = analyze_code_with_ai(code, language_name, question_title)
    
    if execution_result:
        # Judge0 succeeded
        return {
            "status": execution_result["status"],
            "output": execution_result["output"],
            "time_complexity": ai_analysis["time_complexity"],
            "feedback": ai_analysis["feedback"]
        }
    else:
        # Fallback entirely to AI simulation
        return {
            "status": ai_analysis["status"],
            "output": ai_analysis["output"],
            "time_complexity": ai_analysis["time_complexity"],
            "feedback": ai_analysis["feedback"]
        }

def simulate_run_code(code: str, language_id: int, question_title: str):
    """
    Used for the 'Run Code' button. Simply simulates running the code on sample test cases.
    """
    lang_map = {71: "Python", 54: "C++", 62: "Java", 63: "JavaScript"}
    language_name = lang_map.get(language_id, "Unknown Language")
    
    execution_result = execute_code_judge0(code, language_id)
    if execution_result:
        return execution_result
        
    prompt = f"""
    You are a code execution engine. 
    Language: {language_name}
    Code:
    {code}
    
    Run the code in your mind against the standard example test cases for '{question_title}'.
    If there are syntax errors, output them.
    If it runs, show the simulated console output for the examples.
    
    Return EXACTLY as a JSON object:
    "status" (string: e.g., "Executed", "Syntax Error")
    "output" (string: the console output)
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        result = json.loads(text.strip())
        return {
            "status": result.get("status", "Unknown"),
            "output": result.get("output", "No output.")
        }
    except Exception as e:
        return {
            "status": "Error",
            "output": str(e)
        }
