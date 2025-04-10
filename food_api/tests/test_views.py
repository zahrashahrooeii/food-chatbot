from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from food_api.models import Conversation, FoodPreference, FoodCategory, Food
from unittest.mock import patch
import json

class FoodAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.category = FoodCategory.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.food = Food.objects.create(
            name='Test Food',
            category=self.category,
            health_score=8.5,
            is_vegetarian=True,
            calories=200
        )
        self.conversation = Conversation.objects.create(
            is_vegetarian=True,
            is_vegan=False
        )
        self.food_pref = FoodPreference.objects.create(
            conversation=self.conversation,
            food_name='Test Food'
        )

    def test_register_user(self):
        """Test user registration"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_login_user(self):
        """Test user login"""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    @patch('food_api.views.client.chat.completions.create')
    def test_start_conversation(self, mock_openai):
        """Test starting a conversation"""
        mock_openai.return_value.choices[0].message.content = json.dumps({
            'foods': ['Pizza', 'Sushi', 'Salad'],
            'is_vegetarian': True,
            'is_vegan': False
        })
        
        url = reverse('chat-start')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('conversation_id' in response.data)

    def test_vegetarian_list(self):
        """Test getting vegetarian list"""
        url = reverse('vegetarian-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

    def test_analytics_dashboard(self):
        """Test analytics dashboard"""
        url = reverse('analytics-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('total_conversations' in response.data)

    def test_food_categories(self):
        """Test food categories endpoint"""
        url = reverse('food-categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['category'], 'Test Category')

    def test_health_analysis(self):
        """Test health analysis endpoint"""
        url = reverse('health-analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('average_values' in response.data)

    def test_food_recommendations(self):
        """Test food recommendations endpoint"""
        url = reverse('food-recommendations')
        response = self.client.get(url, {'conversation_id': self.conversation.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('recommendations' in response.data)

    def test_export_data(self):
        """Test data export endpoint"""
        url = reverse('export-data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_invalid_conversation_id(self):
        """Test invalid conversation ID handling"""
        url = reverse('food-recommendations')
        response = self.client.get(url, {'conversation_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_conversation_id(self):
        """Test missing conversation ID handling"""
        url = reverse('food-recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 