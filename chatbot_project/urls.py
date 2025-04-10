from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your-email@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('food_api.urls')),  # Include food_api urls under api/ prefix
    path('chatbot/', include('chatbot.urls')),  # Include chatbot urls under chatbot/ prefix
    
    # Swagger documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]