import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .mock_service import MockChatbotService
from food_api.models import Conversation, FoodPreference


@api_view(['POST'])
@permission_classes([AllowAny])  # Open to everyone
def start_conversation(request):
    """
    Start a new conversation with ChatGPT asking for 3 favourite foods.
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
@permission_classes([IsAuthenticated])  # Requires authentication
def simulate_conversations(request):
    """
    Simulate 100 conversations between two ChatGPT instances.
    Requires token-based authentication.
    """
    try:
        count = int(request.data.get("count", 100))
        count = min(count, 100)  # Limit to maximum 100
        
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
            "status": "success",
            "message": f"Simulated {len(simulation_results)} conversations, saved {len(saved_conversations)} to database",
            "sample_results": saved_conversations[:5]  # Return first 5 results as sample
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
