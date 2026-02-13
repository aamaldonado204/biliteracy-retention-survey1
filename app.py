from dataclasses import dataclass
from typing import Dict, List, Tuple
import streamlit as st

LIKERT_MIN = 1
LIKERT_MAX = 5

@dataclass(frozen=True)
class Scale:
    code: str
    name: str
    description: str
    items: List[Tuple[str, bool]]  # (prompt, reverse_scored)

SCALES: List[Scale] = [
    Scale(
        code="SB",
        name="Sense of Belonging",
        description="Feeling valued, included, connected, and supported in the school community.",
        items=[
            ("I feel accepted and valued by colleagues at my school.", False),
            ("I have strong, supportive relationships with people at my school.", False),
            ("I feel like I truly belong in my school community.", False),
            ("I often feel isolated at work.", True),
            ("My contributions as a biliteracy teacher are recognized.", False),
        ],
    ),
    Scale(
        code="LS",
        name="Educational Leadership Support",
        description="Support from administrators/leaders that enables effective practice and professional agency.",
        items=[
            ("School leaders provide the resources needed to teach biliteracy effectively.", False),
            ("Leaders understand the needs of biliteracy instruction.", False),
            ("I feel trusted to make instructional decisions.", False),
            ("Leadership expectations are unclear or inconsistent.", True),
            ("When challenges arise, leaders respond in helpful and timely ways.", False),
        ],
    ),
    Scale(
        code="TS",
        name="Strength-Based Practice",
        description="Using assets (student/family/community strengths) and teacher strengths to drive instruction.",
        items=[
            ("I regularly build on students’ linguistic and cultural strengths in instruction.", False),
            ("I feel confident identifying and using my strengths as a biliteracy teacher.", False),
            ("My classroom practices affirm students’ identities.", False),
            ("I focus more on deficits than strengths when planning instruction.", True),
            ("Students’ home languages are treated as assets in my classroom.", False),
        ],
    ),
    Scale(
        code="DL",
        name="Growth & Professional Learning",
        description="Access to development, collaboration, and growth opportunities aligned to biliteracy needs.",
        items=[
            ("I have access to professional learning that meets biliteracy teaching needs.", False),
            ("I have meaningful opportunities to collaborate with other biliteracy educators.", False),
            ("I receive useful feedback that helps me improve.", False),
            ("Time constraints prevent me from engaging in professional learning.", True),
            ("I feel supported in pursuing growth goals.", False),
        ],
    ),
    Scale(
        code="SJ",
        name="Social Justice & Equity Perspectives",
        description="Equity-oriented practice, advocacy, and commitment to linguistic/cultural justice.",
        items=[
            ("My work helps expand equitable opportunities for multilingual learners.", False),
            ("I feel empowered to advocate for biliteracy students and families.", False),
            ("School policies and practices support linguistic equity.", False),
            ("I feel pressure to minimize students’ home languages.", True),
            ("My instruction challenges deficit narratives about multilingual learners.", False),
        ],
    ),
    Scale(
        code="WB",
        name="Wellbeing & Retention",
        description="Sustainability, stress, workload, and intent to remain in the role/profession.",
        items=[
            ("I can manage my workload within reasonable hours.", False),
            ("I have effective strategies to manage stress related to teaching.", False),
            ("I feel emotionally exhausted by my work.", True),
            ("I intend to remain in my current teaching role next year.", False),
            ("I have considered leaving teaching due to job stress.", True),
        ],
    ),
]

THRESHOLDS = {
    "LOW": (1.0, 2.49),
    "MID": (2.5, 3.74),
    "HIGH": (3.75, 5.0),
}

def reverse_score(x: int) -> int:
    return (LIKERT_MAX + LIKERT_MIN) - x

def interpret(mean_score: float) -> str:
    for label, (lo, hi) in THRESHOLDS.items():
        if lo <= mean_score <= hi:
            return label
    return "UNKNOWN"

LIKERT_LABELS = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree",
}

st.set_page_config(page_title="Biliteracy Teacher Retention Survey")
st.title("Biliteracy Teacher Retention Survey")

participant_id = st.text_input("Participant ID (e.g., T001)", value="")

st.write("Please respond to each statement:")
st.caption("Scale: 1 = Strongly Disagree … 5 = Strongly Agree")

# Collect responses
raw: Dict[str, List[int]] = {}
scored: Dict[str, List[int]] = {}

for scale in SCALES:
    st.subheader(f"{scale.name} [{scale.code}]")
    st.write(scale.description)

    raw_vals: List[int] = []
    scored_vals: List[int] = []

    for idx, (prompt, is_reverse) in enumerate(scale.items, start=1):
        key=key, f"{scale.code}_{idx}"
        val = st.radio(
    prompt,
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: f"{x} - {LIKERT_LABELS[x]}",
    key=f"{scale.code}_{idx}",
    horizontal=True,
)
        )
        raw_vals.append(val)
        scored_vals.append(reverse_score(val) if is_reverse else val)

    raw[scale.code] = raw_vals
    scored[scale.code] = scored_vals
    st.divider()

if st.button("Submit"):
    if not participant_id.strip():
        st.error("Please enter a Participant ID before submitting.")
    else:
        # Compute and show scale scores
        st.success("Thank you! Your response has been recorded (results shown below).")

        results = []
        for scale in SCALES:
            mean = sum(scored[scale.code]) / len(scored[scale.code])
            results.append(
                {
                    "Scale": f"{scale.name} [{scale.code}]",
                    "Mean": round(mean, 2),
                    "Level": interpret(mean),
                }
            )

        st.subheader("Survey Summary")
        st.table(results)

        st.info(
            "Next step: to actually SAVE responses, we’ll connect this app to Google Sheets or a database. "
            "Right now it only displays results."
        )
