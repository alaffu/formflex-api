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


class QuestionCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        exclude = ["created_by"]


class ResponseSerializer(serializers.ModelSerializer):
    question = QuestionCommonSerializer(read_only=True)

    class Meta:
        model = Response
        fields = "__all__"


class NestedChoiceSerializer(serializers.ModelSerializer):
    next_question = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "text", "next_question"]

    def get_next_question(self, obj):
        if obj.next_question:
            return NestedQuestionSerializer(obj.next_question).data
        return None


class NestedQuestionSerializer(serializers.ModelSerializer):
    choices = NestedChoiceSerializer(many=True)
    next_question = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "title", "question_type", "choices", "next_question"]

    def get_next_question(self, obj):
        if obj.choices:
            return None

        children = obj.children.all()
        if children.exists():
            return NestedQuestionSerializer(children.first()).data
        return None
