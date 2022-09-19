from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import MailingList, Message, Client
from .serializers import MailingSerializer, ClientSerializer
from rest_framework.permissions import IsAuthenticated
from .tools import data_for_send


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MailingListViewSet(ModelViewSet):
    queryset = MailingList.objects.all()
    serializer_class = MailingSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mailing = serializer.save()
            data_for_send(mailing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def detail_mailing_info(self, request, pk):
        mailing = self.get_object()
        messages = Message.objects.select_related('user').select_related('mailing_list')\
                                                         .filter(mailing_list=self.get_object())
        data = {
            'start_time': timezone.localtime(mailing.start_time),
            'finish_time': timezone.localtime(mailing.finish_time),
            'count_sent_messages': messages.count(),
            'count_status_sent': messages.filter(status='sent').count(),
            'count_status_not_sent': messages.filter(status='not sent').count(),
            'user_filter_tag': mailing.user_filter_tag,
            'user_filter_phone_code': mailing.user_filter_phone_code,
            'clients': [message.client.phone for message in mailing.message_set.all()],
            'message_text': mailing.text
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def full_statistics_for_mailings(self, request):
        mailing_lists = self.queryset
        result = []
        for mailing in mailing_lists:
            message = Message.objects.select_related('user').select_related('mailing_list')\
                                                .filter(mailing_list=mailing)
            message_info = {
                'mailing_id': mailing.pk,
                'count_messages': message.count(),
                'count_status_sent': message.filter(status='sent').count(),
                'count_status_not_sent': message.filter(status='not sent').count(),
            }
            result.append(message_info)
        return Response({'full_statistic': result}, status=status.HTTP_200_OK)
