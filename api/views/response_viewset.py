from rest_framework import viewsets

from api.models.model import Response
from api.serializers.serializers import ResponseSerializer


class ResponseViewset(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
