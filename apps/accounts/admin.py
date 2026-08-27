from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "education_level")
    list_filter = ("education_level",)
    filter_horizontal = ("subjects",)
