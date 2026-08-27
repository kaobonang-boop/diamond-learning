from django import forms
from .models import StudySession


class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ["subject", "topic", "date", "start_time", "end_time", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, "profile"):
            self.fields["subject"].queryset = user.profile.subjects.all()
        self.fields["topic"].queryset = self.fields["topic"].queryset.none()
        if "subject" in self.data:
            try:
                subject_id = int(self.data.get("subject"))
                from apps.syllabus.models import Topic
                self.fields["topic"].queryset = Topic.objects.filter(subject_id=subject_id)
            except (TypeError, ValueError):
                pass
        elif self.instance.pk:
            self.fields["topic"].queryset = self.instance.subject.topics.all()
