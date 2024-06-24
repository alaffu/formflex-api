from rest_framework import serializers, viewsets
from rest_framework.views import Request, Response
from rest_framework import status
from rest_framework.decorators import action

from api.models.model import Choice, Form, Question
from api.serializers.serializers import QuestionCommonSerializer, QuestionSerializer


class NestedChoiceSerializer(serializers.ModelSerializer):
    next_question = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["text", "next_question"]

    def get_next_question(self, obj):
        if obj.next_question:
            return NestedQuestionSerializer(obj.next_question).data
        return None


class NestedQuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["title", "question_type", "choices", "question"]

    def get_choices(self, obj):
        choices = obj.choices.all()
        return NestedChoiceSerializer(choices, many=True).data

    def get_question(self, obj):
        children = obj.children.all()
        if children.exists():
            return NestedQuestionSerializer(children.first()).data
        return None


def create_number_question(
    data: dict,
    form_id: int,
    last_question: Question | None = None,
    parent_choice: Choice | None = None,
):
    data["form"] = form_id
    question_serializer = QuestionSerializer(data=data)
    question_serializer.is_valid(raise_exception=True)
    created_question = question_serializer.save()

    if last_question:
        created_question.parent = last_question
        created_question.save()

    if parent_choice:
        parent_choice.next_question = created_question
        parent_choice.save()


def create_choice_question(
    data: dict,
    form_id: int,
    last_question: Question | None = None,
    parent_choice: Choice | None = None,
):
    data["form"] = form_id
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
    last_question: Question | None = None,
    parent_choice: Choice | None = None,
):
    data["form"] = form_id
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


def create_question(
    data: dict,
    form_id: int,
    last_question: Question | None = None,
    parent_choice: Choice | None = None,
):
    type_question = data.get("question_type")
    if not type_question:
        raise ValueError("Type is required")

    if type_question == "text":
        return create_text_question(data, form_id, last_question, parent_choice)
    elif type_question == "choice":
        return create_choice_question(data, form_id, last_question, parent_choice)
    elif type_question == "number":
        return create_number_question(data, form_id, last_question, parent_choice)


class QuestionViewset(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionCommonSerializer

    def create(self, request: Request, *args, **kwargs):
        form_id = request.data.get("form")
        if not form_id:
            raise serializers.ValidationError("Form ID is required")

        form = Form.objects.get(pk=form_id)
        if Question.objects.filter(form=form, parent__isnull=True).exists():
            raise serializers.ValidationError(
                "A root question already exists for this form"
            )

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
                    {"message": "Question tree created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": "No data provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request: Request, *args, **kwargs):
        form_id = request.query_params.get("form_id")
        if not form_id:
            return Response(
                {"error": "Form ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        questions = Question.objects.filter(form_id=form_id, parent__isnull=True)
        if questions.exists():
            question = questions.first()
            print(question.title)
            return Response(
                NestedQuestionSerializer(question).data, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "No root questions found for the given form"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(detail=False, methods=["get"])
    def roots(self, request: Request, *args, **kwargs):
        questions = Question.objects.filter(form_id__isnull=False, parent__isnull=True)
        if questions.exists():
            serializer = QuestionCommonSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "No root questions found for the given form"},
            status=status.HTTP_404_NOT_FOUND,
        )
