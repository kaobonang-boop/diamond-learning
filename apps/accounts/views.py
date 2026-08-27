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
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, ProfileEditForm


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
            return redirect("core:dashboard")
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
        return JsonResponse({"success": True, "redirect_url": reverse_lazy("core:dashboard").__str__()})
    # Flatten form errors into one readable message for the modal's single error box.
    first_error = next(iter(form.errors.values()))[0]
    return JsonResponse({"success": False, "error": first_error}, status=400)
