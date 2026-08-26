from django.urls import path
from .import views

urlpatterns = [
    path('list/', views.notification_list_view, name = 'notification_list'),
    path('read<int:notification_id>/', views.mark_notification_read_view, name='mark_notification_read'),
    path('read-all/', views.mark_all_read_view, name='mark_all_notification_read'),
    path('save-subscription/', views.save_push_subscription_view, name='save_push_subscription'),
]