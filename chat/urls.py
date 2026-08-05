from django.urls import path

from . import views


urlpatterns = [
    path("users/", views.user_list_view, name="user_list"),
    path("start/<int:user_id>/", views.start_chat_view, name="start_chat"),
    path('inbox/', views.inbox_view, name="inbox"),
    path('room/<int:conversation_id>/',views.chat_room_view, name="chat_room"),
    path('delete/<int:conversation_id>/', views.delete_chat_view, name="delete_chat"),
]