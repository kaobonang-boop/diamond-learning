from rest_framework import serializers
from .models import PastPaper, SolvedQuestion, TopicalQuestion


class PastPaperSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    education_level = serializers.StringRelatedField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PastPaper
        fields = ["id", "subject", "education_level", "year", "paper_number", "file_url"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class SolvedQuestionSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()

    class Meta:
        model = SolvedQuestion
        fields = ["id", "subject", "year", "paper_number", "question_number", "question_text", "step_by_step_explanation", "final_answer"]


class TopicalQuestionSerializer(serializers.ModelSerializer):
    topic = serializers.StringRelatedField()

    class Meta:
        model = TopicalQuestion
        fields = ["id", "topic", "question_text", "option_a", "option_b", "option_c", "option_d"]
