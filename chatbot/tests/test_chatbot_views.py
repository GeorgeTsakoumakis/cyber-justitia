"""
Test cases for chatbot-related views.

Author: Ionut-Valeriu Facaeru
"""

import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from chatbot.models import Session, Message
import json

CustomUser = get_user_model()


class ChatbotViewsTestCase(TestCase):
    """
    Test case for chatbot-related views.
    """

    def setUp(self):
        """
        TCV1: Set up a test client, user, and session for use in the tests.
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.session = Session.objects.create(user=self.user)

    def test_access_chatbot_home(self):
        """
        TCV2: Test accessing the chatbot home page.
        """
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot_home.html')

    def test_access_chatbot_home_as_authenticated_user(self):
        """
        TCV3: Test accessing the chatbot home page as an authenticated user.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chatbot_session', kwargs={'session_id': self.session.session_id}))

    def test_access_chatbot_session(self):
        """
        TCV4: Test accessing a chatbot session.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': self.session.session_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot_session.html')

    def test_access_non_existent_chatbot_session(self):
        """
        TCV5: Test accessing a non-existent chatbot session.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_access_another_users_chatbot_session(self):
        """
        TCV6: Test accessing another user's chatbot session.
        """
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='Password123!',
            email='otheruser@example.com'
        )
        other_session = Session.objects.create(user=other_user)
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': other_session.session_id}))
        self.assertEqual(response.status_code, 404)

    def test_process_chat_message(self):
        """
        TCV7: Test processing a chat message.
        """
        self.client.login(username='testuser', password='Password123!')
        data = {
            'session_id': self.session.session_id,
            'message': 'Hello, chatbot!'
        }
        response = self.client.post(reverse('process_chat_message'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Check if the role of the second last message is 'user'
        message = Message.objects.filter(session=self.session).order_by('-created_at')[1]
        self.assertEqual(message.role, 'user')
        # Check if the chatbot responded
        self.assertIn('response', response.json())
        message = Message.objects.filter(session=self.session).latest('created_at')
        self.assertEqual(message.role, 'bot')
        # Check if the chatbot responded with the correct message (contains 'Hello' or 'Greetings' or 'Hi')
        self.assertTrue(any(word in message.text for word in ['Hello', 'Greetings', 'Hi']))

    def test_process_chat_message_when_not_authenticated(self):
        """
        TCV8: Test processing a chat message when not authenticated.
        """
        data = {
            'session_id': self.session.session_id,
            'message': 'Hello, chatbot!'
        }
        response = self.client.post(reverse('process_chat_message'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())

    def test_process_chat_message_with_invalid_method(self):
        """
        TCV9: Test processing a chat message with an invalid request method.
        """
        response = self.client.get(reverse('process_chat_message'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('error'), 'Invalid request method')

    def test_create_new_session(self):
        """
        TCV10: Test creating a new session.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_session'))
        self.assertEqual(response.status_code, 302)
        new_session = Session.objects.latest('created_at')
        self.assertRedirects(response, reverse('chatbot_session', kwargs={'session_id': new_session.session_id}))



if __name__ == '__main__':
    unittest.main()
