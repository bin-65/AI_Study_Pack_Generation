import streamlit as st
from groq import Groq
import json


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# GET GROQ API KEY
# --------------------------------------------------

def get_api_key():

    try:
        return st.secrets["GROQ_API_KEY"]

    except Exception:
        st.error("❌ GROQ_API_KEY is not configured.")
        st.info(
            "Streamlit Cloud → Manage app → Settings → Secrets "
            "mein GROQ_API_KEY add karein."
        )
        st.stop()


# --------------------------------------------------
# GROQ CLIENT
# --------------------------------------------------

api_key = get_api_key()

client = Groq(api_key=api_key)


# --------------------------------------------------
# AI FUNCTION
# --------------------------------------------------

def ask_ai(prompt):

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert AI tutor. "
                    "Create clear, accurate and student-friendly "
                    "study material."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.7,

        max_tokens=5000
    )

    return response.choices[0].message.content


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📚 AI Study Pack Generator")

st.write(
    "Generate personalized notes, flashcards, MCQs and practice questions using AI."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("👨‍🎓 Learner Profile")


level = st.sidebar.selectbox(
    "Level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)


difficulty = st.sidebar.selectbox(
    "Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)


language = st.sidebar.selectbox(
    "Language",
    [
        "English",
        "Urdu"
    ]
)


learning_style = st.sidebar.selectbox(
    "Learning Style",
    [
        "Visual",
        "Reading",
        "Practical",
        "Mixed"
    ]
)


goals = st.sidebar.text_area(
    "Learning Goals",
    placeholder="Example: Prepare for exam and understand concepts"
)


# --------------------------------------------------
# MAIN INPUT
# --------------------------------------------------

st.subheader("📝 Study Topic")


topic = st.text_input(
    "Enter your topic",
    placeholder="Example: Python Functions"
)


context = st.text_area(
    "Additional syllabus/context (optional)",
    placeholder="Enter syllabus, chapter details or important topics..."
)


# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------

if st.button("🚀 Generate Study Pack", type="primary"):

    if not topic.strip():

        st.warning("⚠️ Please enter a study topic.")

        st.stop()


    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    prompt = f"""
Create a complete personalized study pack.

STUDENT PROFILE
----------------
Level: {level}
Difficulty: {difficulty}
Language: {language}
Learning Style: {learning_style}
Learning Goals: {goals}

TOPIC
----------------
{topic}

ADDITIONAL CONTEXT
----------------
{context}


Create the study pack with these sections:

1. Learning Objectives
2. Study Plan
3. Detailed Notes
4. Key Points
5. Examples
6. Flashcards
7. Multiple Choice Questions
8. Short Practice Questions
9. Answers and Explanations
10. Common Mistakes
11. Quick Revision Summary


Make the content:

- Accurate
- Easy to understand
- Appropriate for the student's level
- Appropriate for the requested difficulty
- Personalized
- Well structured
- Exam friendly


Use the requested language.

Format the response clearly using Markdown.
"""


    # --------------------------------------------------
    # GENERATE
    # --------------------------------------------------

    with st.spinner("🤖 AI is creating your study pack..."):

        try:

            result = ask_ai(prompt)

        except Exception as e:

            st.error("❌ Something went wrong while contacting Groq.")

            st.code(str(e))

            st.stop()


    # --------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------

    st.success("✅ Study Pack Generated Successfully!")


    tabs = st.tabs(
        [
            "📋 Study Plan",
            "📖 Notes",
            "🧠 Flashcards",
            "❓ MCQs",
            "✍️ Practice",
            "🔄 Full Pack"
        ]
    )


    # Study Plan
    with tabs[0]:

        st.markdown("### 📋 Study Plan")

        st.markdown(result)


    # Notes
    with tabs[1]:

        st.markdown("### 📖 Notes")

        st.markdown(result)


    # Flashcards
    with tabs[2]:

        st.markdown("### 🧠 Flashcards")

        st.markdown(result)


    # MCQs
    with tabs[3]:

        st.markdown("### ❓ Multiple Choice Questions")

        st.markdown(result)


    # Practice
    with tabs[4]:

        st.markdown("### ✍️ Practice Questions")

        st.markdown(result)


    # Full Pack
    with tabs[5]:

        st.markdown(result)


    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------

    st.download_button(

        label="⬇️ Download Study Pack",

        data=result,

        file_name="study_pack.md",

        mime="text/markdown"
    )
