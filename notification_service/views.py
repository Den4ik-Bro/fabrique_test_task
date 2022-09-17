from django.contrib.auth import get_user_model
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from .models import MailingList
from .serializers import MailingSerializer
from rest_framework.permissions import IsAuthenticated


User = get_user_model()

class MailingListViewSet(ModelViewSet):
    queryset = MailingList.objects.all()
    serializer_class = MailingSerializer
    permission_classes = [IsAuthenticated,]
