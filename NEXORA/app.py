
import streamlit as st, os, re, json
from pathlib import Path
st.set_page_config(page_title="NEXORA — Your Career. Reimagined with AI.",page_icon="✦",layout="wide",initial_sidebar_state="expanded")
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "styles" / "main.css"

st.set_page_config(
    page_title="NEXORA — Your Career. Reimagined with AI.",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True
)
from backend.db import create_user, login, save_profile
from backend.core import *

def card(title,text,icon="✦"):
    st.markdown(f'<div class="card"><div class="pill">{icon}</div><h3>{title}</h3><div class="muted">{text}</div></div>',unsafe_allow_html=True)
def output(text,title="AI INSIGHT"):
    st.markdown(f'<div class="card"><div class="pill">✦ {title}</div></div><div class="output">{text}</div>',unsafe_allow_html=True)
def profile_text(p):
    return "\n".join(f"{k.title()}: {v}" for k,v in p.items() if v)

if "auth" not in st.session_state: st.session_state.auth=False
if "page" not in st.session_state: st.session_state.page="Home"
if "step" not in st.session_state: st.session_state.step=1
if "profile" not in st.session_state: st.session_state.profile={}

def footer():
    st.markdown('<div class="footer"><div class="nexora-logo">NEXORA</div><div>Your Career. Reimagined with AI.</div><br>About &nbsp; • &nbsp; Features &nbsp; • &nbsp; Contact &nbsp; • &nbsp; Privacy<br><br>© 2026 NEXORA. All Rights Reserved.</div>',unsafe_allow_html=True)

def home():
    st.markdown('<div class="hero"><div class="kicker">AI Career Platform</div><h1>Your Career.<br>Reimagined with AI.</h1><p>NEXORA brings resume intelligence, job matching, career mentoring, interview preparation and personalized learning into one premium AI workspace.</p></div>',unsafe_allow_html=True)
    st.write("")
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("Get Started  →",use_container_width=True): st.session_state.page="Auth"; st.rerun()
    with c2: st.markdown('<div class="muted" style="padding:12px">AI-powered career tools • One intelligent workspace</div>',unsafe_allow_html=True)
    st.markdown("## Everything you need to move forward")
    cols=st.columns(4)
    feats=[("Resume AI","Generate and refine ATS-ready resumes."),("Job Match","Understand how your profile aligns with a role."),("Career Mentor","Get practical, role-specific guidance."),("Learning Roadmap","Turn skill gaps into a structured plan.")]
    for col,(t,d) in zip(cols,feats):
        with col: card(t,d,"✦")
    st.markdown("## How NEXORA works")
    cols=st.columns(4)
    for i,(t,d) in enumerate([("01","Create your profile"),("02","Analyze your career fit"),("03","Generate AI outputs"),("04","Take your next step")]):
        with cols[i]: card(t,d,"0"+str(i+1))
    footer()

def auth():
    st.markdown('<div class="hero"><div class="kicker">Welcome to NEXORA</div><h1>Build your next career move.</h1><p>Create an account once. Your profile remains saved for future logins.</p></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.markdown("### Create Account")
        e=st.text_input("Email",key="su_e"); p=st.text_input("Password",type="password",key="su_p"); cp=st.text_input("Confirm Password",type="password",key="su_cp")
        if st.button("Create Account",use_container_width=True):
            if not e or not p: st.error("Enter email and password.")
            elif p!=cp: st.error("Passwords do not match.")
            else:
                ok,msg=create_user(e,p)
                if ok:
                    st.session_state.email=e.lower().strip(); st.session_state.auth=True; st.session_state.profile={}; st.session_state.page="Onboarding"; st.rerun()
                else: st.error(msg)
    with b:
        st.markdown("### Log In")
        e=st.text_input("Email",key="li_e"); p=st.text_input("Password",type="password",key="li_p")
        if st.button("Log In",use_container_width=True):
            ok,prof=login(e,p)
            if ok:
                st.session_state.email=e.lower().strip(); st.session_state.profile=prof; st.session_state.auth=True; st.session_state.page="Dashboard"; st.rerun()
            else: st.error("Invalid email or password.")
    st.markdown("<div class='muted' style='text-align:center;margin-top:25px'>Your account is stored locally for this project.</div>",unsafe_allow_html=True)

def onboarding():
    p=st.session_state.profile
    st.markdown(f'<div class="kicker">NEXORA SETUP • STEP {st.session_state.step} OF 4</div><h1>Let’s build your career profile.</h1>',unsafe_allow_html=True)
    st.progress(st.session_state.step/4)
    if st.session_state.step==1:
        p["name"]=st.text_input("Full Name",p.get("name","")); p["email"]=st.text_input("Email",p.get("email",st.session_state.email)); p["phone"]=st.text_input("Phone",p.get("phone","")); p["location"]=st.text_input("Location",p.get("location",""))
    elif st.session_state.step==2:
        p["education"]=st.text_area("Education",p.get("education","")); p["certifications"]=st.text_area("Certifications",p.get("certifications",""))
    elif st.session_state.step==3:
        p["skills"]=st.text_area("Skills",p.get("skills","")); p["experience"]=st.text_area("Experience",p.get("experience","")); p["projects"]=st.text_area("Projects",p.get("projects",""))
    else:
        p["career_goal"]=st.text_area("Career Goal",p.get("career_goal","")); p["interests"]=st.text_area("Interests",p.get("interests",""))
    c1,c2=st.columns([1,1])
    with c1:
        if st.session_state.step>1 and st.button("← Back",use_container_width=True): st.session_state.step-=1; st.rerun()
    with c2:
        label="Finish & Open Dashboard →" if st.session_state.step==4 else "Next →"
        if st.button(label,use_container_width=True):
            save_profile(st.session_state.email,p)
            if st.session_state.step<4: st.session_state.step+=1
            else: st.session_state.page="Dashboard"
            st.rerun()

def dashboard():
    p=st.session_state.profile
    st.markdown(f'<div class="hero"><div class="kicker">NEXORA WORKSPACE</div><h1>Welcome back, {(p.get("name") or "there").split()[0]}.</h1><p>Your AI career workspace is ready. Choose a tool below to continue.</p></div>',unsafe_allow_html=True)
    st.markdown("## Your career toolkit")
    items=[("Smart Student Profile","Profile & career goals","Profile"),("AI Resume Generator","Create an ATS-ready resume","Resume AI"),("Resume Analyzer","Improve your ATS readiness","Resume Analyzer"),("JD Analyzer","Understand role requirements","JD Analyzer"),("Resume–Job Match","Measure profile alignment","Job Match"),("Skill Gap Analyzer","See what to learn next","Skill Gap"),("AI Career Mentor","Ask your career questions","Career Mentor"),("Interview Preparation","Practice role-specific questions","Interview"),("Cover Letter Generator","Create tailored applications","Cover Letter"),("Learning Roadmap","Build a personalized plan","Learning Roadmap")]
    for row in range(0,10,5):
        cols=st.columns(5)
        for col,(t,d,target) in zip(cols,items[row:row+5]):
            with col:
                card(t,d,"✦")
                if st.button("Open →",key="go"+target,use_container_width=True): st.session_state.page=target; st.rerun()

def page_profile():
    p=st.session_state.profile; st.markdown("## Smart Student Profile")
    for k,label in [("name","Name"),("email","Email"),("phone","Phone"),("location","Location"),("education","Education"),("skills","Skills"),("experience","Experience"),("projects","Projects"),("certifications","Certifications"),("interests","Interests"),("career_goal","Career Goal")]:
        p[k]=st.text_area(label,p.get(k,""),key="pf_"+k) if k in ["education","skills","experience","projects","certifications","interests","career_goal"] else st.text_input(label,p.get(k,""),key="pf_"+k)
    if st.button("Save Profile"): save_profile(st.session_state.email,p); st.success("Profile saved.")

def page_resume():
    st.markdown("## AI Resume Generator"); st.caption("Your profile is the source of truth.")
    style=st.selectbox("Resume Style",["Professional","Modern","Minimal","Technology / AI","Creative"])
    extra=st.text_area("Additional resume details")
    if st.button("Generate Resume"):
        st.session_state.resume=generate_resume(profile_text(st.session_state.profile)+"\nStyle: "+style+"\n"+extra)
    if st.session_state.get("resume"):
        output(st.session_state.resume,"RESUME PREVIEW")
        st.download_button("Download PDF",text_to_pdf(st.session_state.resume),"NEXORA_Resume.pdf","application/pdf")

def page_analyzer():
    st.markdown("## Resume Analyzer")
    up=st.file_uploader("Upload PDF, DOCX or TXT",type=["pdf","docx","txt"])
    if up and st.button("Analyze Resume"): st.session_state.ra=analyze_resume(extract_file(up.getvalue(),up.name))
    if st.session_state.get("ra"): output(st.session_state.ra,"ATS ANALYSIS")

def page_jd():
    st.markdown("## Job Description Analyzer"); jd=st.text_area("Paste Job Description",height=300)
    up=st.file_uploader("Or upload JD",type=["txt","pdf","docx"])
    if up: jd=extract_file(up.getvalue(),up.name)
    if st.button("Analyze JD") and jd: st.session_state.jd=analyze_jd(jd)
    if st.session_state.get("jd"): output(st.session_state.jd,"JOB INTELLIGENCE")

def page_match():
    st.markdown("## Resume–Job Match")
    r=st.text_area("Resume text",value=profile_text(st.session_state.profile),height=220); j=st.text_area("Job Description",height=220)
    if st.button("Calculate Match") and r and j: st.session_state.match=match_resume_to_jd(r,j)
    if st.session_state.get("match"): output(st.session_state.match,"JOB MATCH")

def page_gap():
    st.markdown("## Skill Gap Analyzer"); role=st.text_input("Target Job Role"); skills=st.text_area("Current Skills",value=st.session_state.profile.get("skills",""))
    if st.button("Analyze Skill Gap") and role: st.session_state.gap=analyze_skill_gap(skills,role)
    if st.session_state.get("gap"): output(st.session_state.gap,"SKILL INTELLIGENCE")

def page_mentor():
    st.markdown("## AI Career Mentor")
    if "chat" not in st.session_state: st.session_state.chat=[]
    for role,msg in st.session_state.chat: st.markdown(f'<div class="{"chat-user" if role=="user" else "chat-ai"}">{msg}</div>',unsafe_allow_html=True)
    q=st.chat_input("Ask NEXORA anything about your career...")
    if q:
        st.session_state.chat.append(("user",q)); ans=ask_career_mentor(q,profile_text(st.session_state.profile)); st.session_state.chat.append(("ai",ans)); st.rerun()

def page_interview():
    st.markdown("## Interview Preparation")
    role=st.selectbox("Job Role",["Data Scientist","AI Engineer","ML Engineer","Software Developer"]); level=st.selectbox("Difficulty",["Beginner","Intermediate","Advanced"]); typ=st.selectbox("Interview Type",["Technical","HR","Behavioral","Mixed"])
    if st.button("Generate Questions"): st.session_state.int=generate_interview_questions(role,level.lower(),5)+"\n\nInterview Type: "+typ
    if st.session_state.get("int"): output(st.session_state.int,"INTERVIEW STUDIO")

def page_cover():
    st.markdown("## Cover Letter Generator"); company=st.text_input("Company"); role=st.text_input("Job Role"); jd=st.text_area("Job Description",height=220)
    if st.button("Generate Cover Letter"): st.session_state.cl=generate_cover_letter(profile_text(st.session_state.profile)+"\nTarget Role: "+role,jd,company)
    if st.session_state.get("cl"):
        output(st.session_state.cl,"COVER LETTER")
        st.download_button("Download PDF",text_to_pdf(st.session_state.cl),"NEXORA_Cover_Letter.pdf","application/pdf")

def page_roadmap():
    st.markdown("## Personalized Learning Roadmap"); role=st.text_input("Target Job"); level=st.selectbox("Current Level",["Beginner","Intermediate","Advanced"]); weeks=st.slider("Timeline (weeks)",4,24,12)
    if st.button("Generate Roadmap"): st.session_state.rm=generate_roadmap(role,level,weeks)
    if st.session_state.get("rm"): output(st.session_state.rm,"LEARNING ROADMAP")

if not st.session_state.auth:
    st.markdown('<div class="nexora-logo">NEXORA</div>',unsafe_allow_html=True)
    if st.session_state.page=="Home": home()
    else: auth()
else:
    with st.sidebar:
        st.markdown('<div class="nexora-logo">NEXORA</div><p class="muted">Your Career. Reimagined with AI.</p>',unsafe_allow_html=True)
        nav=["Dashboard","Profile","Resume AI","Resume Analyzer","JD Analyzer","Job Match","Skill Gap","Career Mentor","Interview","Cover Letter","Learning Roadmap"]
        for x in nav:
            if st.button(x,use_container_width=True,key="nav"+x): st.session_state.page=x; st.rerun()
        st.divider(); st.markdown(f'<div class="muted">{st.session_state.email}</div>',unsafe_allow_html=True)
        if st.button("Log Out",use_container_width=True): st.session_state.auth=False; st.session_state.page="Home"; st.session_state.chat=[]; st.rerun()
    pages={"Dashboard":dashboard,"Profile":page_profile,"Resume AI":page_resume,"Resume Analyzer":page_analyzer,"JD Analyzer":page_jd,"Job Match":page_match,"Skill Gap":page_gap,"Career Mentor":page_mentor,"Interview":page_interview,"Cover Letter":page_cover,"Learning Roadmap":page_roadmap}
    if st.session_state.page=="Onboarding": onboarding()
    else: pages.get(st.session_state.page,dashboard)()
