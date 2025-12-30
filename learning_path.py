# learning_path.py

def mastery_level(score: float) -> str:
    if score < 0.4:
        return "Not Mastered"
    elif score < 0.7:
        return "Partially Mastered"
    return "Mastered"


def generate_learning_path(topic_mastery, topic_difficulty, daily_time=60):
    """
    Generate a structured, mastery-aware learning plan
    """

    if not topic_mastery:
        return [{
            "topic": "General Review",
            "time_minutes": daily_time,
            "activities": ["Light revision", "Practice questions"]
        }]

    # Sort topics by mastery (lowest first)
    sorted_topics = sorted(
        topic_mastery.items(),
        key=lambda x: x[1]
    )

    # Safe inverse mastery sum
    inverse_scores = [1 - score for _, score in sorted_topics]
    total_inverse = sum(inverse_scores) if sum(inverse_scores) > 0 else len(sorted_topics)

    path = []

    for topic, score in sorted_topics:
        level = mastery_level(score)

        weight = (1 - score) / total_inverse
        allocated_time = max(10, round(weight * daily_time))

        path.append({
            "type": "study",
            "topic": topic,
            "mastery_score": round(score, 3),
            "level": level,
            "difficulty": topic_difficulty.get(topic, 2),
            "time_minutes": allocated_time,
            "activities": suggest_activities(level)
        })

        # 🔴 CONDITIONAL REVISION (KEY FIX)
        if score < 0.5:
            path.append({
                "type": "revision",
                "topic": topic,
                "time_minutes": 10,
                "focus": "Concept reinforcement + recall"
            })

    return path


def suggest_activities(level):
    if level == "Not Mastered":
        return [
            "Concept review",
            "Worked examples",
            "Easy practice"
        ]
    elif level == "Partially Mastered":
        return [
            "Mixed practice",
            "Timed questions"
        ]
    else:
        return [
            "Challenge problems",
            "Peer explanation"
        ]