import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

st.title("📚 AI Study Pack Generator")
st.write("Create personalized notes, flashcards, MCQs and practice questions with AI.")


def get_api_key():
    try:
        key = st.secrets["GROQ_API_KEY"]
        if not key:
            raise KeyError
        return key
    except Exception:
        st.error("❌ GROQ_API_KEY is missing.")
        st.info("Streamlit Cloud → Manage app → Settings → Secrets → add GROQ_API_KEY.")
        st.stop()


@st.cache_resource
def get_client():
    return Groq(api_key=get_api_key())


def generate_study_pack(client, prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are an expert AI tutor. Create accurate, clear, well-organized and student-friendly study material."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=6000,
    )
    return response.choices[0].message.content


with st.sidebar:
    st.header("👨‍🎓 Learner Profile")

    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    language = st.selectbox("Language", ["English", "Urdu"])
    learning_style = st.selectbox(
        "Learning Style", ["Visual", "Reading", "Practical", "Mixed"]
    )
    goals = st.text_area(
        "Learning Goals",
        placeholder="Example: Prepare for exam and understand concepts"
    )


st.subheader("📝 Study Topic")

topic = st.text_input("Enter your topic", placeholder="Example: Python Functions")

context = st.text_area(
    "Additional syllabus/context (optional)",
    placeholder="Enter syllabus, chapter details or important topics..."
)


if st.button("🚀 Generate Study Pack", type="primary"):

    if not topic.strip():
        st.warning("⚠️ Please enter a study topic.")
        st.stop()

    prompt = f"""
Create a complete personalized study pack.

LEARNER PROFILE
Level: {level}
Difficulty: {difficulty}
Language: {language}
Learning Style: {learning_style}
Learning Goals: {goals}

TOPIC:
{topic}

ADDITIONAL CONTEXT:
{context}

Create these sections:

# 1. Learning Objectives
Give 4-6 clear objectives.

# 2. Study Plan
Give a simple step-by-step study plan.

# 3. Detailed Notes
Explain the topic clearly at the student's level.

# 4. Key Points
List the most important points.

# 5. Examples
Give useful examples.

# 6. Flashcards
Create at least 8 question/answer flashcards.

# 7. Multiple Choice Questions
Create 10 MCQs. Each must have four options (A, B, C, D),
the correct answer, and a short explanation.

# 8. Short Practice Questions
Create 5 short-answer questions and provide answers.

# 9. Common Mistakes
List common mistakes students make.

# 10. Quick Revision
Give a concise revision summary.

Use Markdown headings and bullet points.
Keep everything accurate, useful, exam-friendly and personalized.
"""

    client = get_client()

    with st.spinner("🤖 AI is generating your study pack..."):
        try:
            result = generate_study_pack(client, prompt)

            st.success("✅ Study Pack Generated Successfully!")

            tabs = st.tabs([
                "📋 Plan", "📖 Notes", "🧠 Flashcards",
                "❓ MCQs", "✍️ Practice", "📚 Full Pack"
            ])

            with tabs[0]:
                st.markdown("### 📋 Study Plan")
                st.markdown(result)

            with tabs[1]:
                st.markdown("### 📖 Notes")
                st.markdown(result)

            with tabs[2]:
                st.markdown("### 🧠 Flashcards")
                st.markdown(result)

            with tabs[3]:
                st.markdown("### ❓ MCQs")
                st.markdown(result)

            with tabs[4]:
                st.markdown("### ✍️ Practice Questions")
                st.markdown(result)

            with tabs[5]:
                st.markdown(result)

            st.download_button(
                "⬇️ Download Study Pack",
                data=result,
                file_name="study_pack.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error("❌ Groq request failed.")
            st.code(str(e))
