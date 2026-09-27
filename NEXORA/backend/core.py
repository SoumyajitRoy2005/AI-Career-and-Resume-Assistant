
import os, io, re
from dotenv import load_dotenv
load_dotenv()
from google import genai
from pypdf import PdfReader
from fpdf import FPDF
try:
    from docx import Document
except Exception: Document=None

MODEL_NAME=os.getenv("MODEL_NAME","gemini-3.1-flash-lite")
_api=os.getenv("GEMINI_API_KEY","").strip()
client=genai.Client(api_key=_api) if _api else None

def build_prompt(role, context, instructions, user_input, constraints, output_format):
    return f"""### ROLE
{role}

### CONTEXT
{context}

### INSTRUCTIONS
{instructions}

### USER INPUT
{user_input}

### CONSTRAINTS
{constraints}

### EXPECTED OUTPUT FORMAT
{output_format}""".strip()

PROMPTS={}
PROMPTS["resume_generate"]=lambda p: build_prompt(
"You are an expert ATS-aware resume writer for students and early-career candidates.",
"The candidate profile below is the ONLY source of truth. Do not invent employers, dates, or degrees.",
"Write a clean, professional, single-column resume in plain text with clear section headings.",
p,"No fabrication. No first-person pronouns. Concise bullet points. ATS-friendly.",
"Plain text with sections: Name & Contact | Summary | Skills | Education | Projects | Experience | Achievements")
PROMPTS["resume_analyze"]=lambda p: build_prompt(
"You are a senior technical recruiter and ATS specialist.","Analyze the resume below as if screening for a real role.",
"Score the resume, list strengths, weaknesses, and concrete fixes.",p,
"Be specific and actionable. No generic advice.",
"Structured text: OVERALL SCORE (0-100) | STRENGTHS | WEAKNESSES | ATS ISSUES | TOP 5 FIXES")
PROMPTS["jd_analyze"]=lambda p: build_prompt(
"You are a hiring manager extracting structured requirements from a job description.",
"Extract only what is explicitly stated or clearly implied.",
"Identify required skills, keywords, qualifications, and role expectations.",p,
"Do not invent requirements that are not in the JD.",
"Structured text: ROLE TITLE | REQUIRED SKILLS | PREFERRED SKILLS | KEYWORDS | QUALIFICATIONS | RESPONSIBILITIES")
PROMPTS["resume_jd_match"]=lambda p: build_prompt(
"You are an ATS matching engine.","Compare the resume against the job description objectively.",
"Compute a match percentage, list matching and missing keywords/skills, and give targeted suggestions.",p,
"Match % must be justified by the keyword overlap you list.",
"Structured text: MATCH % | MATCHING KEYWORDS | MISSING KEYWORDS | MATCHING SKILLS | MISSING SKILLS | SUGGESTIONS")
PROMPTS["skill_gap"]=lambda p: build_prompt(
"You are a career skills coach.","Based on the target role and current skills, identify gaps.",
"Categorize missing skills by priority and recommend what to learn first.",p,
"Priority must be justified by role relevance.",
"Structured text: HIGH PRIORITY | MEDIUM PRIORITY | LOW PRIORITY | RECOMMENDED NEXT STEPS")
PROMPTS["career_mentor"]=lambda p: build_prompt(
"You are a warm, pragmatic career mentor for students.","Answer the student's career question with role-specific, actionable guidance.",
"Give direct advice, then a short action plan.",p,"Be encouraging but honest. No fluff.",
"ADVICE | ACTION PLAN (3-5 steps)")
PROMPTS["roadmap"]=lambda p: build_prompt(
"You are a curriculum designer for tech careers.","Design a beginner-to-advanced roadmap for the target role.",
"Phase the roadmap, list skills per phase, and recommend portfolio projects.",p,
"Realistic timeline. Free/low-cost resources preferred.",
"PHASE 1 (Beginner) | PHASE 2 (Intermediate) | PHASE 3 (Advanced) | PROJECTS | MILESTONES")
PROMPTS["interview"]=lambda p: build_prompt(
"You are a technical interviewer.","Generate interview questions for the given role and level.",
"Produce HR, technical, and role-specific questions with brief ideal-answer hints.",p,
"Questions must be relevant to the role.",
"HR QUESTIONS | TECHNICAL QUESTIONS | ROLE-SPECIFIC QUESTIONS | PREPARATION REPORT")
PROMPTS["cover_letter"]=lambda p: build_prompt(
"You are a professional cover-letter writer.","Write a tailored cover letter using the candidate profile and job description.",
"Match tone to the company. Keep it under 350 words.",p,
"No fabrication. No clichés like 'I am writing to apply'.",
"Plain text cover letter with greeting, 3-4 body paragraphs, closing.")
PROMPTS["pdf_analyze"]=lambda p: build_prompt(
"You are a document analyst.","Analyze the PDF text below per the requested task.",
"Follow the task instruction exactly.",p,"Only use information present in the document.",
"Clear, structured response matching the task.")

def llm(prompt, temperature=.4):
    if not client: return "AI service is not configured. Add GEMINI_API_KEY to your .env file."
    try:
        r=client.interactions.create(model=MODEL_NAME,input=prompt)
        return (r.output_text or "").strip()
    except Exception as e:
        return f"AI request error: {e}"

def generate_resume(p): return llm(PROMPTS["resume_generate"](p),.3)
def analyze_resume(p): return llm(PROMPTS["resume_analyze"](p),.3)
def analyze_jd(p): return llm(PROMPTS["jd_analyze"](p),.2)
def match_resume_to_jd(r,j): return llm(PROMPTS["resume_jd_match"](f"RESUME:\n{r}\n\nJOB DESCRIPTION:\n{j}"),.2)
def analyze_skill_gap(s,role): return llm(PROMPTS["skill_gap"](f"TARGET ROLE: {role}\n\nCURRENT SKILLS: {s}"),.3)
def ask_career_mentor(q,ctx=""): return llm(PROMPTS["career_mentor"](f"STUDENT CONTEXT: {ctx or 'Not provided'}\n\nQUESTION: {q}"),.5)
def generate_roadmap(role,level,weeks=12): return llm(PROMPTS["roadmap"](f"TARGET ROLE: {role}\nCURRENT LEVEL: {level}\nTIMELINE: {weeks} weeks"),.4)
def generate_interview_questions(role,level="entry",count=5): return llm(PROMPTS["interview"](f"ROLE: {role}\nLEVEL: {level}\nQUESTIONS PER CATEGORY: {count}"),.5)
def generate_cover_letter(profile,jd,company=""): return llm(PROMPTS["cover_letter"](f"COMPANY: {company or 'the company'}\n\nCANDIDATE PROFILE:\n{profile}\n\nJOB DESCRIPTION:\n{jd}"),.4)

def extract_file(data,name):
    if name.lower().endswith(".pdf"):
        return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
    if name.lower().endswith(".docx"):
        if not Document: return ""
        return "\n".join(x.text for x in Document(io.BytesIO(data)).paragraphs)
    return data.decode("utf-8",errors="ignore")

def text_to_pdf(text):
    pdf=FPDF(); pdf.set_auto_page_break(auto=True,margin=15); pdf.set_margins(15,15,15); pdf.add_page(); pdf.set_font("Helvetica",size=11)
    safe=text.replace("—","-").replace("–","-").replace("•","*").encode("latin-1",errors="replace").decode("latin-1")
    w=pdf.w-pdf.l_margin-pdf.r_margin
    for line in safe.split("\n"):
        pdf.set_x(pdf.l_margin); pdf.multi_cell(w,6,line if line.strip() else " ")
    return bytes(pdf.output())
