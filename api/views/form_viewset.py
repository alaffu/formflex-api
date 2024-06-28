from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response as DRFResponse

from api.models.model import Form, Question, Response
from api.serializers.serializers import FormSerializer


class FormViewset(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

    @action(detail=True, methods=["get"], url_path="answers_summary")
    def answers_summary(self, request, pk=None):
        form = self.get_object()
        questions = Question.objects.filter(form=form)
        summary = []

        for question in questions:
            answers_count = Response.objects.filter(question=question).count()
            people_count = (
                Response.objects.filter(question=question)
                .values("created_by")
                .distinct()
                .count()
            )
            summary.append(
                {
                    "question": question.title,
                    "answers_count": answers_count,
                    "people_count": people_count,
                }
            )

        return DRFResponse(summary)
