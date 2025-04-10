from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('health-check/', views.health_check, name='health-check'),
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('chat/start/', views.start_conversation, name='chat-start'),
    path('chat/simulate/', views.simulate_conversations, name='simulate'),
    path('vegetarian-list/', views.vegetarian_list, name='vegetarian-list'),
    
    # New bonus feature endpoints
    path('analytics/', views.analytics_dashboard, name='analytics-dashboard'),
    path('categories/', views.food_categories, name='food-categories'),
    path('health-analysis/', views.health_analysis, name='health-analysis'),
    path('export/', views.export_data, name='export-data'),
    path('recommendations/', views.food_recommendations, name='food-recommendations'),
]