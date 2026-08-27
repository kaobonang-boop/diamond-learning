from rest_framework import serializers
from .models import EducationLevel, Subject, Topic, TopicProgress


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ["id", "code", "name", "description", "order"]


class SubjectSerializer(serializers.ModelSerializer):
    education_level = serializers.StringRelatedField()

    class Meta:
        model = Subject
        fields = ["id", "name", "slug", "description", "education_level"]


class TopicSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    objectives = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ["id", "title", "slug", "description", "objectives", "subject", "order"]

    def get_objectives(self, obj):
        return obj.objectives_list()


class TopicProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicProgress
        fields = ["id", "topic", "status", "updated_at"]
        read_only_fields = ["updated_at"]
