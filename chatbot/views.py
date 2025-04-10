import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from .mock_service import MockChatbotService
from food_api.models import Conversation, FoodPreference


@api_view(['POST'])
@permission_classes([AllowAny])  # Open to everyone
def start_conversation(request):
    """
    Start a new conversation with the chatbot asking for food preferences.
    
    This endpoint initiates a new conversation where the chatbot asks about 
    favorite foods and dietary preferences. No authentication required.
    
    Returns:
        conversation_id: The ID of the newly created conversation
        question: The question asked by the chatbot
        response: A JSON object containing:
            - foods: List of 3 favorite foods
            - is_vegetarian: Boolean indicator if the foods are vegetarian
            - is_vegan: Boolean indicator if the foods are vegan
    """
    chatbot = MockChatbotService()
    result = chatbot.ask_food_preferences()
    
    try:
        # Parse the JSON answer
        answer_data = json.loads(result["answer"])
        
        # Create conversation record
        conversation = Conversation.objects.create(
            is_vegetarian=answer_data.get('is_vegetarian', False),
            is_vegan=answer_data.get('is_vegan', False)
        )
        
        # Create food preference records
        for food in answer_data.get('foods', []):
            FoodPreference.objects.create(
                conversation=conversation,
                food_name=food
            )
            
        return Response({
            "conversation_id": conversation.id,
            "question": result["question"],
            "response": answer_data
        })
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])  # Requires authentication
def simulate_conversations(request):
    """
    Simulate multiple conversations between chatbot instances.
    
    This endpoint simulates a specified number of conversations between 
    the chatbot and users, generating varied food preferences data.
    
    Authentication is required for this endpoint using either:
    - Token Authentication: Include 'Authorization: Token <your-token>' in the headers
    - Session Authentication: For browser-based sessions
    
    Parameters:
        count (int, optional): Number of conversations to simulate (default: 100, max: 1000)
    
    Returns:
        message: Success message
        successful: Number of successfully simulated conversations
        failed: Number of failed simulations
        results: Sample of the first 5 conversations with food preferences
    """
    try:
        count = int(request.data.get("count", 100))
        count = min(count, 1000)  # Limit to maximum 1000
        
        chatbot = MockChatbotService()
        simulation_results = chatbot.simulate_multiple_conversations(count)
        
        # Save results to database
        saved_conversations = []
        for result in simulation_results:
            try:
                # Create conversation record
                conversation = Conversation.objects.create(
                    is_vegetarian=result.get('is_vegetarian', False),
                    is_vegan=result.get('is_vegan', False)
                )
                
                # Create food preference records
                for food in result.get('foods', []):
                    FoodPreference.objects.create(
                        conversation=conversation,
                        food_name=food
                    )
                
                saved_conversations.append({
                    "conversation_id": conversation.id,
                    "foods": result.get('foods'),
                    "is_vegetarian": conversation.is_vegetarian,
                    "is_vegan": conversation.is_vegan
                })
            except Exception as e:
                print(f"Error saving conversation: {str(e)}")
        
        return Response({
            "message": f"Completed {len(simulation_results)} conversations",
            "successful": len(simulation_results),
            "failed": 0,
            "results": saved_conversations[:5]  # Return first 5 results as sample
        })
    except Exception as e:
        return Response({
            "message": str(e),
            "successful": 0,
            "failed": count,
            "results": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
