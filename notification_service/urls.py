from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app = 'notification_service'
router = DefaultRouter()

router.register('mailing', viewset=views.MailingListViewSet, basename='mailing')

urlpatterns = [
    path('api/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
]
