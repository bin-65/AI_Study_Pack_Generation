import os
import streamlit as st
from groq import Groq
from workflow import run_study_workflow

st.set_page_config(page_title="AI Study Pack Generator", page_icon="📚", layout="wide")

st.title("📚 AI Study Pack Generator")
st.caption("Personalized AI workflow: Planning → Content → Assessment → Review → Refinement")

def get_api_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None

with st.sidebar:
    st.header("🎯 Learner Profile")
    level = st.selectbox("Student level", [
        "School", "High School", "College / University", "Beginner", "Advanced"
    ])
    difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    language = st.selectbox("Language", ["English", "Urdu", "Roman Urdu"])
    learning_style = st.selectbox("Learning style", [
        "Balanced", "Examples first", "Flashcards first", "Exam focused"
    ])
    goals = st.text_area("Learning goals", placeholder="What should the student achieve?")

topic = st.text_input("📌 Topic", placeholder="e.g. Photosynthesis, Python loops, Algebra")
context = st.text_area(
    "📄 Optional syllabus/context",
    placeholder="Paste syllabus points, textbook scope, or exam requirements."
)

if st.button("🚀 Generate Study Pack", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic.")
    elif not get_api_key():
        st.error("GROQ_API_KEY is missing. Add it to Streamlit Secrets.")
    else:
        profile = {
            "topic": topic.strip(),
            "level": level,
            "difficulty": difficulty,
            "language": language,
            "learning_style": learning_style,
            "goals": goals.strip() or "Master the topic.",
            "context": context.strip() or "No additional context."
        }
        try:
            client = Groq(api_key=get_api_key())
            with st.status("Running AI workflow...", expanded=True) as status:
                st.write("1️⃣ Planning learning objectives...")
                result = run_study_workflow(client, profile, st.write)
                status.update(label="Workflow completed ✅", state="complete")
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"Workflow failed: {e}")
            st.info("Check your API key and try again.")

result = st.session_state.get("result")

if result:
    plan = result["plan"]
    review = result["review"]
    final = result["final"]

    st.divider()
    st.subheader(f"📖 Final Study Pack: {result['profile']['topic']}")

    a, b, c = st.columns(3)
    a.metric("Review score", f"{review.get('score', 0)}/100")
    b.metric("Approved", "Yes" if review.get("approved") else "Refined")
    c.metric("Refinement", "Applied" if result["refined"] else "Not needed")

    tabs = st.tabs([
        "🗺️ Planning", "📝 Notes", "🧠 Flashcards",
        "❓ MCQs", "🎯 Practice", "🔍 Review"
    ])

    with tabs[0]:
        st.write("### Learning objectives")
        for item in plan.get("learning_objectives", []):
            st.markdown(f"- {item}")
        st.write("### Study outline")
        for item in plan.get("outline", []):
            st.markdown(f"- {item}")

    with tabs[1]:
        st.markdown(final.get("notes", ""))
        st.write("### Key points")
        for item in final.get("key_points", []):
            st.markdown(f"- {item}")
        if final.get("examples"):
            st.write("### Examples")
            for item in final["examples"]:
                st.markdown(f"- {item}")

    with tabs[2]:
        for i, card in enumerate(final.get("flashcards", []), 1):
            with st.expander(f"Card {i}: {card.get('question', '')}"):
                st.write(card.get("answer", ""))

    with tabs[3]:
        for i, q in enumerate(final.get("mcqs", []), 1):
            st.markdown(f"**{i}. {q.get('question', '')}**")
            answer = st.radio(
                "Choose an answer:",
                q.get("options", []),
                key=f"mcq_{i}",
                index=None
            )
            if st.button("Check answer", key=f"check_{i}"):
                if answer == q.get("correct_answer"):
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Correct answer: {q.get('correct_answer')}")
                st.caption(q.get("explanation", ""))

    with tabs[4]:
        for i, q in enumerate(final.get("short_questions", []), 1):
            with st.expander(f"Question {i}: {q.get('question', '')}"):
                st.write(f"**Answer:** {q.get('answer', '')}")

    with tabs[5]:
        st.write(f"**Score:** {review.get('score', 0)}/100")
        st.write(f"**Approved:** {review.get('approved', False)}")
        for item in review.get("issues", []):
            st.markdown(f"- {item}")

    st.download_button(
        "⬇️ Download Study Pack JSON",
        data=__import__("json").dumps(result, ensure_ascii=False, indent=2),
        file_name="study_pack_workflow.json",
        mime="application/json",
        use_container_width=True
    )
else:
    st.info("Enter a topic and learner profile, then click Generate Study Pack.")
