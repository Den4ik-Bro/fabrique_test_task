import os
import logging
import celery
from core.celery import app
import requests
from django.utils import timezone
from .models import Message, MailingList
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

# logger = logging.getLogger(__name__)


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
            logger.error(f'mailing_id: {mailing_id}, error: ConnectionError')
            raise self.retry(exc=error)
        if response.status_code == 200:
            Message.objects.filter(pk=data['id']).update(status='sent')
            logger.info(f'message: {data["id"]}, status: sent, text: {mailing.text}')
        return response.status_code
    else:
        try:
            self.retry(eta=mailing.start_time)
            logger.info(f'mailing_id: {mailing.pk} will be launched in {mailing.start_time}')
        except celery.exceptions.MaxRetriesExceededError:
            logger.error(f'mailing_id: {mailing.pk}, MaxRetriesExceededError')
            return False


