from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView,
)
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST

from .forms import LevelForm, OptionalSubjectsForm, ProfileEditForm, RegistrationForm


def after_level_chosen_url(profile):
    """Where to send a student once their level is set: the optional-subjects
    page if their level has electives (JCE/BGCSE), otherwise the dashboard."""
    level = profile.education_level
    if level and level.optional_subjects().exists():
        return reverse("accounts:choose_subjects")
    return reverse("core:dashboard")


class DiamondLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class DiamondLogoutView(LogoutView):
    next_page = "core:home"


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Diamond Learning, {user.first_name or user.username}!")
            return redirect(after_level_chosen_url(user.profile))
        return render(request, self.template_name, {"form": form})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:edit_profile")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def choose_level(request):
    """Pick (or change) your level. Changing level resets your subjects to the
    new level's compulsory ones; picking the same level again keeps them."""
    profile = request.user.profile
    if request.method == "POST":
        form = LevelForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data["education_level"]
            if profile.education_level_id != level.id:
                profile.apply_level(level)
            return redirect(after_level_chosen_url(profile))
    else:
        form = LevelForm(initial={"education_level": profile.education_level})
    return render(request, "accounts/choose_level.html", {"form": form, "profile": profile})


@login_required
def choose_subjects(request):
    """JCE / BGCSE only: tick the optional subjects you take. Compulsory
    subjects are already in place and shown for information."""
    profile = request.user.profile
    level = profile.education_level
    if level is None:
        return redirect("accounts:choose_level")
    if not level.optional_subjects().exists():
        return redirect("core:dashboard")

    if request.method == "POST":
        form = OptionalSubjectsForm(request.POST, level=level)
        if form.is_valid():
            profile.set_optional_subjects(form.cleaned_data["subjects"])
            messages.success(request, "Your subjects are saved.")
            return redirect("core:dashboard")
    else:
        form = OptionalSubjectsForm(
            level=level,
            initial={"subjects": profile.subjects.filter(is_core=False)},
        )
    return render(request, "accounts/choose_subjects.html", {
        "form": form,
        "level": level,
        "core_subjects": level.core_subjects(),
    })


class DiamondPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
