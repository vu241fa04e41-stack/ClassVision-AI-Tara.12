def calculate_attendance(total_students: int, present_students: int) -> float:
    if total_students <= 0:
        return 0.0
    return round((present_students / total_students) * 100, 2)
