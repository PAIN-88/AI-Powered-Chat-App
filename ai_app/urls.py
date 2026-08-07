from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ai_chat_view, name='ai_chat'),
    path('summarize/<int:conversation_id>/', views.summarize_chat, name='summarize_chat'),
    path('summary-page/<int:conversation_id>/', views.summary_page_view, name='summary_page'),
    path('', views.ai_chat_page, name='ai_chat_page'),
]