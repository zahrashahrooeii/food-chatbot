from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch, MagicMock
import json

from food_api.models import Conversation, FoodPreference
from .mock_service import MockChatbotService


class MockServiceTest(TestCase):
    """Tests for the MockChatbotService class"""

    def test_ask_food_preferences(self):
        """Test that ask_food_preferences returns expected format"""
        service = MockChatbotService()
        result = service.ask_food_preferences()
        
        # Check the format of the response
        self.assertIn('question', result)
        self.assertIn('answer', result)
        
        # Check the answer can be parsed as JSON
        answer_data = json.loads(result['answer'])
        self.assertIn('foods', answer_data)
        self.assertIn('is_vegetarian', answer_data)
        self.assertIn('is_vegan', answer_data)
        
        # Check that foods is a list of 3 items
        self.assertEqual(len(answer_data['foods']), 3)
        
        # Check that vegetarian/vegan flags are booleans
        self.assertIsInstance(answer_data['is_vegetarian'], bool)
        self.assertIsInstance(answer_data['is_vegan'], bool)
    
    def test_simulate_multiple_conversations(self):
        """Test that we can simulate multiple conversations"""
        service = MockChatbotService()
        
        # Test with different counts
        for count in [1, 5, 10]:
            results = service.simulate_multiple_conversations(count)
            
            # Check we got the expected number of results
            self.assertEqual(len(results), count)
            
            # Check the format of each result
            for result in results:
                self.assertIn('conversation_id', result)
                self.assertIn('question', result)
                self.assertIn('answer', result)
                self.assertIn('foods', result)
                self.assertIn('is_vegetarian', result)
                self.assertIn('is_vegan', result)
                
                # Check that vegetarian/vegan flags are consistent
                # If vegan is True, vegetarian must also be True
                if result['is_vegan']:
                    self.assertTrue(result['is_vegetarian'])


class ChatbotViewsTest(TestCase):
    """Tests for chatbot views"""
    
    def setUp(self):
        self.client = Client()
        # Create a test user for authenticated endpoints
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        # Create a token for API authentication
        self.token = Token.objects.create(user=self.user)
        self.api_client = APIClient()
    
    @patch('chatbot.views.MockChatbotService.ask_food_preferences')
    def test_start_conversation_endpoint(self, mock_ask):
        """Test the start_conversation endpoint"""
        # Mock the response from the service
        mock_ask.return_value = {
            'question': 'What are your top 3 favourite foods?',
            'answer': json.dumps({
                'foods': ['pizza', 'sushi', 'chocolate cake'],
                'is_vegetarian': False,
                'is_vegan': False
            })
        }
        
        # Make the request
        response = self.client.post('/api/chat/start-conversation/', {})
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('conversation_id', data)
        self.assertIn('question', data)
        self.assertIn('response', data)
        
        # Check that a conversation was created in the database
        self.assertEqual(Conversation.objects.count(), 1)
        conversation = Conversation.objects.first()
        self.assertFalse(conversation.is_vegetarian)
        self.assertFalse(conversation.is_vegan)
        
        # Check that food preferences were created
        self.assertEqual(FoodPreference.objects.count(), 3)
        foods = [pref.food_name for pref in FoodPreference.objects.all()]
        self.assertIn('pizza', foods)
        self.assertIn('sushi', foods)
        self.assertIn('chocolate cake', foods)
    
    @patch('chatbot.views.MockChatbotService.ask_food_preferences')
    def test_start_conversation_handles_errors(self, mock_ask):
        """Test that start_conversation handles errors gracefully"""
        # Mock the service to raise an exception
        mock_ask.side_effect = Exception('Test error')
        
        # Make the request
        response = self.client.post('/api/chat/start-conversation/', {})
        
        # Check the response
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('chatbot.views.MockChatbotService.simulate_multiple_conversations')
    def test_simulate_conversations_endpoint_requires_auth(self, mock_simulate):
        """Test that simulate_conversations requires authentication"""
        # Try without authentication
        response = self.client.post('/api/chat/simulate/', {'count': 5})
        self.assertEqual(response.status_code, 401)  # Unauthorized
        
        # Set the token authentication
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Mock the service response
        mock_simulate.return_value = [
            {
                'conversation_id': 1,
                'question': 'What are your top 3 favorite foods?',
                'answer': json.dumps({
                    'foods': ['pizza', 'sushi', 'chocolate cake'],
                    'is_vegetarian': False,
                    'is_vegan': False
                }),
                'foods': ['pizza', 'sushi', 'chocolate cake'],
                'is_vegetarian': False,
                'is_vegan': False
            }
        ]
        
        # Try with authentication
        response = self.api_client.post('/api/chat/simulate/', {'count': 5})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('successful', data)
        self.assertEqual(data['successful'], 1)
    
    @patch('chatbot.views.MockChatbotService.simulate_multiple_conversations')
    def test_simulate_conversations_with_count(self, mock_simulate):
        """Test simulate_conversations with different count values"""
        # Set the token authentication
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Mock the service response
        mock_simulate.return_value = [{'conversation_id': i} for i in range(1, 11)]
        
        # Test with count=10
        response = self.api_client.post('/api/chat/simulate/', {'count': 10})
        mock_simulate.assert_called_with(10)
        
        # Test with default count (100)
        response = self.api_client.post('/api/chat/simulate/', {})
        mock_simulate.assert_called_with(100)
        
        # Test with count exceeding the limit
        response = self.api_client.post('/api/chat/simulate/', {'count': 2000})
        # Should be capped at 1000
        mock_simulate.assert_called_with(1000)


class AuthenticationTest(TestCase):
    """Tests for authentication functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
    
    def test_login_view(self):
        """Test that a user can log in"""
        # Try with incorrect credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Form is re-displayed
        self.assertFalse(response.context['user'].is_authenticated)
        
        # Try with correct credentials
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_register_view(self):
        """Test that a user can register"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complex-password123',
            'password2': 'complex-password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'newuser')
        
        # Check the user was created in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_logout_view(self):
        """Test that a user can log out"""
        # First log in
        self.client.login(username='testuser', password='testpassword')
        
        # Check we're logged in
        response = self.client.get(reverse('home'))
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Log out
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
    
    def test_chat_view_requires_login(self):
        """Test that the chat view requires login"""
        # Try without being logged in
        response = self.client.get(reverse('chat'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
        
        # Log in
        self.client.login(username='testuser', password='testpassword')
        
        # Try accessing chat view
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 200)


class APIAuthTest(TestCase):
    """Tests for API authentication"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=self.user)
    
    def test_api_token_auth(self):
        """Test token authentication for API endpoints"""
        # Try without token
        response = self.client.post('/api/chat/simulate/', {'count': 5})
        self.assertEqual(response.status_code, 401)  # Unauthorized
        
        # Try with token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/chat/simulate/', {'count': 5})
        self.assertEqual(response.status_code, 200)
    
    def test_session_auth(self):
        """Test session authentication for API endpoints"""
        # Log in
        self.client.login(username='testuser', password='testpassword')
        
        # Try accessing protected endpoint
        response = self.client.post('/api/chat/simulate/', {'count': 5})
        self.assertEqual(response.status_code, 200)
