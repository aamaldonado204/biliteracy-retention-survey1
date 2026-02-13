import streamlit as st

st.set_page_config(page_title="Biliteracy Teacher Retention Survey")

st.title("Biliteracy Teacher Retention Survey")

participant_id = st.text_input("Participant ID")

LIKERT = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree"
}

questions = [
    "I feel accepted and valued by colleagues at my school.",
    "I have strong, supportive relationships with people at my school.",
    "I feel like I truly belong in my school community.",
    "I often feel isolated at work.",
    "My contributions as a biliteracy teacher are recognized.",
    "I feel emotionally exhausted by my work.",
    "I intend to remain in my current teaching role next year."
]

responses = {}

for i, question in enumerate(questions):
    responses[question] = st.radio(
        question,
        options=list(LIKERT.keys()),
        format_func=lambda x: LIKERT[x],
        key=f"q_{i}"
    )

if st.button("Submit Survey"):
    st.success("Thank you! Your responses have been submitted.")
