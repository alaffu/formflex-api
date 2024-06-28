from django.db.models import QuerySet
from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Request, Response as DRFResponse

from api.models.model import Question, Response
from api.serializers.serializers import ResponseSerializer


def convert_to_dict_create_view_data(data):
    result_dict = {}
    for item in data:
        question_id = item["question"]
        answer = item["answer"]
        result_dict[question_id] = {"answer": answer}
    return result_dict


def validate_text_answer(answer):
    if isinstance(answer, str):
        return True
    return False


def validate_choice_answer(answer, question):
    if not isinstance(answer, int):
        return False

    if question.choices.filter(pk=answer).exists():
        print("True")
        return True
    return False


def validate_response_choice_question(questions: QuerySet, converted_data: dict):
    choice_questions = questions.filter(question_type="choice")
    if choice_questions.exists():
        choice_answers = {question.id: 0 for question in choice_questions}
        for question_id in converted_data:
            if question_id in choice_answers:
                choice_answers[question_id] += 1
                if choice_answers[question_id] > 1:
                    raise serializers.ValidationError(
                        f"Multiple choices answered for question ID: {question_id}"
                    )


class ResponseViewset(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        form_id = self.request.query_params.get("form_id")
        if form_id:
            return Response.objects.filter(question__form__pk=form_id)

        return Response.objects.all()

    def create(self, request: Request, *args, **kwargs):
        if not request.data:
            raise serializers.ValidationError({"detail": "Data is required"})

        responses_data = request.data.get("responses")
        form_id = request.data.get("form_id")

        if not form_id:
            raise serializers.ValidationError({"detail": "Form ID is required"})

        converted_data = convert_to_dict_create_view_data(responses_data)
        question_ids = list(converted_data.keys())
        questions = Question.objects.filter(pk__in=question_ids, form__pk=form_id)

        if questions.count() != len(question_ids):
            invalid_ids = set(question_ids) - set(
                questions.values_list("pk", flat=True)
            )
            raise serializers.ValidationError(
                {"detail": f"Invalid question IDs: {invalid_ids}"}
            )

        validate_response_choice_question(questions, converted_data)

        responses_to_create = []
        for question_id, obj in converted_data.items():
            question = questions.get(pk=question_id)

            if question.question_type == "text":
                if not validate_text_answer(obj["answer"]):
                    raise serializers.ValidationError(
                        {
                            "detail": f"Answer for question ID {question_id} is not a string"
                        }
                    )
                responses_to_create.append(
                    Response(
                        question=question,
                        answer_text=obj["answer"],
                        created_by=request.user,
                    )
                )

            if question.question_type == "choice":
                if not validate_choice_answer(obj["answer"], question):
                    raise serializers.ValidationError(
                        {
                            "detail": f"Answer for question ID {question_id} is not a valid choice"
                        }
                    )
                responses_to_create.append(
                    Response(
                        question=question,
                        answer_choice=obj["answer"],
                        created_by=request.user,
                    )
                )

        Response.objects.bulk_create(responses_to_create)
        return DRFResponse(
            {"message": "Responses created successfully"},
            status=status.HTTP_201_CREATED,
        )
