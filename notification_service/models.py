from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class MailingList(models.Model):
    start_time = models.DateTimeField(verbose_name='start time')
    text = models.TextField(verbose_name='text')
    user_filter = models.CharField(max_length=100, verbose_name='tag or cod user filter')
    finish_time = models.DateTimeField(verbose_name='finish time')

    def __str__(self):
        return f'mailing list {self.start_time} - {self.finish_time}'

    def clean(self):
        if self.start_time > self.finish_time:
            raise ValidationError('The send date cannot be later than the end date')


class Meta:
    verbose_name = 'Mailing list'
    verbose_name_plural = 'Mailing lists'


class User(AbstractUser):
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(
            regex=r'^7\d{10}$',
            message='Wrong number format. Number format should be 7XXXXXXXXX (X - number from 0 to 9)'
        )],
        verbose_name='phone number'
    )
    mobile_operator_code = models.PositiveSmallIntegerField(verbose_name='mobile operator code')
    tag = models.CharField(max_length=100, verbose_name='tag', blank=True)
    time_zone = models.CharField(max_length=100, verbose_name='time zone', blank=True)

    def save(self, *args, **kwargs):
        self.mobile_operator_code = self.phone[1:4]
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Message(models.Model):
    CHOICES = [
        ('sent','SENT'),
        ('not sent', 'NOT SENT')
    ]
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=CHOICES, max_length=8, verbose_name='status sending')
    mailing_list = models.ForeignKey(MailingList, on_delete=models.PROTECT, verbose_name='mailing list')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='user')

    def __str__(self):
        return f'message {self.created_date} for {self.user}'

    def clean(self):
        if self.status not in self.CHOICES:
            raise ValidationError('Wrong status')

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
