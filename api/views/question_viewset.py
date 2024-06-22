from rest_framework import viewsets
from rest_framework.views import Request, Response

from api.models.model import Choice, Question
from api.serializers.serializers import QuestionSerializer


def create_number_question(data: dict):
    pass


def create_choice_question(
    data: dict, last_question: Question = None, parent_choice: Choice = None
):
    choice_question_serializer = QuestionSerializer(data=data)
    choice_question_serializer.is_valid()
    created_question_choice = choice_question_serializer.save()

    if last_question:
        created_question_choice.parent = last_question
        created_question_choice.save()

    if parent_choice:
        parent_choice.next_question = created_question_choice
        parent_choice.save()

    children_questions: dict | None = data.get("choices")
    if not children_questions:
        return

    for choice_title, child_question in children_questions.items():
        create_question(child_question)
        question = QuestionSerializer(data=child_question)
        question.is_valid(raise_exception=True)
        created_question = question.save()

        choice = Choice()
        choice.text = choice_title
        choice.question = last_question
        choice.next_question = created_question


def create_text_question(
    data: dict, last_question: Question = None, parent_choice: Choice | None = None
):
    text_question_serializer = QuestionSerializer(data=data)
    text_question_serializer.is_valid()
    created_question: Question = text_question_serializer.save()

    parent_choice.next_question = created_question
    parent_choice.save()

    if last_question:
        created_question.parent = last_question
        created_question.save()

    child_question = data.get("question")
    if child_question:
        create_question(child_question, created_question)


def create_question(data: dict, last_question: Question = None):
    type_question = data.get("type")
    if not type_question:
        raise Exception("Type is required")

    if type_question == "text":
        create_question(data, last_question)
    elif type_question == "choice":
        create_choice_question(data, last_question)


class QuestionViewset(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request: Request, *args, **kwargs):
        if request.data:
            create_question(request.data)
        return Response({"message": "Hello World"})
