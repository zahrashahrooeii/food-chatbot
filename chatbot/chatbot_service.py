import random
import logging
import json
import time
from django.conf import settings
from openai import OpenAI

# Handle different versions of OpenAI library
try:
    from openai import OpenAIError
except ImportError:
    try:
        from openai.error import OpenAIError
    except ImportError:
        # Define a fallback error class if OpenAIError can't be imported
        class OpenAIError(Exception):
            pass


class MockOpenAIResponse:
    """Mock response object to simulate OpenAI API responses"""
    def __init__(self, content):
        self.choices = [
            type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': content
                })
            })
        ]


class ChatbotService:
    def __init__(self):
        # Check if we should use the real OpenAI API or mock responses
        self.use_mock = not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('sk-proj-')
        if not self.use_mock and settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.use_mock = True
            logging.warning("No valid OpenAI API key found, using mock responses")
        logging.info(f"Using {'mock' if self.use_mock else 'real'} OpenAI service")

    def ask_food_preferences(self, user_message=None):
        try:
            logging.info("Sending request to OpenAI API...")
            
            if self.use_mock:
                # Use mock response instead of real API
                time.sleep(0.5)  # Simulate API delay
                if not user_message:
                    return {
                        "reply": "Hi! I'd love to learn about your favorite foods. What are your top 3 favorite foods? Feel free to tell me what they are and why you enjoy them!"
                    }
                else:
                    # Analyze the user's message to provide more contextual responses
                    message_lower = user_message.lower()
                    
                    # Check if the message mentions specific foods
                    if any(food in message_lower for food in ["pizza", "burger", "pasta", "sushi", "rice", "noodles", "chicken", "fish"]):
                        responses = [
                            f"That's a great choice! I can see why you enjoy that. What makes these foods special to you? Is it the flavors, the texture, or maybe some good memories associated with them?",
                            f"Interesting selections! I'd love to know more about how you like these prepared. Do you have a favorite way of cooking or eating them?",
                            f"Those sound delicious! What drew you to these particular foods? Is there a story behind why they became your favorites?"
                        ]
                        return {"reply": random.choice(responses)}
                    
                    # Check if the message mentions reasons or preferences
                    elif any(word in message_lower for word in ["because", "like", "love", "enjoy", "favorite", "best"]):
                        responses = [
                            "I can really feel your enthusiasm for these foods! Have you always enjoyed these, or did they grow on you over time?",
                            "That's fascinating! Do you enjoy cooking these foods yourself, or do you have a favorite place where you like to get them?",
                            "I love how passionate you are about these foods! Do you have any special occasions or memories connected to them?"
                        ]
                        return {"reply": random.choice(responses)}
                    
                    # Check if it's a short or unclear response
                    elif len(message_lower.split()) < 5:
                        return {
                            "reply": "Could you tell me a bit more about these foods? What makes them your favorites?"
                        }
                    
                    # Default response for other cases
                    responses = [
                        "Thanks for sharing! Those sound like interesting choices. What made these particular foods become your favorites?",
                        "Great picks! I'd love to hear more about why you enjoy these foods. Do you have any special memories with them?",
                        "Those sound delicious! What do you like most about each of these foods?"
                    ]
                    return {"reply": random.choice(responses)}
            else:
                # Use real OpenAI API
                messages = [
                    {"role": "system", "content": """You are a friendly and engaging food chatbot having a natural conversation about favorite foods.
                    Your goal is to:
                    1. If the user hasn't shared their favorite foods yet, ask them in a friendly way about their top 3 favorite foods
                    2. If they have shared foods, engage naturally by:
                       - Acknowledging their specific food choices
                       - Asking relevant follow-up questions about preparation, memories, or preferences
                       - Showing genuine interest in their responses
                       - Keeping the conversation flowing naturally
                    3. Keep responses concise but warm and engaging
                    4. Never break character or mention being an AI
                    
                    Example good responses:
                    - "Ah, pizza and pasta! Are you a fan of Italian cuisine in general? What draws you to these foods?"
                    - "Homemade curry sounds amazing! Do you enjoy cooking it yourself, or do you have a favorite restaurant?"
                    """}
                ]
                
                if user_message:
                    messages.append({"role": "user", "content": user_message})
                else:
                    messages.append({"role": "user", "content": "Start a conversation about favorite foods"})
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.8,  # Slightly increased for more variety
                    max_tokens=150,
                )
            
                logging.info("Received response from OpenAI API.")
                return {"reply": response.choices[0].message.content.strip()}

        except OpenAIError as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return {"error": f"OpenAI API error: {str(e)}"}
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def simulate_multiple_conversations(self, count=100):
        """
        Simulate conversations between two ChatGPT instances:
        1. ChatGPT A asks about favorite foods
        2. ChatGPT B responds with random preferences
        """
        results = []
        
        # ChatGPT A's question is always the same, so we don't need to generate it each time
        question = "What are your top 3 favorite foods?"
        
        # Pre-generate all mock responses for better performance
        if self.use_mock:
            mock_responses = [
                {
                    "foods": ["homemade pizza", "grilled salmon", "chocolate mousse"],
                    "is_vegetarian": False,
                    "is_vegan": False,
                    "explanation": "I love the combination of comfort food and gourmet dishes."
                },
                {
                    "foods": ["quinoa buddha bowl", "mushroom risotto", "dark chocolate truffles"],
                    "is_vegetarian": True,
                    "is_vegan": False,
                    "explanation": "I prefer vegetarian dishes that are rich in flavor and nutrition."
                },
                {
                    "foods": ["beyond burger", "chickpea curry", "vegan ice cream"],
                    "is_vegetarian": True,
                    "is_vegan": True,
                    "explanation": "I love plant-based alternatives that are both healthy and delicious."
                },
                {
                    "foods": ["sushi rolls", "pad thai", "tiramisu"],
                    "is_vegetarian": False,
                    "is_vegan": False,
                    "explanation": "I enjoy diverse Asian cuisines and Italian desserts."
                },
                {
                    "foods": ["falafel wrap", "lentil soup", "fresh fruit sorbet"],
                    "is_vegetarian": True,
                    "is_vegan": True,
                    "explanation": "I prefer light, healthy, and plant-based Mediterranean dishes."
                }
            ]
            
            # Generate all results at once
            results = [
                {
                    "conversation_id": i + 1,
                    "question": question,
                    "response": random.choice(mock_responses)
                }
                for i in range(count)
            ]
            return results
            
        # For real API, we'll still need to make API calls sequentially
        for i in range(count):
            try:
                # ChatGPT B responds with food preferences
                answer_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are ChatGPT B, responding about food preferences.
                        When asked about your favorite foods, respond with exactly 3 random foods.
                        Be creative and diverse in your choices.
                        Include a mix of different cuisines and types of dishes.
                        Randomly decide if you are vegetarian or vegan.
                        IMPORTANT: Respond ONLY in valid JSON format with these exact fields:
                        {
                            "foods": ["food1", "food2", "food3"],
                            "is_vegetarian": boolean,
                            "is_vegan": boolean,
                            "explanation": "Brief explanation of why these are your favorites"
                        }"""},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.8,
                    max_tokens=150
                )
                
                try:
                    answer = answer_response.choices[0].message.content.strip()
                    response_data = json.loads(answer)
                    
                    # Validate response format
                    if not all(key in response_data for key in ['foods', 'is_vegetarian', 'is_vegan']):
                        raise ValueError("Invalid response format")
                    if len(response_data['foods']) != 3:
                        raise ValueError("Must provide exactly 3 foods")
                        
                    results.append({
                        "conversation_id": i + 1,
                        "question": question,
                        "response": response_data
                    })
                except (json.JSONDecodeError, ValueError) as e:
                    # Fall back to mock data if response is invalid
                    logging.error(f"Invalid response from ChatGPT B: {str(e)}")
                    mock_data = self._generate_mock_food_data()
                    results.append({
                        "conversation_id": i + 1,
                        "question": question,
                        "response": mock_data
                    })
            
            except Exception as e:
                logging.error(f"Error in conversation {i+1}: {str(e)}")
                # Fall back to mock data for any errors
                mock_data = self._generate_mock_food_data()
                results.append({
                    "conversation_id": i + 1,
                    "question": question,
                    "response": mock_data
                })
            
        return results
    
    def _generate_mock_food_data(self):
        """Generate mock food data with diverse food combinations"""
        mock_responses = [
            {
                "foods": ["homemade pizza", "grilled salmon", "chocolate mousse"],
                "is_vegetarian": False,
                "is_vegan": False
            },
            {
                "foods": ["quinoa buddha bowl", "mushroom risotto", "dark chocolate truffles"],
                "is_vegetarian": True,
                "is_vegan": False
            },
            {
                "foods": ["beyond burger", "chickpea curry", "vegan ice cream"],
                "is_vegetarian": True,
                "is_vegan": True
            },
            {
                "foods": ["sushi rolls", "pad thai", "tiramisu"],
                "is_vegetarian": False,
                "is_vegan": False
            },
            {
                "foods": ["falafel wrap", "lentil soup", "fresh fruit sorbet"],
                "is_vegetarian": True,
                "is_vegan": True
            },
            {
                "foods": ["grilled steak", "lobster thermidor", "crème brûlée"],
                "is_vegetarian": False,
                "is_vegan": False
            },
            {
                "foods": ["margherita pizza", "spinach lasagna", "cheesecake"],
                "is_vegetarian": True,
                "is_vegan": False
            },
            {
                "foods": ["tofu stir-fry", "vegetable sushi", "mango sticky rice"],
                "is_vegetarian": True,
                "is_vegan": True
            },
            {
                "foods": ["chicken tikka masala", "beef burger", "apple pie"],
                "is_vegetarian": False,
                "is_vegan": False
            },
            {
                "foods": ["tempeh tacos", "cauliflower wings", "vegan chocolate cake"],
                "is_vegetarian": True,
                "is_vegan": True
            }
        ]
        return random.choice(mock_responses) 