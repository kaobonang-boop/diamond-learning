from django.contrib import admin
from .models import Note, FavouriteNote, NoteReadProgress


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "last_updated")
    list_filter = ("topic__subject__education_level", "topic__subject")
    search_fields = ("title", "content")


admin.site.register(FavouriteNote)
admin.site.register(NoteReadProgress)
