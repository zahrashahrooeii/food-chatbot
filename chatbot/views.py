import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from food_api.models import Conversation, FoodPreference
from django.db.models import Count
import logging
from .chatbot_service import ChatbotService


def cleanup_old_conversations(max_records=1000):
    """Clean up old conversation records to prevent database bloat"""
    try:
        # Count total conversations
        total_count = Conversation.objects.count()
        
        if total_count > max_records:
            # Calculate how many records to delete
            to_delete = total_count - max_records
            
            # Get the IDs of the oldest records to delete
            old_conversations = Conversation.objects.order_by('id')[:to_delete]
            old_ids = list(old_conversations.values_list('id', flat=True))
            
            # Delete associated food preferences first
            FoodPreference.objects.filter(conversation_id__in=old_ids).delete()
            
            # Delete the conversations
            Conversation.objects.filter(id__in=old_ids).delete()
            
            logging.info(f"Cleaned up {to_delete} old conversation records")
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def start_conversation(request):
    """
    Start or continue a conversation with the chatbot about favorite foods.
    
    This endpoint handles both starting new conversations and continuing existing ones.
    The chatbot will ask about favorite foods and engage in natural conversation about them.
    
    Parameters:
        message (string, optional): The user's message in the conversation
        
    Returns:
        reply: The chatbot's response message
    """
    try:
        message = request.data.get('message') if request.data else None
        chatbot = ChatbotService()
        result = chatbot.ask_food_preferences(message)
        
        if 'error' in result:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(result)
        
    except Exception as e:
        logging.error(f"Error in start_conversation: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def simulate_conversations(request):
    """
    Simulate multiple conversations about food preferences.
    
    This endpoint simulates a specified number of conversations between 
    the chatbot and users, generating varied food preferences data.
    
    Parameters:
        count (int, optional): Number of conversations to simulate (default: 100, max: 1000)
    
    Returns:
        message: Success message
        successful: Number of successfully simulated conversations
        failed: Number of failed simulations
        results: Sample of the first 5 conversations with food preferences
    """
    logging.info("Simulating conversations...")
    try:
        count = int(request.data.get("count", 100))
        count = min(count, 1000)  # Limit to maximum 1000
        
        # Clean up old records before simulation
        cleanup_old_conversations()
        
        chatbot = ChatbotService()
        simulation_results = chatbot.simulate_multiple_conversations(count)
        
        # Save results to database
        saved_conversations = []
        failed_count = 0
        
        for result in simulation_results:
            try:
                # Extract the response data from the simulation result
                response_data = result['response']
                
                # Create conversation record
                conversation = Conversation.objects.create(
                    is_vegetarian=response_data['is_vegetarian'],
                    is_vegan=response_data['is_vegan']
                )
                
                # Create food preference records
                for food in response_data['foods']:
                    FoodPreference.objects.create(
                        conversation=conversation,
                        food_name=food
                    )
                
                saved_conversations.append({
                    "conversation_id": conversation.id,
                    "foods": response_data['foods'],
                    "is_vegetarian": response_data['is_vegetarian'],
                    "is_vegan": response_data['is_vegan'],
                    "explanation": response_data.get('explanation', '')
                })
            except Exception as e:
                logging.error(f"Error saving conversation: {str(e)}")
                failed_count += 1
        
        # Get some statistics about the data
        total_conversations = Conversation.objects.count()
        vegetarian_count = Conversation.objects.filter(is_vegetarian=True).count()
        vegan_count = Conversation.objects.filter(is_vegan=True).count()
        
        return Response({
            "message": f"Completed {len(saved_conversations)} conversations",
            "successful": len(saved_conversations),
            "failed": failed_count,
            "results": saved_conversations[:5],  # Return first 5 results as sample
            "statistics": {
                "total_conversations": total_conversations,
                "vegetarian_percentage": round((vegetarian_count / total_conversations) * 100, 1) if total_conversations > 0 else 0,
                "vegan_percentage": round((vegan_count / total_conversations) * 100, 1) if total_conversations > 0 else 0
            }
        })
    except Exception as e:
        logging.error(f"Error in simulate_conversations: {str(e)}")
        return Response({
            "message": str(e),
            "successful": 0,
            "failed": count,
            "results": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
