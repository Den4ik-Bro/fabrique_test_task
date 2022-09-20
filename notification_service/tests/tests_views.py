from datetime import timedelta
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from notification_service.models import Client, MailingList, Message
from django.utils import timezone


class ClientViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        users = [Client(phone=f'7999111223{num}') for num in range(1, 6)]
        Client.objects.bulk_create(users)
        self.user = Client.objects.first()

    def test_list(self):
        url = reverse('client-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Client.objects.count())

    def test_detail(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], 1)
        self.assertEqual(response.json()['phone'], '79991112231')

    def test_post(self):
        url = reverse('client-list')
        data = {'phone': '70003734646'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['phone'], '70003734646')
        self.assertEqual(response.json()['mobile_operator_code'], '000')

    def test_put(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        data = {
            "id": 1,
            "phone": "79991112231",
            "mobile_operator_code": "999",
            "tag": "test",
            "time_zone": ""
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tag, 'test')
        data = {
            "tag": "test"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch(self):
        url = reverse('client-detail', kwargs={'pk': self.user.pk})
        data = {
            "tag": "test_patch"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tag, 'test_patch')


class MailingListViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        mailing_lists = [
            MailingList(start_time=timezone.now(), finish_time=timezone.now() + timedelta(hours=1), text='test')
            for _ in range(3)
        ]
        MailingList.objects.bulk_create(mailing_lists)
        self.mailing = MailingList.objects.first()

    def test_list(self):
        url = reverse('mailing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], MailingList.objects.count())

    def test_detail(self):
        url = reverse('mailing-detail', kwargs={'pk': self.mailing.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.mailing.pk)

    def test_post(self):
        url = reverse('mailing-list')
        data = {
            'start_time': timezone.now(),
            'finish_time': timezone.now() + timedelta(hours=3),
            'text': 'text',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_detail_mailing_info(self):
        clients = [Client(phone=f'7999888776{num}') for num in range(1, 4)]
        Client.objects.bulk_create(clients)
        messages = [
            Message(client=client, mailing_list=self.mailing, status='not sent') for client in Client.objects.all()
        ]
        Message.objects.bulk_create(messages)

        url = reverse('mailing-detail-mailing-info', kwargs={'pk': self.mailing.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), {
                'start_time': '2022-09-20T22:23:35.175520+03:00',
                'finish_time': '2022-09-20T23:23:35.175535+03:00',
                'count_sent_messages': 3,
                'count_status_sent': 0,
                'count_status_not_sent': 3,
                'user_filter_tag': None,
                'user_filter_phone_code': None,
                'clients': ['79998887761', '79998887762', '79998887763'],
                'message_text': 'test'
            }
        )

    def test_full_statistics_for_mailings(self):
        clients = [Client(phone=f'7999888776{num}') for num in range(1, 4)]
        Client.objects.bulk_create(clients)
        messages = [
            Message(client=client, mailing_list=self.mailing, status='not sent') for client in Client.objects.all()
        ]
        Message.objects.bulk_create(messages)

        url = reverse('mailing-full-statistics-for-mailings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()['full_statistic'][0], {
                'mailing_id': 1,
                'count_messages': 3,
                'count_status_sent': 0,
                'count_status_not_sent': 3
            }
        )
