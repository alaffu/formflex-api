from rest_framework import viewsets

from api.models.model import Form
from api.serializers.serializers import FormSerializer


class FormViewset(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
