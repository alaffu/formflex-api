from rest_framework import viewsets

from api.models.model import Choice
from api.serializers.serializers import ChoiceSerializer


class ChoiceViewset(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
