import streamlit as st

st.title("Biliteracy Teacher Retention Survey")

participant_id = st.text_input("Participant ID")

LIKERT = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree"
}

q1 = st.radio(
    "I feel accepted and valued by colleagues at my school.",
    options=list(LIKERT.keys()),
    format_func=lambda x: LIKERT[x]
)

q2 = st.radio(
    "I feel emotionally exhausted by my work.",
    options=list(LIKERT.keys()),
    format_func=lambda x: LIKERT[x]
)

q3 = st.radio(
    "I intend to remain in my current teaching role next year.",
    options=list(LIKERT.keys()),
    format_func=lambda x: LIKERT[x]
)

if st.button("Submit"):
    st.success("Thank you! Your response has been submitted.")
