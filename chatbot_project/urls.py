from django.contrib import admin
from django.urls import path, include
# Temporarily comment out problematic imports
# from rest_framework.authtoken.views import obtain_auth_token
# from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# Re-enable schema_view definition
schema_view = get_schema_view(
    openapi.Info(
        title="Food Chatbot API",
        default_version='v1',
        description="""
        A sophisticated AI-powered Food Chatbot API that provides personalized food recommendations
        and analytics. Features include:

        * User Authentication & Authorization
        * AI-powered Food Preference Analysis
        * Dietary Preference Tracking (Vegetarian/Vegan)
        * Food Category Analytics
        * Health Score Analysis
        * Personalized Food Recommendations
        * Data Export Capabilities
        * Real-time Chat Simulation
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API URLs
    path('api/food/', include('food_api.urls')), 
    path('api/chat/', include('chatbot.urls')),  

    # Frontend/Authentication URLs
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('chat/', views.chat_view, name='chat'),
    
    # Authentication URLs with proper redirects
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', next_page='chat'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', next_page='chat'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('login/chat/', lambda request: redirect('chat'), name='login_chat_redirect'),

    # Re-enable Swagger documentation URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]