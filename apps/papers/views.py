from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.syllabus.models import EducationLevel, Subject, Topic
from .models import PastPaper, SolvedQuestion, TopicalAttempt, TopicalQuestion


# ---------------- Past Papers ----------------

def past_papers_home(request):
    levels = EducationLevel.objects.prefetch_related("subjects")
    return render(request, "papers/past_papers_home.html", {"levels": levels})


@login_required
def past_papers_subject(request, level_code, subject_slug):
    level = get_object_or_404(EducationLevel, code__iexact=level_code)
    subject = get_object_or_404(Subject, education_level=level, slug=subject_slug)
    papers = PastPaper.objects.filter(subject=subject).order_by("paper_number", "-year")

    grouped = {}
    for p in papers:
        grouped.setdefault(p.paper_number, []).append(p)

    return render(request, "papers/past_papers_subject.html", {
        "level": level, "subject": subject, "grouped": grouped,
    })


@login_required
def download_past_paper(request, paper_id):
    paper = get_object_or_404(PastPaper, pk=paper_id)
    if not paper.file:
        raise Http404("This paper hasn't been uploaded yet.")
    return FileResponse(paper.file.open("rb"), as_attachment=False, filename=paper.file.name)


# ---------------- Solved Papers ----------------

def solved_papers_home(request):
    levels = EducationLevel.objects.prefetch_related("subjects")
    return render(request, "papers/solved_papers_home.html", {"levels": levels})


@login_required
def solved_papers_subject(request, level_code, subject_slug):
    level = get_object_or_404(EducationLevel, code__iexact=level_code)
    subject = get_object_or_404(Subject, education_level=level, slug=subject_slug)

    q = request.GET.get("q", "").strip()
    questions = SolvedQuestion.objects.filter(subject=subject).select_related("topic")
    if q:
        questions = questions.filter(Q(question_text__icontains=q) | Q(paper_number__icontains=q) | Q(year__icontains=q))

    grouped = {}
    for sq in questions.order_by("paper_number", "-year", "question_number"):
        grouped.setdefault(sq.paper_number, []).append(sq)

    return render(request, "papers/solved_papers_subject.html", {
        "level": level, "subject": subject, "grouped": grouped, "q": q,
    })


# ---------------- Topical Papers ----------------

def topical_home(request):
    levels = EducationLevel.objects.prefetch_related("subjects")
    return render(request, "papers/topical_home.html", {"levels": levels})


def topical_subject(request, level_code, subject_slug):
    level = get_object_or_404(EducationLevel, code__iexact=level_code)
    subject = get_object_or_404(Subject, education_level=level, slug=subject_slug)
    topics = subject.topics.all()
    return render(request, "papers/topical_subject.html", {"level": level, "subject": subject, "topics": topics})


@login_required
def topical_quiz(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    questions = list(topic.topical_questions.all())

    if request.method == "POST":
        score = 0
        results = []
        for q in questions:
            chosen = request.POST.get(f"q{q.id}")
            is_correct = chosen == q.correct_option
            if chosen:
                TopicalAttempt.objects.create(user=request.user, question=q, selected_option=chosen)
            if is_correct:
                score += 1
            results.append({"question": q, "chosen": chosen, "is_correct": is_correct})
        return render(request, "papers/topical_results.html", {
            "topic": topic, "results": results, "score": score, "total": len(questions),
        })

    return render(request, "papers/topical_quiz.html", {"topic": topic, "questions": questions})
