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


class DiamondPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class DiamondPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class DiamondPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class DiamondPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class DiamondPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


@require_POST
def ajax_login(request):
    """Powers the sign-in popup. Same validation as the real login page,
    just returns JSON instead of a redirect so the modal can stay open."""
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
        return JsonResponse({"success": True, "redirect_url": reverse_lazy("core:dashboard").__str__()})
    return JsonResponse({"success": False, "error": "Incorrect username or password."}, status=400)


@require_POST
def ajax_register(request):
    """Powers the sign-up popup. Reuses RegistrationForm so it's the exact
    same validation and account-creation logic as the full page."""
    form = RegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({"success": True, "redirect_url": after_level_chosen_url(user.profile)})
    # Flatten form errors into one readable message for the modal's single error box.
    first_error = next(iter(form.errors.values()))[0]
    return JsonResponse({"success": False, "error": first_error}, status=400)
