from rest_framework import serializers

from api.models.model import Choice, Form, Question, Response


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = "__all__"

    def get_children(self, obj):
        return QuestionSerializer(obj.children.all(), many=True).data


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = "__all__"


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = "__all__"
