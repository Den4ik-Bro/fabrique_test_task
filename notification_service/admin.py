from django.contrib import admin
from . import models


admin.site.register(models.User)
admin.site.register(models.MailingList)
admin.site.register(models.Message)
