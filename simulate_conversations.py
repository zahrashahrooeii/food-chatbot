import os
import django
import json
from tqdm import tqdm

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
django.setup()

from openai import OpenAI
from food_api.models import Conversation, FoodPreference
from django.conf import settings

def simulate_conversations(count=100):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    successful = 0
    
    print(f"\nSimulating {count} conversations...")
    progress_bar = tqdm(total=count)
    
    for _ in range(count):
        try:
            # ChatGPT A asks the question
            question = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are ChatGPT A, asking about food preferences."},
                    {"role": "user", "content": "Ask for someone's top 3 favorite foods."}
                ]
            )

            # ChatGPT B answers with food preferences
            answer = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are ChatGPT B. Respond with your top 3 favorite foods. Randomly choose if you are vegetarian/vegan or not. Format your response as JSON with fields: foods (array of 3 strings), is_vegetarian (boolean), is_vegan (boolean)"},
                    {"role": "user", "content": question.choices[0].message.content}
                ]
            )

            # Parse the response and store in database
            response_data = json.loads(answer.choices[0].message.content)
            conversation = Conversation.objects.create(
                is_vegetarian=response_data['is_vegetarian'],
                is_vegan=response_data['is_vegan']
            )

            # Store food preferences
            for rank, food in enumerate(response_data['foods'], 1):
                FoodPreference.objects.create(
                    conversation=conversation,
                    food_name=food,
                    rank=rank
                )
            successful += 1
            
        except Exception as e:
            print(f"\nError in conversation {_}: {str(e)}")
            continue
        finally:
            progress_bar.update(1)
    
    progress_bar.close()
    return successful

if __name__ == '__main__':
    successful = simulate_conversations(100)
    print(f"\nSuccessfully completed {successful} out of 100 conversations")
    
    # Print statistics
    total_convos = Conversation.objects.count()
    vegetarian_count = Conversation.objects.filter(is_vegetarian=True).count()
    vegan_count = Conversation.objects.filter(is_vegan=True).count()
    
    print(f"\nStatistics:")
    print(f"Total conversations: {total_convos}")
    print(f"Vegetarian users: {vegetarian_count}")
    print(f"Vegan users: {vegan_count}") 