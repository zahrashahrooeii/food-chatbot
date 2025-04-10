import random
import logging
import json
import time

class MockChatbotService:
    """A mock implementation that doesn't use OpenAI at all"""
    
    def ask_food_preferences(self):
        """Return mock food preferences"""
        time.sleep(0.5)  # Simulate delay
        
        foods = ["pizza", "sushi", "chocolate cake"]
        is_vegetarian = random.choice([True, False])
        is_vegan = is_vegetarian and random.choice([True, False])
        
        response = {
            "foods": foods,
            "is_vegetarian": is_vegetarian,
            "is_vegan": is_vegan
        }
        
        return {
            "question": "What are your top 3 favourite foods?",
            "answer": json.dumps(response)
        }
    
    def simulate_multiple_conversations(self, count=100):
        """Simulate conversations without using OpenAI"""
        results = []
        food_combinations = [
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
        
        for i in range(count):
            # Simulate delay
            time.sleep(0.01)
            
            # Generate mock data
            mock_data = random.choice(food_combinations)
            
            results.append({
                "conversation_id": i + 1,
                "question": "What are your top 3 favorite foods?",
                "answer": json.dumps(mock_data),
                "foods": mock_data["foods"],
                "is_vegetarian": mock_data["is_vegetarian"],
                "is_vegan": mock_data["is_vegan"]
            })
            
        return results 