from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import MailingList, Client


class ClientSerializer(ModelSerializer):

    class Meta:
        model = Client
        fields = '__all__'


class MailingSerializer(ModelSerializer):

    class Meta:
        model = MailingList
        fields = '__all__'

    def validate(self, data):
        if data['start_time'] > data['finish_time']:
            raise serializers.ValidationError('The send date cannot be later than the end date')
        return super().validate(data)
