from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from apps.syllabus.models import EducationLevel, Subject
from .models import UserProfile


class LevelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.code


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    education_level = LevelChoiceField(
        queryset=EducationLevel.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        error_messages={"required": "Please choose your level (PSLE, JCE or BGCSE)."},
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Use the profile the post_save signal already attached to this user,
            # so the view that redirects afterwards sees the level we set here.
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            # Compulsory subjects are assigned straight away. For PSLE that is
            # every subject; JCE/BGCSE students pick their optional ones next.
            profile.apply_level(self.cleaned_data["education_level"])
        return user


class LevelForm(forms.Form):
    """Used by existing students who have no level yet, or who move up a level."""
    education_level = LevelChoiceField(
        queryset=EducationLevel.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        error_messages={"required": "Please choose your level."},
    )


class OptionalSubjectsForm(forms.Form):
    """Optional (non-compulsory) subjects for the student's level."""
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, level=None, **kwargs):
        super().__init__(*args, **kwargs)
        if level is not None:
            self.fields["subjects"].queryset = level.optional_subjects()


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio"]
        widgets = {
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
