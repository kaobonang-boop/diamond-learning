def site_context(request):
    from apps.syllabus.models import EducationLevel
    return {
        "SITE_NAME": "Diamond Learning",
        "SITE_TAGLINE": "Pressure makes diamonds.",
        "AUTH_MODAL_LEVELS": EducationLevel.objects.all(),
    }
