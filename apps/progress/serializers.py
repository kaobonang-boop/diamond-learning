from rest_framework import serializers


class SubjectProgressSerializer(serializers.Serializer):
    subject = serializers.CharField()
    syllabus = serializers.IntegerField()
    notes = serializers.IntegerField()
    topical = serializers.IntegerField()
