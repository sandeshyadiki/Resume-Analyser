import streamlit as st
import pandas as pd
from docx import Document
import PyPDF2
import re
from gtts import gTTS

# -------------------------------
# 🎨 Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better look
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fb;
        }
        .reportview-container .markdown-text-container {
            font-family: 'Segoe UI', sans-serif;
        }
        .block-container {
            padding: 2rem 2rem 2rem 2rem;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 0.5em 1em;
            font-size: 16px;
            border-radius: 8px;
        }
        .stFileUploader {
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            padding: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🌟 Sidebar
# -------------------------------
with st.sidebar:
    st.title("🧠 Resume Analyzer AI")
    st.markdown("Upload your resume to get AI feedback, match score and learning resources.")
    st.image("https://cdn-icons-png.flaticon.com/512/942/942748.png", width=150)
    st.markdown("Developed with ❤️ by **Sandesh**")
    st.markdown("---")
    st.markdown("🔗 [GitHub](https://github.com) | 🌐 [Portfolio](https://yourportfolio.com)")

# -------------------------------
# 🧾 Main Header
# -------------------------------
st.markdown("<h1 style='text-align: center;'>📄 AI Resume Analyzer Portal</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Get insights, skill score, suggestions and voice feedback</h4>", unsafe_allow_html=True)
st.markdown("")

# -------------------------------
# 📂 Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload your Resume (.docx or .pdf)", type=["docx", "pdf"])

# --- Skill Dictionary ---
role_skills = {
    "Data Analyst": ["python", "sql", "excel", "data visualization", "tableau", "power bi", "statistics", "machine learning"],
    "Web Developer": ["html", "css", "javascript", "react", "nodejs", "mongodb", "express", "frontend", "backend"],
    "AI Engineer": ["python", "machine learning", "deep learning", "tensorflow", "keras", "pytorch", "nlp", "opencv"]
}

# --- Extraction Functions ---
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() for page in pdf_reader.pages])

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else ""

def extract_phone(text):
    match = re.search(r"\b\d{10}\b", text)
    return match.group() if match else ""

def extract_skills(text):
    skill_keywords = [skill for sublist in role_skills.values() for skill in sublist]
    return list({skill for skill in skill_keywords if skill.lower() in text.lower()})

def extract_education(text):
    edu_keywords = ['b.tech', 'm.tech', 'b.e', 'm.e', 'mba', 'msc', 'bsc', 'phd', 'bca', 'mca']
    return ", ".join([edu.upper() for edu in edu_keywords if edu in text.lower()])

def calculate_skill_score(resume_skills, target_skills):
    matched = [s for s in resume_skills if s in target_skills]
    return round(len(matched) / len(target_skills) * 100, 2)

from fuzzywuzzy import fuzz

def compute_skill_score(resume_text, target_role):
    role_skills = {
        "Data Analyst": {
            "mandatory": ["python", "sql", "excel", "statistics"],
            "optional": ["power bi", "tableau", "pandas", "numpy", "data visualization"]
        },
        "Web Developer": {
            "mandatory": ["html", "css", "javascript"],
            "optional": ["react", "nodejs", "express", "mongodb"]
        },
        # Add more roles...
    }

    resume_text = resume_text.lower()
    mandatory_skills = role_skills.get(target_role, {}).get("mandatory", [])
    optional_skills = role_skills.get(target_role, {}).get("optional", [])

    matched_mandatory = 0
    matched_optional = 0

    for skill in mandatory_skills:
        if fuzz.partial_ratio(skill, resume_text) > 80:
            matched_mandatory += 1

    for skill in optional_skills:
        if fuzz.partial_ratio(skill, resume_text) > 80:
            matched_optional += 1

    total_score = (matched_mandatory * 2 + matched_optional)
    max_score = (len(mandatory_skills) * 2 + len(optional_skills))

    skill_score = int((total_score / max_score) * 100)
    return skill_score


# --- Learning Links ---
learning_links = {
    "python": "https://docs.python.org/3/tutorial/",
    "sql": "https://www.w3schools.com/sql/",
    "excel": "https://support.microsoft.com/en-us/excel",
    "data visualization": "https://www.tableau.com/learn/articles/data-visualization",
    "tableau": "https://www.tableau.com/learn/training",
    "power bi": "https://learn.microsoft.com/en-us/power-bi/",
    "statistics": "https://www.khanacademy.org/math/statistics-probability",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "html": "https://developer.mozilla.org/en-US/docs/Web/HTML",
    "css": "https://developer.mozilla.org/en-US/docs/Web/CSS",
    "javascript": "https://javascript.info/",
    "react": "https://reactjs.org/docs/getting-started.html",
    "nodejs": "https://nodejs.org/en/docs",
    "mongodb": "https://www.mongodb.com/docs/",
    "express": "https://expressjs.com/",
    "frontend": "https://www.freecodecamp.org/learn/",
    "backend": "https://roadmap.sh/backend",
    "deep learning": "https://www.deeplearning.ai/",
    "tensorflow": "https://www.tensorflow.org/tutorials",
    "keras": "https://keras.io/getting_started/",
    "pytorch": "https://pytorch.org/tutorials/",
    "nlp": "https://www.nltk.org/",
    "opencv": "https://docs.opencv.org/"
}

# --- Resume Processing ---
if uploaded_file:
    extension = uploaded_file.name.split('.')[-1].lower()
    text = extract_text_from_docx(uploaded_file) if extension == "docx" else extract_text_from_pdf(uploaded_file)

    email = extract_email(text)
    phone = extract_phone(text)
    education = extract_education(text)
    skills = extract_skills(text)

    # Role selection
    st.markdown("### 🎯 Select Your Target Role")
    selected_role = st.selectbox("Choose a role to match your resume with:", list(role_skills.keys()))
    score = calculate_skill_score(skills, role_skills[selected_role])
    missing = [s for s in role_skills[selected_role] if s not in skills]

    # Summary
    st.markdown("### 📝 Resume Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📧 **Email:** {email}")
        st.write(f"📞 **Phone:** {phone}")
        st.write(f"🎓 **Education:** {education}")
    with col2:
        st.write(f"💼 **Selected Role:** {selected_role}")
        st.write(f"🔍 **Extracted Skills:** {', '.join(skills)}")

    # Score bar
    st.markdown("### 📊 Skill Match Score")
    st.progress(score / 100)
    st.success(f"✅ Your skill match score is: **{score}%**")

    # Suggestions
    st.markdown("### 🔧 Suggestions & Learning Resources")
    if missing:
        for skill in missing:
            link = learning_links.get(skill, "#")
            st.markdown(f"- 🔸 [{skill.title()}]({link})")
    else:
        st.success("You're all set! You have all required skills for the role.")

    # Voice Assistant
    st.markdown("### 🔊 Voice Feedback")
    def speak_text(text):
        tts = gTTS(text)
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")

    voice_msg = f"Your skill match score is {score} percent."
    if missing:
        voice_msg += f" You can improve by learning: {', '.join(missing)}."
    else:
        voice_msg += " You have all required skills. Great job!"

    speak_text(voice_msg)
