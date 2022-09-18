import os
from core.celery import app
import requests
from .models import Message


@app.task(bind=True)
def send_message(self, data):
    if data['start'] <= data['now'] <= data['stop']:
        token = os.environ.get('TOKEN')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        url = f'https://probe.fbrq.cloud/v1/send/{data["id"]}'
        try:
            response = requests.post(url, json=data, headers=headers)
        except ConnectionError as error:
            raise self.retry(exc=error)
        if response.status_code == 200:
            Message.objects.filter(pk=data['id']).update(status='sent')
        return response.status_code
    else:
        self.retry(countdown=120)

    # mailing = MailingList.objects.get(pk=mailing_id)
    # users = User.objects.filter(
    #     Q(tag=mailing.user_filter_tag) | Q(mobile_operator_code=mailing.user_filter_phone_code)
    # )
    # now = datetime.datetime.now()
    # if mailing.start_time <= now <= mailing.finish_time:
    #     messages = [Message(user=user.pk, mailing_list=mailing.pk, status='not sent') for user in users]
    #     Message.objects.bulk_create(messages)
    #     for message in messages:
    #         token = os.environ.get('TOKEN')
    #         data = {
    #             'text': message.mailing_list.text,
    #             'id': message.pk,
    #             'phone': int(message.user.phone)
    #         }
    #         headers = {
    #             'Authorization': f'Bearer {token}',
    #             'Content-Type': 'application/json'
    #         }
    #         url = f'https://probe.fbrq.cloud/v1/send/{data["id"]}'
    #         try:
    #             response = requests.post(url, json=data, headers=headers)
    #         except requests.exceptions.RequestException as errors:
    #             raise self.retry(exc=errors)
    #         if response.status_code == 200:
    #             message.status = 'SENT'
    #     return True
    # else:
    #     return self.retry(countdown=60)
