from rest_framework import viewsets
from rest_framework.views import Request, Response
from rest_framework import status

from api.models.model import Choice, Question
from api.serializers.serializers import QuestionSerializer


def create_number_question(
    data: dict,
    form_id: int,
    last_question: Question = None,
    parent_choice: Choice = None,
):
    pass  # Not implemented yet


def create_choice_question(
    data: dict,
    form_id: int,
    last_question: Question = None,
    parent_choice: Choice = None,
):
    data["form"] = form_id  # Set the form ID
    choice_question_serializer = QuestionSerializer(data=data)
    choice_question_serializer.is_valid(raise_exception=True)
    created_question_choice = choice_question_serializer.save()

    if last_question:
        created_question_choice.parent = last_question
        created_question_choice.save()

    if parent_choice:
        parent_choice.next_question = created_question_choice
        parent_choice.save()

    children_questions = data.get("choices", {})
    for choice_title, child_question in children_questions.items():
        created_question = create_question(
            child_question, form_id, created_question_choice
        )
        choice = Choice(
            text=choice_title,
            question=created_question_choice,
            next_question=created_question,
        )
        choice.save()


def create_text_question(
    data: dict,
    form_id: int,
    last_question: Question = None,
    parent_choice: Choice = None,
):
    data["form"] = form_id  # Set the form ID
    text_question_serializer = QuestionSerializer(data=data)
    text_question_serializer.is_valid(raise_exception=True)
    created_question = text_question_serializer.save()

    if parent_choice:
        parent_choice.next_question = created_question
        parent_choice.save()

    if last_question:
        created_question.parent = last_question
        created_question.save()

    child_question = data.get("question")
    if child_question:
        create_question(child_question, form_id, created_question)


def create_question(data: dict, form_id: int, last_question: Question = None):
    type_question = data.get("question_type")
    if not type_question:
        raise ValueError("Type is required")

    if type_question == "text":
        return create_text_question(data, form_id, last_question)
    elif type_question == "choice":
        return create_choice_question(data, form_id, last_question)
    elif type_question == "number":
        return create_number_question(
            data, form_id, last_question
        )  # Implement if needed


class QuestionViewset(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request: Request, *args, **kwargs):
        if request.data:
            try:
                form_id = request.data.get("form")
                if not form_id:
                    return Response(
                        {"error": "Form ID is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                create_question(request.data, form_id)
                return Response(
                    {"message": "Question created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST
        )
