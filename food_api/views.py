from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from openai import OpenAI, RateLimitError
from django.conf import settings
from .models import Conversation, FoodPreference, FoodCategory, Food, Analytics, ChatHistory
import json
from django.db.models import Count, Avg
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from collections import Counter
from rest_framework.reverse import reverse
import random
import logging

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return auth token.
    
    This endpoint allows new users to register with the system by providing
    a username and password.
    
    Parameters:
        username (string): Required. Unique username for the new account.
        password (string): Required. Password for the new account.
        
    Returns:
        token: Authentication token for the new user
        user_id: ID of the newly created user
        username: Username of the new user
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return auth token.
    
    This endpoint authenticates existing users and returns a token 
    for use in subsequent API calls.
    
    Parameters:
        username (string): Required. The user's username.
        password (string): Required. The user's password.
        
    Returns:
        token: Authentication token for the user
        user_id: ID of the user
        username: Username of the user
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = User.objects.get(username=username)
        
        if not user.check_password(password):
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint"""
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint showing all available endpoints for the Food Chatbot API
    """
    return Response({
        'message': 'Welcome to Food Chatbot API',
        'documentation': {
            'description': 'This API provides access to food preferences data from simulated conversations with ChatGPT',
            'authentication': {
                'step1': 'Register a new account using POST /api/register/ with {"username": "your_username", "password": "your_password"}',
                'step2': 'Login using POST /api/login/ with the same credentials to get your token',
                'step3': 'Use the token in subsequent requests by adding header: Authorization: Token your_token_here'
            }
        },
        'public_endpoints': {
            'register': {
                'url': reverse('register', request=request),
                'method': 'POST',
                'body': {'username': 'string', 'password': 'string'},
                'description': 'Create a new user account',
                'authentication': 'Not required'
            },
            'login': {
                'url': reverse('login', request=request),
                'method': 'POST',
                'body': {'username': 'string', 'password': 'string'},
                'description': 'Login to get authentication token',
                'authentication': 'Not required'
            },
            'health_check': {
                'url': reverse('health-check', request=request),
                'method': 'GET',
                'description': 'Check if API is running',
                'authentication': 'Not required'
            }
        },
        'data_endpoints': {
            'vegetarian_list': {
                'url': reverse('vegetarian-list', request=request),
                'method': 'GET',
                'description': 'Get list of vegetarian/vegan users and their food preferences',
                'parameters': {
                    'type': 'Query parameter to filter results',
                    'options': ['all', 'vegetarian', 'vegan'],
                    'example': '/api/vegetarian-list/?type=vegan'
                },
                'authentication': 'Required'
            },
            'analytics': {
                'url': reverse('analytics-dashboard', request=request),
                'method': 'GET',
                'description': 'Get analytics about food preferences, dietary choices, and popular foods',
                'parameters': {
                    'days': 'Number of days to analyze (default: 7)',
                    'example': '/api/analytics/?days=30'
                },
                'authentication': 'Required'
            },
            'food_categories': {
                'url': reverse('food-categories', request=request),
                'method': 'GET',
                'description': 'Get statistics about food categories including vegetarian/vegan options',
                'authentication': 'Required'
            },
            'export_data': {
                'url': reverse('export-data', request=request),
                'method': 'GET',
                'description': 'Export all food preference data as CSV',
                'authentication': 'Required'
            }
        },
        'simulation_endpoints': {
            'chat_start': {
                'url': reverse('chat-start', request=request),
                'method': 'POST',
                'description': 'Start a single conversation about food preferences',
                'authentication': 'Not required'
            },
            'simulate': {
                'url': reverse('simulate', request=request),
                'method': 'POST',
                'description': 'Simulate multiple conversations (up to 100)',
                'body': {'count': 'number (default: 100)'},
                'authentication': 'Required'
            }
        },
        'analysis_endpoints': {
            'health_analysis': {
                'url': reverse('health-analysis', request=request),
                'method': 'GET',
                'description': 'Get health analysis of food choices',
                'authentication': 'Required'
            },
            'recommendations': {
                'url': reverse('food-recommendations', request=request),
                'method': 'GET',
                'description': 'Get personalized food recommendations',
                'parameters': {
                    'conversation_id': 'ID of the conversation to base recommendations on',
                    'example': '/api/recommendations/?conversation_id=123'
                },
                'authentication': 'Required'
            }
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def start_conversation(request):
    """Start a conversation with ChatGPT to ask about favorite foods"""
    try:
        # Create mock food preferences data
        foods = ["pizza", "sushi", "chocolate cake"]
        is_vegetarian = random.choice([True, False])
        is_vegan = is_vegetarian and random.choice([True, False])
        
        response_data = {
            "foods": foods,
            "is_vegetarian": is_vegetarian,
            "is_vegan": is_vegan
        }
        
        # Create a new conversation
        conversation = Conversation.objects.create(
            is_vegetarian=response_data.get('is_vegetarian', False),
            is_vegan=response_data.get('is_vegan', False)
        )
        
        # Store food preferences
        for food in response_data.get('foods', []):
            FoodPreference.objects.create(
                conversation=conversation,
                food_name=food
            )
        
        return Response({
            "conversation_id": conversation.id,
            "response": response_data
        })
    except Exception as e:
        return Response({
            "error": str(e),
            "note": "An error occurred while processing your request."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def simulate_conversations(request):
    """
    Simulate multiple conversations between two ChatGPT instances about food preferences.
    """
    try:
        # Cleanup old conversations first
        try:
            Conversation.objects.all().delete()
            logging.info("Cleaned up old conversations")
        except Exception as e:
            logging.error(f"Error cleaning up old conversations: {str(e)}")

        # Validate count parameter
        try:
            count = int(request.data.get('count', 100))
            if count <= 0:
                return Response({
                    "error": "Count must be greater than 0"
                }, status=status.HTTP_400_BAD_REQUEST)
            count = min(count, 100)  # Limit to maximum 100
        except ValueError:
            return Response({
                "error": "Invalid count parameter"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Pre-defined diverse food combinations
        food_combinations = [
            {
                "foods": ["Margherita Pizza", "Caesar Salad", "Tiramisu"],
                "is_vegetarian": True,
                "is_vegan": False,
                "explanation": "I love Italian cuisine with a mix of savory and sweet."
            },
            {
                "foods": ["Tofu Stir-fry", "Quinoa Bowl", "Vegan Ice Cream"],
                "is_vegetarian": True,
                "is_vegan": True,
                "explanation": "Plant-based foods that are both healthy and delicious."
            },
            {
                "foods": ["Grilled Salmon", "Greek Salad", "Dark Chocolate"],
                "is_vegetarian": False,
                "is_vegan": False,
                "explanation": "A balanced combination of protein, fresh vegetables, and a sweet treat."
            },
            {
                "foods": ["Falafel Wrap", "Hummus", "Baklava"],
                "is_vegetarian": True,
                "is_vegan": True,
                "explanation": "Middle Eastern cuisine offers amazing vegetarian options."
            },
            {
                "foods": ["Sushi Rolls", "Miso Soup", "Green Tea Ice Cream"],
                "is_vegetarian": False,
                "is_vegan": False,
                "explanation": "Japanese cuisine provides a perfect balance of flavors."
            },
            {
                "foods": ["Black Bean Burrito", "Guacamole", "Churros"],
                "is_vegetarian": True,
                "is_vegan": True,
                "explanation": "Mexican food with a vegetarian twist."
            },
            {
                "foods": ["Pad Thai", "Spring Rolls", "Mango Sticky Rice"],
                "is_vegetarian": False,
                "is_vegan": False,
                "explanation": "Thai food offers an exciting mix of sweet and savory."
            },
            {
                "foods": ["Mushroom Risotto", "Caprese Salad", "Panna Cotta"],
                "is_vegetarian": True,
                "is_vegan": False,
                "explanation": "Classic Italian vegetarian dishes that are rich in flavor."
            },
            {
                "foods": ["Beyond Burger", "Sweet Potato Fries", "Coconut Sorbet"],
                "is_vegetarian": True,
                "is_vegan": True,
                "explanation": "Modern vegan alternatives that are just as satisfying."
            },
            {
                "foods": ["Chicken Tikka Masala", "Naan Bread", "Mango Lassi"],
                "is_vegetarian": False,
                "is_vegan": False,
                "explanation": "Indian cuisine with a perfect blend of spices."
            }
        ]

        # Bulk create conversations and preferences
        conversations = []
        food_preferences = []
        results = []
        
        for i in range(count):
            # Get random food combination
            response_data = random.choice(food_combinations)
            
            # Create conversation object
            conversation = Conversation(
                is_vegetarian=response_data['is_vegetarian'],
                is_vegan=response_data['is_vegan']
            )
            conversations.append(conversation)
            
            # Store result
            results.append({
                "foods": response_data['foods'],
                "is_vegetarian": response_data['is_vegetarian'],
                "is_vegan": response_data['is_vegan'],
                "explanation": response_data['explanation']
            })

        # Bulk create conversations
        created_conversations = Conversation.objects.bulk_create(conversations)
        
        # Create food preferences
        for idx, conversation in enumerate(created_conversations):
            response_data = results[idx]
            for food in response_data['foods']:
                food_preferences.append(
                    FoodPreference(
                        conversation=conversation,
                        food_name=food
                    )
                )
        
        # Bulk create food preferences
        FoodPreference.objects.bulk_create(food_preferences)
        
        # Calculate statistics
        total_vegetarian = sum(1 for r in results if r['is_vegetarian'])
        total_vegan = sum(1 for r in results if r['is_vegan'])
        
        return Response({
            "message": f"Successfully simulated {count} conversations",
            "statistics": {
                "total_conversations": count,
                "vegetarian_percentage": round((total_vegetarian / count * 100), 2),
                "vegan_percentage": round((total_vegan / count * 100), 2)
            },
            "results": results[:5]  # Return first 5 results as sample
        })
        
    except Exception as e:
        logging.error(f"Simulation error: {str(e)}")
        return Response({
            "error": str(e),
            "note": "An error occurred during simulation."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def cleanup_old_conversations():
    """Clean up old conversations to prevent database bloat"""
    try:
        total_count = Conversation.objects.count()
        if total_count > 1000:  # Keep maximum 1000 conversations
            # Delete oldest conversations
            conversations_to_delete = Conversation.objects.order_by('created_at')[:total_count-1000]
            deleted_count = conversations_to_delete.delete()[0]
            logging.info(f"Cleaned up {deleted_count} old conversations")
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")
        # Don't raise the error - cleanup is not critical

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def vegetarian_list(request):
    """
    Get list of vegetarian/vegan users and their food preferences.
    
    This endpoint provides a list of conversations filtered by dietary preference.
    
    Authentication is no longer required.
    
    Parameters:
        type (string, optional): Filter type - 'all', 'vegetarian', or 'vegan'. Default is 'all'.
    
    Returns:
        count: Number of conversations in the result
        conversations: List of conversations with dietary preferences and foods
    """
    try:
        filter_type = request.query_params.get('type', 'all')
        
        if filter_type == 'vegetarian':
            vegetarian_convos = Conversation.objects.filter(is_vegetarian=True)
        elif filter_type == 'vegan':
            vegetarian_convos = Conversation.objects.filter(is_vegan=True)
        else:
            vegetarian_convos = Conversation.objects.filter(is_vegetarian=True) | Conversation.objects.filter(is_vegan=True)
        
        results = []
        for convo in vegetarian_convos:
            foods = convo.food_preferences.all().order_by('created_at')
            results.append({
                "conversation_id": convo.id,
                "is_vegetarian": convo.is_vegetarian,
                "is_vegan": convo.is_vegan,
                "favorite_foods": [food.food_name for food in foods],
                "created_at": convo.created_at.isoformat()
            })
        
        return Response({
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """
    Get analytics about food preferences and dietary choices.
    
    This endpoint provides aggregated analytics data about user preferences
    over a specified time period.
    
    Authentication is required using either:
    - Token Authentication: Include 'Authorization: Token <your-token>' in the headers
    - Session Authentication: For browser-based sessions
    
    Parameters:
        days (int, optional): Number of days to analyze. Default is 7 days.
    
    Returns:
        total_conversations: Total number of conversations analyzed
        vegetarian_percentage: Percentage of vegetarian preferences
        vegan_percentage: Percentage of vegan preferences
        top_foods: List of most popular foods with counts
        food_categories: Distribution of food preferences by category
    """
    # Get time range from query params or default to last 7 days
    days = int(request.GET.get('days', 7))
    start_date = datetime.now() - timedelta(days=days)
    
    # Get conversations in time range
    conversations = Conversation.objects.filter(created_at__gte=start_date)
    
    # Get food preferences
    food_prefs = FoodPreference.objects.filter(conversation__in=conversations)
    
    # Calculate most popular foods
    food_counts = Counter(food_prefs.values_list('food_name', flat=True))
    popular_foods = [{"name": name, "count": count} 
                    for name, count in food_counts.most_common(10)]
    
    # Calculate dietary preferences
    total = conversations.count()
    vegetarian_count = conversations.filter(is_vegetarian=True).count()
    vegan_count = conversations.filter(is_vegan=True).count()
    
    # Get health scores
    foods = Food.objects.all()
    avg_health_score = foods.aggregate(Avg('health_score'))['health_score__avg'] or 0
    
    return Response({
        'total_conversations': total,
        'vegetarian_percentage': (vegetarian_count / total * 100) if total > 0 else 0,
        'vegan_percentage': (vegan_count / total * 100) if total > 0 else 0,
        'popular_foods': popular_foods,
        'average_health_score': round(avg_health_score, 2),
        'time_range': f'Last {days} days'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def food_categories(request):
    """Get food categories and their statistics"""
    categories = FoodCategory.objects.all()
    result = []
    
    for category in categories:
        foods = category.foods.all()
        result.append({
            'category': category.name,
            'description': category.description,
            'total_foods': foods.count(),
            'avg_health_score': foods.aggregate(Avg('health_score'))['health_score__avg'] or 0,
            'vegetarian_options': foods.filter(is_vegetarian=True).count(),
            'vegan_options': foods.filter(is_vegan=True).count()
        })
    
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_analysis(request):
    """Get health analysis of food choices"""
    foods = Food.objects.all()
    
    # Calculate average nutritional values
    avg_values = foods.aggregate(
        avg_health=Avg('health_score'),
        avg_calories=Avg('calories'),
        avg_protein=Avg('protein'),
        avg_carbs=Avg('carbs'),
        avg_fats=Avg('fats')
    )
    
    # Get top healthy foods
    healthy_foods = foods.order_by('-health_score')[:5].values('name', 'health_score')
    
    return Response({
        'average_values': avg_values,
        'top_healthy_foods': list(healthy_foods),
        'recommendations': [
            'Consider adding more plant-based options',
            'Balance your protein and carb intake',
            'Include a variety of food categories'
        ]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_data(request):
    """Export conversation data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="food_preferences.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Food Name', 'Is Vegetarian', 'Is Vegan', 'Category'])
    
    for pref in FoodPreference.objects.all():
        writer.writerow([
            pref.created_at.strftime('%Y-%m-%d'),
            pref.food_name,
            pref.conversation.is_vegetarian,
            pref.conversation.is_vegan,
            'N/A'  # You can add category if available
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def food_recommendations(request):
    """Get personalized food recommendations based on preferences"""
    try:
        # Get user's conversation history
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response({
                "error": "Please provide a conversation_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.get(id=conversation_id)
        user_foods = FoodPreference.objects.filter(conversation=conversation)
        
        # Get food categories from user's preferences
        preferred_categories = set()
        for food_pref in user_foods:
            matching_foods = Food.objects.filter(name__icontains=food_pref.food_name)
            for food in matching_foods:
                if food.category:
                    preferred_categories.add(food.category.id)
        
        # Find similar foods based on categories and dietary preferences
        recommended_foods = Food.objects.filter(
            category__id__in=preferred_categories,
            is_vegetarian=conversation.is_vegetarian,
            is_vegan=conversation.is_vegan
        ).exclude(
            name__in=[f.food_name for f in user_foods]
        ).order_by('-health_score')[:5]
        
        # Get healthy alternatives
        healthy_alternatives = Food.objects.filter(
            health_score__gte=7.0,
            is_vegetarian=conversation.is_vegetarian,
            is_vegan=conversation.is_vegan
        ).exclude(
            name__in=[f.food_name for f in user_foods]
        ).order_by('-health_score')[:3]
        
        return Response({
            'user_preferences': {
                'is_vegetarian': conversation.is_vegetarian,
                'is_vegan': conversation.is_vegan,
                'favorite_foods': [f.food_name for f in user_foods]
            },
            'recommendations': {
                'similar_foods': [{
                    'name': food.name,
                    'category': food.category.name if food.category else None,
                    'health_score': food.health_score,
                    'calories': food.calories
                } for food in recommended_foods],
                'healthy_alternatives': [{
                    'name': food.name,
                    'category': food.category.name if food.category else None,
                    'health_score': food.health_score,
                    'calories': food.calories
                } for food in healthy_alternatives]
            }
        })
        
    except Conversation.DoesNotExist:
        return Response({
            "error": "Conversation not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_test(request):
    """Simple test endpoint to verify authentication works"""
    return Response({
        "message": "Authentication successful!",
        "user": request.user.username,
        "auth": str(request.auth)
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def token_debug(request):
    """Debug token authentication issues"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    # Log all request headers for debugging
    headers = {key: value for key, value in request.META.items() if key.startswith('HTTP_')}
    
    if auth_header:
        try:
            # Split the auth header
            auth_parts = auth_header.split(' ')
            
            if len(auth_parts) == 2 and auth_parts[0].lower() == 'token':
                token_key = auth_parts[1]
                
                # Try to find the token in the database
                try:
                    token = Token.objects.get(key=token_key)
                    user = token.user
                    return Response({
                        "message": "Token found",
                        "token": token_key,
                        "user_id": user.id,
                        "username": user.username,
                        "headers": headers
                    })
                except Token.DoesNotExist:
                    return Response({
                        "error": "Token does not exist in database",
                        "token_provided": token_key,
                        "headers": headers
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({
                    "error": "Invalid Authorization header format",
                    "auth_header": auth_header,
                    "headers": headers
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "error": f"Error processing authentication: {str(e)}",
                "auth_header": auth_header,
                "headers": headers
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({
            "error": "No Authorization header found",
            "headers": headers
        }, status=status.HTTP_401_UNAUTHORIZED)

# Websocket for real-time chat will be implemented separately
# Websocket for real-time chat will be implemented separately