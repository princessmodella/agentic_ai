# Optional: evaluate correctness of answers
def evaluate_answer(answer: str, reference: str):
    if answer.strip() == reference.strip():
        return "✅ Correct"
    return "⚠️ Needs Review"
