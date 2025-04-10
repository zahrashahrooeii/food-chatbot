from django.test import TestCase
from unittest.mock import patch

class ChatbotAPITest(TestCase):
    @patch('chatbot.views.openai.chat.completions.create')
    def test_chatbot_view_returns_answer(self, mock_openai):
        mock_openai.return_value.choices = [
            type('obj', (object,), {"message": type('msg', (object,), {"content": "Pizza, Pasta, Salad"})})()
        ]

        response = self.client.get('/api/chatbot/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Pizza", response.json()["answer"])
