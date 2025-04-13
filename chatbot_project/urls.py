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
    path('api/food/', include('food_api.urls')), # Keep your food API urls
    path('api/chat/', include('chatbot.urls')),  # Keep your chatbot API urls

    # Frontend/Authentication URLs using chatbot_project.views
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_view, name='chat'), # Placeholder for chat UI page

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Re-enable Swagger documentation URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]