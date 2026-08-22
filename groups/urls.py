from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_group_view, name='create_group'),
    path('inbox/', views.group_inbox_view, name='group_inbox'),
    path('room/<int:group_id>/', views.group_room_view, name='group_room'),
    path('add/<int:group_id>/', views.add_group_member_view, name='add_group_member'),
    path('remove/<int:group_id>/<int:user_id>/', views.remove_group_member_view, name='remove_group_member'),
    path('delete/<int:group_id>/', views.delete_group_view, name='delete_group'),
]