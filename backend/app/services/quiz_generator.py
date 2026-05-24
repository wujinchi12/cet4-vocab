import random
from sqlalchemy.orm import Session
from app.models.word import Word


def generate_quiz_questions(
    db: Session,
    quiz_type: str,
    count: int,
    direction: str = "en_to_cn",
    user_id: int | None = None,
) -> list[dict]:
    all_words = db.query(Word).all()
    if len(all_words) < 4:
        return []

    selected = random.sample(all_words, min(count, len(all_words)))

    if quiz_type == "choice":
        return _generate_choice_questions(all_words, selected, direction)
    elif quiz_type == "fill":
        return _generate_fill_questions(selected, direction)
    elif quiz_type == "match":
        return _generate_match_questions(selected, direction)
    return []


def _generate_choice_questions(all_words: list[Word], selected: list[Word], direction: str) -> list[dict]:
    questions = []
    for word in selected:
        distractors = [w for w in all_words if w.id != word.id]
        chosen = random.sample(distractors, min(3, len(distractors)))

        if direction == "en_to_cn":
            question_text = word.english
            correct_answer = word.chinese
            options = [word.chinese] + [w.chinese for w in chosen]
        else:
            question_text = word.chinese
            correct_answer = word.english
            options = [word.english] + [w.english for w in chosen]

        random.shuffle(options)
        questions.append({
            "type": "choice",
            "word_id": word.id,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
        })
    return questions


def _generate_fill_questions(selected: list[Word], direction: str) -> list[dict]:
    questions = []
    for word in selected:
        if direction == "en_to_cn":
            question_text = f"写出 '{word.english}' 的中文意思"
            correct_answer = word.chinese
        else:
            question_text = f"写出 '{word.chinese}' 对应的英文单词"
            correct_answer = word.english
        questions.append({
            "type": "fill",
            "word_id": word.id,
            "question": question_text,
            "correct_answer": correct_answer,
        })
    return questions


def _generate_match_questions(selected: list[Word], direction: str) -> list[dict]:
    if direction == "en_to_cn":
        pairs = [{"left": w.english, "right": w.chinese, "word_id": w.id} for w in selected]
    else:
        pairs = [{"left": w.chinese, "right": w.english, "word_id": w.id} for w in selected]

    rights = [p["right"] for p in pairs]
    random.shuffle(rights)
    for i, p in enumerate(pairs):
        p["shuffled_right"] = rights[i]

    return [{"type": "match", "pairs": pairs}]


def grade_answers(db: Session, quiz_type: str, answers: list[dict]) -> tuple[int, int, list[dict]]:
    correct = 0
    wrong = 0
    results = []

    for ans in answers:
        word_id = ans.get("word_id")
        user_answer = ans.get("answer", "").strip()
        word = db.query(Word).filter(Word.id == word_id).first()

        correct_answer = ""
        if word:
            if quiz_type == "choice":
                # Find which question/word this answer belongs to and get expected answer
                correct_answer = ans.get("correct_answer", "")
            elif quiz_type == "fill":
                correct_answer = ans.get("correct_answer", "")
            else:
                correct_answer = ans.get("correct_answer", "")

        if quiz_type == "choice":
            is_correct = user_answer == correct_answer
        elif quiz_type == "fill":
            is_correct = user_answer.lower() == correct_answer.lower()
        else:
            is_correct = False

        if is_correct:
            correct += 1
        else:
            wrong += 1

        results.append({
            "word_id": word_id,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "english": word.english if word else "",
            "chinese": word.chinese if word else "",
        })

    return correct, wrong, results
