from django.urls import path
from . import views

urlpatterns = [
    path('start-conversation/', views.start_conversation, name='start-conversation'),
    path('simulate/', views.simulate_conversations, name='simulate-conversations'),
]
