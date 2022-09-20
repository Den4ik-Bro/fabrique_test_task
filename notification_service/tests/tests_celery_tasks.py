from datetime import timedelta
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from notification_service.models import Client, MailingList, Message
from django.utils import timezone
from unittest.mock import patch
from notification_service.tasks import send_message
from notification_service.tools import data_for_send


class SendMessageTestCase(APITestCase):

    def test_send_message(self):
        mailing = MailingList.objects.create(
            start_time=timezone.now(),
            finish_time=timezone.now() + timedelta(hours=1),
            text='test'
        )
        client = Client.objects.create(phone='79997775544')
        message = Message.objects.create(client=client, mailing_list=mailing, status='not sent')
        data = {
            'id': 1,
            'text': mailing.text,
            'phone': int(client.phone)
        }
        send = send_message(data=data, mailing_id=mailing.pk)
        self.assertEqual(send, 200)
        message.refresh_from_db()
        self.assertEqual(message.status, 'sent')
