from rest_framework.serializers import ModelSerializer
from .models import MailingList


class MailingSerializer(ModelSerializer):

    class Meta:
        model = MailingList
        field = '__all__'
