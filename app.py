  python survey_retention.py
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import csv
import os
from typing import Dict, List, Tuple

LIKERT_MIN = 1
LIKERT_MAX = 5

# -----------------------------
# Configuration (edit freely)
# -----------------------------

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

# Interpretation thresholds (mean score)
# Adjust if you prefer different cut points.
THRESHOLDS = {
    "LOW": (1.0, 2.49),
    "MID": (2.5, 3.74),
    "HIGH": (3.75, 5.0),
}


# -----------------------------
# Core logic
# -----------------------------

def reverse_score(x: int) -> int:
    # 1<->5, 2<->4, 3 stays
    return (LIKERT_MAX + LIKERT_MIN) - x

def clamp_likert(x: int) -> int:
    if x < LIKERT_MIN:
        return LIKERT_MIN
    if x > LIKERT_MAX:
        return LIKERT_MAX
    return x

def interpret(mean_score: float) -> str:
    for label, (lo, hi) in THRESHOLDS.items():
        if lo <= mean_score <= hi:
            return label
    return "UNKNOWN"

def ask_likert(prompt: str) -> int:
    while True:
        raw = input(f"{prompt}\n  ({LIKERT_MIN}=Strongly Disagree ... {LIKERT_MAX}=Strongly Agree): ").strip()
        try:
            val = int(raw)
            if LIKERT_MIN <= val <= LIKERT_MAX:
                return val
        except ValueError:
            pass
        print(f"Please enter a number from {LIKERT_MIN} to {LIKERT_MAX}.")

def compute_scale_scores(responses: Dict[str, List[int]]) -> Dict[str, Dict[str, float | str]]:
    out: Dict[str, Dict[str, float | str]] = {}
    for scale in SCALES:
        vals = responses[scale.code]
        mean = sum(vals) / len(vals)
        out[scale.code] = {
            "name": scale.name,
            "mean": round(mean, 2),
            "level": interpret(mean),
        }
    return out

def print_report(participant_id: str, scale_scores: Dict[str, Dict[str, float | str]]) -> None:
    print("\n" + "=" * 60)
    print("SURVEY SUMMARY")
    print("=" * 60)
    print(f"Participant: {participant_id}")
    print(f"Timestamp:  {datetime.now().isoformat(timespec='seconds')}\n")

    # Sorted by mean ascending to highlight lowest first
    sorted_scales = sorted(scale_scores.items(), key=lambda kv: float(kv[1]["mean"]))  # type: ignore
    for code, data in sorted_scales:
        print(f"[{code}] {data['name']}")
        print(f"  Score (mean): {data['mean']}   Level: {data['level']}")
        print()

    # Quick flags
    lows = [f"{code} ({scale_scores[code]['name']})" for code in scale_scores if scale_scores[code]["level"] == "LOW"]
    highs = [f"{code} ({scale_scores[code]['name']})" for code in scale_scores if scale_scores[code]["level"] == "HIGH"]

    print("-" * 60)
    if lows:
        print("Potential focus areas (LOW):")
        for s in lows:
            print(f"  - {s}")
    else:
        print("No scales in the LOW range.")

    if highs:
        print("\nStrength areas (HIGH):")
        for s in highs:
            print(f"  - {s}")
    print("=" * 60 + "\n")

def save_csv(
    filename: str,
    participant_id: str,
    raw_item_scores: Dict[str, List[int]],
    scale_scores: Dict[str, Dict[str, float | str]],
) -> None:
    file_exists = os.path.exists(filename)
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Flatten row
    row: Dict[str, str] = {"timestamp": timestamp, "participant_id": participant_id}

    # Add item-level columns
    for scale in SCALES:
        for idx, (prompt, reverse_scored) in enumerate(scale.items, start=1):
            col = f"{scale.code}_item{idx}"
            row[col] = str(raw_item_scores[scale.code][idx - 1])

    # Add scale-level columns
    for code, data in scale_scores.items():
        row[f"{code}_mean"] = str(data["mean"])
        row[f"{code}_level"] = str(data["level"])

    # Write CSV
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def run_survey() -> None:
    print("\nBiliteracy Teacher Retention Survey")
    print("This tool is for research/screening purposes only and is not a clinical assessment.\n")

    participant_id = input("Enter participant ID (e.g., T001): ").strip() or "UNKNOWN"

    raw_item_scores: Dict[str, List[int]] = {}

    for scale in SCALES:
        print("\n" + "-" * 60)
        print(f"{scale.name} [{scale.code}]")
        print(scale.description)
        print("-" * 60)

        scale_vals: List[int] = []
        for prompt, reverse_scored in scale.items:
            val = ask_likert(prompt)
            scored = reverse_score(val) if reverse_scored else val
            scale_vals.append(scored)
        raw_item_scores[scale.code] = scale_vals

    scale_scores = compute_scale_scores(raw_item_scores)
    print_report(participant_id, scale_scores)

    out_file = "retention_survey_results.csv"
    save_csv(out_file, participant_id, raw_item_scores, scale_scores)
    print(f"Saved results to: {out_file}\n")

if __name__ == "__main__":
    run_survey()
