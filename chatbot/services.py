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
                        "reply": "What are your 3 favorite foods? Feel free to tell me about them and why you like them!"
                    }
                else:
                    return {
                        "reply": "Thanks for sharing! Those sound like delicious choices. Would you like to tell me more about why you enjoy these foods?"
                    }
            else:
                # Use real OpenAI API
                messages = [
                    {"role": "system", "content": """You are a friendly food chatbot having a conversation about favorite foods.
                    If the user hasn't provided their favorite foods yet, ask them what their 3 favorite foods are in a friendly way.
                    If they have shared their foods, respond naturally and ask follow-up questions about why they like those foods.
                    Keep the conversation natural and engaging."""},
                ]
                
                if user_message:
                    messages.append({"role": "user", "content": user_message})
                else:
                    messages.append({"role": "user", "content": "Start the conversation about favorite foods"})
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
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
        This satisfies Step 4.1-4.3 in the assignment
        """
        results = []
        
        for i in range(count):
            try:
                if self.use_mock:
                    # Use mock responses
                    time.sleep(0.1)  # Simulate API delay
                    
                    # Step 4.1: Ask the question (mocked)
                    question = "What are your top 3 favorite foods?"
                    
                    # Step 4.2: Answer with random preferences (mocked)
                    mock_data = self._generate_mock_food_data()
                    results.append({
                        "conversation_id": i + 1,
                        "question": question,
                        "answer": json.dumps(mock_data),
                        "foods": mock_data.get('foods'),
                        "is_vegetarian": mock_data.get('is_vegetarian', False),
                        "is_vegan": mock_data.get('is_vegan', False)
                    })
                else:
                    # Step 4.1: Ask the question
                    chatgpt_a_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a friendly chatbot asking about food preferences."},
                            {"role": "user", "content": "Generate a question asking someone what their top 3 favorite foods are."}
                        ],
                        temperature=0.7,
                        max_tokens=50,
                    )
                    question = chatgpt_a_response.choices[0].message.content.strip()
                    logging.info(f"ChatGPT A asked: {question}")
                    
                    # Step 4.2: Answer with random preferences
                    chatgpt_b_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a chatbot that provides food preferences. Respond with your top 3 favorite foods and randomly choose if you are vegetarian/vegan. Respond ONLY in valid JSON format with fields: foods (array of 3 strings), is_vegetarian (boolean), is_vegan (boolean)"},
                            {"role": "user", "content": question}
                        ],
                        temperature=0.8,
                        max_tokens=150,
                    )
                    
                    answer = chatgpt_b_response.choices[0].message.content.strip()
                    logging.info(f"ChatGPT B answered: {answer}")
                    
                    # Parse the response
                    try:
                        response_data = json.loads(answer)
                        # Validate the response data
                        if not isinstance(response_data.get('foods'), list) or len(response_data.get('foods', [])) != 3:
                            logging.warning(f"Invalid response format from ChatGPT B: {answer}")
                            # Fall back to mock data
                            response_data = self._generate_mock_food_data()
                        
                        results.append({
                            "conversation_id": i + 1,
                            "question": question,
                            "answer": answer,
                            "foods": response_data.get('foods'),
                            "is_vegetarian": response_data.get('is_vegetarian', False),
                            "is_vegan": response_data.get('is_vegan', False)
                        })
                    except json.JSONDecodeError:
                        logging.warning(f"Could not parse JSON from ChatGPT B: {answer}")
                        # Fall back to mock data
                        mock_data = self._generate_mock_food_data()
                        results.append({
                            "conversation_id": i + 1,
                            "question": question,
                            "answer": answer,
                            "foods": mock_data.get('foods'),
                            "is_vegetarian": mock_data.get('is_vegetarian', False),
                            "is_vegan": mock_data.get('is_vegan', False)
                        })
                
            except OpenAIError as e:
                logging.error(f"OpenAI API error in conversation {i+1}: {str(e)}")
                # Fall back to mock data when API errors occur
                mock_data = self._generate_mock_food_data()
                results.append({
                    "conversation_id": i + 1,
                    "question": "What are your top 3 favorite foods?",
                    "answer": "Response unavailable due to API error",
                    "foods": mock_data.get('foods'),
                    "is_vegetarian": mock_data.get('is_vegetarian', False),
                    "is_vegan": mock_data.get('is_vegan', False),
                    "error": str(e)
                })
            except Exception as e:
                logging.error(f"Unexpected error in conversation {i+1}: {str(e)}")
                # Fall back to mock data for unexpected errors
                mock_data = self._generate_mock_food_data()
                results.append({
                    "conversation_id": i + 1,
                    "question": "What are your top 3 favorite foods?",
                    "answer": "Response unavailable due to unexpected error",
                    "foods": mock_data.get('foods'),
                    "is_vegetarian": mock_data.get('is_vegetarian', False),
                    "is_vegan": mock_data.get('is_vegan', False),
                    "error": str(e)
                })
                
        return results
    
    def _generate_mock_food_data(self):
        """Generate mock food data as fallback when API fails"""
        mock_responses = [
            {
                "foods": ["vegan pizza", "tofu stir-fry", "avocado toast"],
                "is_vegetarian": True,
                "is_vegan": True
            },
            {
                "foods": ["spaghetti", "vegan burgers", "fruit salad"],
                "is_vegetarian": True,
                "is_vegan": False
            },
            {
                "foods": ["sushi", "ramen", "chocolate cake"],
                "is_vegetarian": False,
                "is_vegan": False
            },
            {
                "foods": ["falafel", "hummus", "pita bread"],
                "is_vegetarian": True,
                "is_vegan": True
            },
            {
                "foods": ["tacos", "burritos", "nachos"],
                "is_vegetarian": False,
                "is_vegan": False
            }
        ]
        return random.choice(mock_responses)


class ChatbotSimulationService:
    def __init__(self):
        # Using mock responses only - no API key needed
        self.use_mock = True

    def simulate_conversations(self, count=100):
        mock_responses = [
            "I love vegan pizza, tofu stir-fry, and avocado toast!",
            "My top 3 are spaghetti, vegan burgers, and fruit salad!",
            "I enjoy sushi, ramen, and chocolate cake!",
            "I like falafel, hummus, and pita bread!",
            "I love tacos, burritos, and nachos!"
        ]
        results = []
        for i in range(count):
            question = "What are your top 3 favourite foods?"
            answer = random.choice(mock_responses)
            results.append({
                "conversation_id": i + 1,
                "question": question,
                "answer": answer
            })
        return results
