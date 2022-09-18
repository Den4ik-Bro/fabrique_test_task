import datetime
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import MailingList, Message, Client
from .serializers import MailingSerializer, ClientSerializer
from rest_framework.permissions import IsAuthenticated
from .tasks import send_message


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

            clients = Client.objects.filter(
                Q(tag=mailing.user_filter_tag) | Q(mobile_operator_code=mailing.user_filter_phone_code)
            )
            messages = [Message(client=client, mailing_list=mailing, status='not sent') for client in clients]
            Message.objects.bulk_create(messages)
            for message in Message.objects.filter(mailing_list=mailing):
                data = {
                    'id': message.pk,
                    'text': mailing.text,
                    'phone': int(message.client.phone),
                    'start': mailing.start_time,
                    'stop': mailing.finish_time,
                    'now': datetime.datetime.now(),
                }
                send_message.delay(data=data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def mailing_info(self, request, pk): # хз оставлять или нет, подумать...
        messages = Message.objects.select_related('user').select_related('mailing_list')\
                                                .filter(mailing_list=self.get_object())
        data = {
            'count_sent_messages': messages.count(),
            'count_status_sent': messages.filter(status='sent').count(),
            'count_status_not_sent': messages.filter(status='not sent').count(),
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        mailing_list = self.queryset
        result = []
        for mailing in mailing_list:
            message = Message.objects.select_related('user').select_related('mailing_list')\
                                                .filter(mailing_list=mailing)
            message_info = {
                'mailing_id': mailing.pk,
                'text_message': mailing.text,
                'user_filter_tag': mailing.user_filter_tag,
                'user_filter_phone_code': mailing.user_filter_phone_code,
                'count_messages': message.count(),
                'count_sent_messages': message.count(),
                'count_status_sent': message.filter(status='sent').count(),
                'count_status_not_sent': message.filter(status='not sent').count(),
            }
            result.append(message_info)
        return Response({'full_statistic': result}, status=status.HTTP_200_OK)
