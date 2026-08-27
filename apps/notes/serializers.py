from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    topic = serializers.StringRelatedField()

    class Meta:
        model = Note
        fields = ["id", "title", "content", "subject", "topic", "date_created", "last_updated"]
