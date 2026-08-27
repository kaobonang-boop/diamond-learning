from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from apps.syllabus.models import EducationLevel, Subject
from .models import UserProfile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    education_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(), empty_label=None, widget=forms.RadioSelect
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(), required=False, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "education_level", "subjects", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate subject choices for whichever level is posted/initial, so the
        # checkbox list narrows to the chosen level (handled client-side in the
        # template; server-side we just accept any valid subject for validation).
        self.fields["subjects"].queryset = Subject.objects.select_related("education_level")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.education_level = self.cleaned_data["education_level"]
            profile.save()
            profile.subjects.set(self.cleaned_data["subjects"])
        return user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ["education_level", "subjects", "avatar", "bio"]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple,
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save()
        if commit:
            profile.save()
            self.save_m2m()
        return profile
