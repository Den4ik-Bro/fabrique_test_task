import os

import celery
from core.celery import app
import requests
from django.utils import timezone

from .models import Message, MailingList


@app.task(bind=True)
def send_message(self, data, mailing_id):
    mailing = MailingList.objects.get(pk=mailing_id)
    if mailing.start_time.timetz() <= timezone.now().timetz() <= mailing.finish_time.timetz():
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
        try:
            self.retry(eta=mailing.start_time)
        except celery.exceptions.MaxRetriesExceededError:
            return False


