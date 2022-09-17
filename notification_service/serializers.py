from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import MailingList


User = get_user_model()


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class MailingSerializer(ModelSerializer):

    class Meta:
        model = MailingList
        fields = '__all__'
