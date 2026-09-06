import json
import re
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("The AI response did not contain JSON.")
    return json.loads(match.group(0))

def call_ai(client, system_prompt, context, max_tokens=6000, retries=2):
    last_error = None
    for _ in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                temperature=0.35,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
                ]
            )
            return parse_json(response.choices[0].message.content)
        except Exception as error:
            last_error = error
    raise RuntimeError(f"AI stage failed after retries: {last_error}")

def run_study_workflow(client: Groq, profile: dict, progress=None):
    def log(message):
        if progress:
            progress(message)

    log("Planning Agent")
    plan = call_ai(client, """You are the Planning Agent.
Return ONLY JSON with:
goal, learning_objectives[], outline[], misconceptions[],
difficulty_rationale, personalization_notes.
Create a personalized plan from the learner profile.""", profile)

    log("Content Generation Agent")
    content = call_ai(client, """You are the Content Generation Agent.
Return ONLY JSON with:
notes, key_points[], examples[],
flashcards[] with question and answer.
Use the learner profile AND planning output.""",
        {"learner_profile": profile, "plan": plan}, 7000)

    log("Assessment Agent")
    assessment = call_ai(client, """You are the Assessment Agent.
Return ONLY JSON with:
mcqs[] where each item has question, options[4], correct_answer,
explanation; short_questions[] with question and answer.
Assess the exact objectives and generated content.""",
        {"learner_profile": profile, "plan": plan, "content": content}, 7000)

    log("Review Agent")
    review = call_ai(client, """You are the Quality Review Agent.
Return ONLY JSON with:
approved, score, issues[], missing_objectives[], factual_risks[],
improvements[].
Check accuracy, objective coverage, difficulty, clarity, duplication,
and assessment answer correctness.""",
        {
            "learner_profile": profile,
            "plan": plan,
            "content": content,
            "assessment": assessment
        }, 5000)

    needs_refinement = (
        not bool(review.get("approved", False))
        or float(review.get("score", 0)) < 85
    )

    if needs_refinement:
        log("Refinement Agent")
        final = call_ai(client, """You are the Refinement Agent.
Return ONLY JSON with:
notes, key_points[], examples[], flashcards[],
mcqs[], short_questions[].
Fix the important issues from the review while preserving the learner goals.""",
            {
                "learner_profile": profile,
                "plan": plan,
                "content": content,
                "assessment": assessment,
                "review": review
            }, 8000)
    else:
        log("Review passed — refinement not required")
        final = {**content, **assessment}

    return {
        "profile": profile,
        "plan": plan,
        "content": content,
        "assessment": assessment,
        "review": review,
        "final": final,
        "refined": needs_refinement
    }
