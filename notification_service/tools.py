from django.db.models import Q
from .models import Client, Message
from .tasks import send_message


def data_for_send(mailing):
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
        }
        send_message.delay(data=data, mailing_id=mailing.pk)
