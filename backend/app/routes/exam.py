from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.word import Word
from app.models.exam import ExamPaper, ExamQuestion, ExamHistory

router = APIRouter(prefix="/api/exam", tags=["exam"])


@router.post("/cleanup")
def cleanup_duplicates(db: Session = Depends(get_db)):
    dupes = (
        db.query(ExamPaper.year, func.count(ExamPaper.id))
        .group_by(ExamPaper.year)
        .having(func.count(ExamPaper.id) > 1)
        .all()
    )
    removed = 0
    for year, _ in dupes:
        ids = [row[0] for row in db.query(ExamPaper.id).filter(ExamPaper.year == year).order_by(ExamPaper.id).all()]
        keep, remove = ids[0], ids[1:]
        for rid in remove:
            db.query(ExamQuestion).filter(ExamQuestion.paper_id == rid).delete()
            db.query(ExamHistory).filter(ExamHistory.paper_id == rid).delete()
            db.query(ExamPaper).filter(ExamPaper.id == rid).delete()
        removed += len(remove)
    db.commit()
    return {"removed_duplicate_papers": removed}


@router.get("/papers", response_model=list[dict])
def list_papers(db: Session = Depends(get_db)):
    papers = db.query(ExamPaper).order_by(ExamPaper.year.desc()).all()
    result = []
    for p in papers:
        count = db.query(ExamQuestion).filter(ExamQuestion.paper_id == p.id).count()
        result.append({
            "id": p.id, "title": p.title, "year": p.year,
            "description": p.description, "time_limit": p.time_limit,
            "question_count": count,
        })
    return result


@router.get("/papers/{paper_id}", response_model=dict)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(ExamPaper).filter(ExamPaper.id == paper_id).first()
    if not paper:
        return {"detail": "Not found"}

    questions = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.paper_id == paper_id)
        .order_by(ExamQuestion.order_num)
        .all()
    )

    q_list = []
    for q in questions:
        q_list.append({
            "id": q.id, "paper_id": q.paper_id,
            "question_type": q.question_type,
            "passage": q.passage,
            "question_text": q.question_text,
            "options": q.options,
            "order_num": q.order_num,
        })

    return {
        "id": paper.id, "title": paper.title, "year": paper.year,
        "description": paper.description, "time_limit": paper.time_limit,
        "questions": q_list,
    }


@router.post("/submit")
def submit_exam(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper_id = body.get("paper_id")
    answers = body.get("answers", [])
    time_spent = body.get("time_spent")

    questions = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.paper_id == paper_id, ExamQuestion.question_type != "writing")
        .all()
    )
    q_map = {q.id: q for q in questions}

    correct = 0
    wrong = 0
    results = []

    for ans in answers:
        q = q_map.get(ans.get("question_id"))
        if not q:
            continue
        user_answer = ans.get("answer", "").strip()
        is_correct = user_answer.lower() == q.correct_answer.strip().lower()
        if is_correct:
            correct += 1
        else:
            wrong += 1
        results.append({
            "question_id": q.id,
            "question_type": q.question_type,
            "question_text": q.question_text,
            "your_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "word_id": q.word_id,
            "english": "",
            "chinese": "",
        })

    # Enrich with word data
    word_ids = [r["word_id"] for r in results if r["word_id"]]
    if word_ids:
        words_map = {w.id: w for w in db.query(Word).filter(Word.id.in_(word_ids)).all()}
        for r in results:
            if r["word_id"] and r["word_id"] in words_map:
                r["english"] = words_map[r["word_id"]].english
                r["chinese"] = words_map[r["word_id"]].chinese

    total = correct + wrong
    score = (correct / total * 100) if total > 0 else 0

    history = ExamHistory(
        user_id=current_user.id,
        paper_id=paper_id,
        score=score,
        total_questions=total,
        correct_count=correct,
        time_spent=time_spent,
    )
    db.add(history)
    db.commit()

    return {
        "total_questions": total,
        "correct_count": correct,
        "wrong_count": wrong,
        "score_percent": score,
        "results": results,
    }


@router.get("/history")
def exam_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = (
        db.query(ExamHistory)
        .filter(ExamHistory.user_id == current_user.id)
        .order_by(ExamHistory.completed_at.desc())
        .limit(20)
        .all()
    )
    paper_ids = [e.paper_id for e in entries]
    papers = {p.id: p for p in db.query(ExamPaper).filter(ExamPaper.id.in_(paper_ids)).all()} if paper_ids else {}

    return [
        {
            "id": e.id,
            "paper_title": papers[e.paper_id].title if e.paper_id in papers else "",
            "paper_year": papers[e.paper_id].year if e.paper_id in papers else 0,
            "score": e.score,
            "total_questions": e.total_questions,
            "correct_count": e.correct_count,
            "time_spent": e.time_spent,
            "completed_at": e.completed_at.isoformat(),
        }
        for e in entries
    ]
