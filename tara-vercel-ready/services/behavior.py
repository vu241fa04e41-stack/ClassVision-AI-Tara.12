def analyze_behavior(person_count: int) -> dict:
    if person_count <= 0:
        return {
            "status": "Empty Classroom",
            "activity": "No Activity",
            "attention_score": 0,
        }
    activity = "High Activity" if person_count > 60 else "Normal Activity"
    return {
        "status": "Occupied",
        "activity": activity,
        "attention_score": 90,
    }
