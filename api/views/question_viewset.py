from rest_framework import viewsets
from rest_framework.views import Request, Response

from api.models.model import Question
from api.serializers.serializers import QuestionSerializer


class QuestionViewset(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request: Request, *args, **kwargs):
        print(request.data)
        return Response({"message": "Hello World"})
