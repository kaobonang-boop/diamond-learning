import calendar
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StudySessionForm
from .models import StudySession


@login_required
def timetable_view(request):
    view_mode = request.GET.get("view", "weekly")
    today = date.today()

    if view_mode == "monthly":
        start = today.replace(day=1)
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        end = today.replace(day=days_in_month)
    else:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

    sessions = StudySession.objects.filter(user=request.user, date__gte=start, date__lte=end).select_related("subject", "topic")

    days = []
    cursor = start
    while cursor <= end:
        days.append({"date": cursor, "sessions": [s for s in sessions if s.date == cursor]})
        cursor += timedelta(days=1)

    return render(request, "timetable/timetable.html", {
        "view_mode": view_mode, "days": days, "start": start, "end": end,
    })


@login_required
def add_session(request):
    if request.method == "POST":
        form = StudySessionForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            return redirect("timetable:timetable")
    else:
        form = StudySessionForm(user=request.user)
    return render(request, "timetable/session_form.html", {"form": form, "mode": "add"})


@login_required
def edit_session(request, session_id):
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    if request.method == "POST":
        form = StudySessionForm(request.POST, instance=session, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("timetable:timetable")
    else:
        form = StudySessionForm(instance=session, user=request.user)
    return render(request, "timetable/session_form.html", {"form": form, "mode": "edit", "session": session})


@login_required
@require_POST
def delete_session(request, session_id):
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    session.delete()
    return redirect("timetable:timetable")


@login_required
@require_POST
def complete_session(request, session_id):
    session = get_object_or_404(StudySession, pk=session_id, user=request.user)
    session.completed = not session.completed
    session.save()
    return redirect("timetable:timetable")
