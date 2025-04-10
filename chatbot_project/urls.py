from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

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
    path('api/food/', include('food_api.urls')),
    path('api/chat/', include('chatbot.urls')),
    path('api/auth/login/', obtain_auth_token, name='api_token_auth'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Frontend Views
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]