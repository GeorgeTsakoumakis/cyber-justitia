import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from chatbot.models import Session, Message

# Get the CustomUser model
CustomUser = get_user_model()


class ChatbotModelTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='Password123!')

    def test_create_session_with_valid_user(self):
        session = Session.objects.create(user=self.user)
        self.assertIsNotNone(session.session_id)
        self.assertIsNotNone(session.created_at)

    def test_create_session_without_user(self):
        with self.assertRaises(IntegrityError):
            Session.objects.create(user=None)

    def test_session_string_representation(self):
        session = Session.objects.create(user=self.user)
        self.assertEqual(str(session), f'{self.user.username}_{session.session_id}')

    def test_create_message_with_valid_data(self):
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='Hello, world!', role=Message.Role.USER)
        self.assertIsNotNone(message.message_id)
        self.assertIsNotNone(message.created_at)
        self.assertEqual(message.text, 'Hello, world!')
        self.assertEqual(message.role, Message.Role.USER)

    def test_create_message_without_session(self):
        with self.assertRaises(IntegrityError):
            Message.objects.create(session=None, text='Hello, world!', role=Message.Role.USER)

    def test_create_message_with_empty_text(self):
        session = Session.objects.create(user=self.user)
        with self.assertRaises(ValidationError):
            message = Message(session=session, text='', role=Message.Role.USER)
            message.full_clean()

    # This one fails
    def test_create_message_with_text_exceeding_max_length(self):
        session = Session.objects.create(user=self.user)
        with self.assertRaises(ValidationError):
            message = Message(session=session, text='A' * 1026, role=Message.Role.USER)
            message.full_clean()

    def test_create_message_with_invalid_role(self):
        session = Session.objects.create(user=self.user)
        with self.assertRaises(ValidationError):
            message = Message(session=session, text='You lost the game', role='invalid_role')
            message.full_clean()

    def test_create_message_with_different_roles(self):
        session = Session.objects.create(user=self.user)
        user_message = Message.objects.create(session=session, text='User message', role=Message.Role.USER)
        bot_message = Message.objects.create(session=session, text='Bot message', role=Message.Role.BOT)
        system_message = Message.objects.create(session=session, text='System message', role=Message.Role.SYSTEM)
        self.assertEqual(user_message.role, Message.Role.USER)
        self.assertEqual(bot_message.role, Message.Role.BOT)
        self.assertEqual(system_message.role, Message.Role.SYSTEM)

    def test_retrieve_messages_order_by_created_at(self):
        session = Session.objects.create(user=self.user)
        Message.objects.create(session=session, text='First message', role=Message.Role.USER)
        Message.objects.create(session=session, text='Second message', role=Message.Role.BOT)
        messages = Message.objects.filter(session=session).order_by('created_at')
        self.assertEqual(messages[0].text, 'First message')
        self.assertEqual(messages[1].text, 'Second message')

    def test_delete_session_cascades_delete_messages(self):
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='Message to be deleted', role=Message.Role.USER)
        self.assertEqual(Message.objects.filter(session=session).count(), 1)
        session_id = session.session_id  # Store the session ID before deleting
        session.delete()
        self.assertEqual(Message.objects.filter(session_id=session_id).count(), 0)

    def test_session_model_constraints(self):
        session = Session.objects.create(user=self.user)
        self.assertEqual(session._meta.db_table, 'sessions')
        self.assertEqual(session._meta.verbose_name, 'Session')
        self.assertEqual(session._meta.verbose_name_plural, 'Sessions')

    def test_message_model_constraints(self):
        # Verify message constraints like verbose name and roles
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='Test message', role=Message.Role.USER)
        self.assertEqual(message._meta.db_table, 'messages')
        self.assertEqual(message._meta.verbose_name, 'Message')
        self.assertEqual(message._meta.verbose_name_plural, 'Messages')

        role_values = [choice[0] for choice in Message.Role.choices]
        self.assertIn('user', role_values)
        self.assertIn('bot', role_values)
        self.assertIn('system', role_values)

    def test_create_multiple_sessions_for_same_user(self):
        session1 = Session.objects.create(user=self.user)
        session2 = Session.objects.create(user=self.user)
        self.assertNotEqual(session1.session_id, session2.session_id)

    def test_create_multiple_messages_in_single_session(self):
        session = Session.objects.create(user=self.user)
        message1 = Message.objects.create(session=session, text='First message', role=Message.Role.USER)
        message2 = Message.objects.create(session=session, text='Second message', role=Message.Role.BOT)
        self.assertEqual(message1.session, session)
        self.assertEqual(message2.session, session)

    def test_create_message_with_emojis(self):
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='Hello 😊', role=Message.Role.USER)
        self.assertEqual(message.text, 'Hello 😊')

    def test_update_message_text(self):
        # Just checking if db works correctly nobody will use this
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='Old message', role=Message.Role.USER)
        message.text = 'Updated message'
        message.save()
        self.assertEqual(message.text, 'Updated message')

    def test_create_message_at_text_length_boundary(self):
        session = Session.objects.create(user=self.user)
        message = Message.objects.create(session=session, text='A' * 1024, role=Message.Role.USER)
        self.assertEqual(len(message.text), 1024)

    def test_create_and_retrieve_session_by_created_at(self):
        session = Session.objects.create(user=self.user)
        retrieved_session = Session.objects.get(created_at=session.created_at)
        self.assertEqual(session, retrieved_session)

    def test_session_string_representation_with_long_username(self):
        long_username_user = CustomUser.objects.create_user(username='a'*150, email='longusername@example.com', password='Password123!')
        session = Session.objects.create(user=long_username_user)
        expected_str = f'{long_username_user.username}_{session.session_id}'
        self.assertEqual(str(session), expected_str)


if __name__ == '__main__':
    unittest.main()