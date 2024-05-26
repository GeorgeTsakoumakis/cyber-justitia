import unittest

from django.contrib.auth.password_validation import validate_password
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from ..models import ProfessionalUser
from chatbot.models import Session, Message
from forum.models import Post, Comment, PostVote, CommentVote

# Get the CustomUser model
CustomUser = get_user_model()


class CustomUserModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_user_creation(self):
        # Check that the user is created correctly
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('Password123!'))

    def test_str_method(self):
        # Check the __str__ method
        self.assertEqual(str(self.user), 'testuser')

    def test_unique_email(self):
        # Check that emails are unique
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='anotheruser',
                first_name='Another',
                last_name='User',
                email='testuser@example.com',
                password='Password123!'
            )

    def test_email_format(self):
        # Check that invalid email format raises a ValidationError
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user8',
                first_name='Firstname',
                last_name='Lastname',
                email='invalid-email-format'
            )
            user.full_clean()

    def test_blank_names(self):
        # Check that first_name and last_name are not blank
        user = CustomUser(
            username='user2',
            first_name='',
            last_name='Lastname',
            email='user2@example.com',
            password='Password123!'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

        user = CustomUser(
            username='user3',
            first_name='Firstname',
            last_name='',
            email='user3@example.com',
            password='Password123!'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_blank_username(self):
        # Check that username is not blank
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                first_name='Firstname',
                last_name='Lastname',
                email='user@example.com',
                password='Password123!'
            )

    def test_duplicate_username(self):
        # Check that usernames are unique
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='testuser',
                first_name='Another',
                last_name='User',
                email='anotheruser@example.com',
                password='Password123!'
            )

    def test_default_is_banned(self):
        # Check that is_banned defaults to False
        self.assertFalse(self.user.is_banned)

    def test_max_length_constraints(self):
        # Check max length constraints
        long_username = 'a' * 151  # lots of a's
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username=long_username,
                first_name='Firstname',
                last_name='Lastname',
                email='user4@example.com'
            )
            user.full_clean()

        long_first_name = 'a' * 151
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user5',
                first_name=long_first_name,
                last_name='Lastname',
                email='user5@example.com'
            )
            user.full_clean()

        long_last_name = 'a' * 151
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user6',
                first_name='Firstname',
                last_name=long_last_name,
                email='user6@example.com'
            )
            user.full_clean()

        long_email = 'a' * 321 + '@example.com'
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user7',
                first_name='Firstname',
                last_name='Lastname',
                email=long_email
            )
            user.full_clean()

        long_description = 'a' * 257
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user8',
                first_name='Firstname',
                last_name='Lastname',
                email='user8@example.com',
                description=long_description
            )
            user.full_clean()

    def test_username_with_special_characters(self):
        with (self.assertRaises(ValidationError)):
            user = CustomUser(
                username='!@#%$%',
                first_name='Firstname',
                last_name='Lastname',
                email='user11@example.com',
                password='Password123!'
            )
            user.full_clean()

    def test_whitespace_username(self):
        with self.assertRaises(ValidationError):
            user = CustomUser(username='   ')
            user.full_clean()

    def test_whitespace_names(self):
        # Check that first_name and last_name are not blank
        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create_user(
                username='user2',
                first_name='     ',
                last_name='Lastname',
                email='user2@example.com',
                password='Password123!'
            )
            user.full_clean()

        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create_user(
                username='user3',
                first_name='Firstname',
                last_name='     ',
                email='user3@example.com',
                password='Password123!'
            )
            user.full_clean()

    def test_whitespace_email(self):
        with self.assertRaises(ValidationError):
            user = CustomUser(username='user8', email='   valid@example.com   ')
            user.full_clean()

    def test_invalid_password(self):
        # Check that an invalid password raises a ValidationError
        invalid_password = 'cringe'

        with self.assertRaises(ValidationError):
            validate_password(invalid_password, user=self.user)


class ProfessionalUserModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_create_professional_user(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        self.assertIsInstance(professional_user, ProfessionalUser)
        self.assertEqual(professional_user.flair, "Experienced Attorney")

    def test_blank_flair(self):
        professional_user = ProfessionalUser(user=self.user, flair="")
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_max_flair_length(self):
        flair = 'a' * 100
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair=flair
        )
        self.assertEqual(professional_user.flair, flair)

    def test_long_flair(self):
        flair = 'a' * 101
        professional_user = ProfessionalUser(user=self.user, flair=flair)
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_update_flair(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        professional_user.flair = "Expert Legal Advisor"
        professional_user.save()
        professional_user.refresh_from_db()
        self.assertEqual(professional_user.flair, "Expert Legal Advisor")

    def test_valid_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned="Violation of terms"
        )
        self.assertIsInstance(professional_user, ProfessionalUser)
        self.assertEqual(professional_user.reason_banned, "Violation of terms")

    def test_blank_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=""
        )
        self.assertEqual(professional_user.reason_banned, "")

    def test_null_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=None
        )
        self.assertIsNone(professional_user.reason_banned)

    def test_max_reason_banned_length(self):
        reason_banned = 'a' * 150
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=reason_banned
        )
        self.assertEqual(professional_user.reason_banned, reason_banned)

    def test_long_reason_banned(self):
        reason_banned = 'a' * 151
        professional_user = ProfessionalUser(user=self.user, flair="Experienced Attorney", reason_banned=reason_banned)
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_create_professional_without_user(self):
        professional_user = ProfessionalUser(user=None, flair="Experienced Attorney")
        with self.assertRaises(IntegrityError):
            professional_user.save()

    def test_delete_associated_user(self):
        # Checks if ProfessionalUser deletes itself when the associated User is deleted
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        self.user.delete()
        with self.assertRaises(ProfessionalUser.DoesNotExist):
            ProfessionalUser.objects.get(pk=professional_user.prof_id)


# Creating a test_models.py in chatbot/tests doesn't work for some reason
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


class PostModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )

    def test_create_post_with_valid_data(self):
        post = Post.objects.create(
            title='Valid Title',
            text='Valid text.',
            user=self.user
        )
        self.assertEqual(post.title, 'Valid Title')
        self.assertEqual(post.text, 'Valid text.')
        self.assertEqual(post.user, self.user)

    def test_create_post_with_empty_title(self):
        post = Post(
            title='',
            text='Valid text.',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_long_title(self):
        long_title = 'a' * 257
        post = Post(
            title=long_title,
            text='Valid text.',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_empty_text(self):
        post = Post(
            title='Valid Title',
            text='',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_long_text(self):
        long_text = 'a' * 40001
        post = Post(
            title='Valid Title',
            text=long_text,
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_post_slug_is_unique(self):
        post1 = Post.objects.create(
            title='Unique Title',
            text='Valid text.',
            user=self.user
        )
        post2 = Post.objects.create(
            title='Unique Title',
            text='Another valid text.',
            user=self.user
        )
        self.assertNotEqual(post1.slug, post2.slug)

    def test_post_delete(self):
        post = Post.objects.create(
            title='Title to Delete',
            text='Text to delete.',
            user=self.user
        )
        post.delete()
        self.assertTrue(post.is_deleted)
        self.assertEqual(post.text, '[deleted]')
        self.assertEqual(post.title, '[deleted]')


class CommentModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.post = Post.objects.create(
            title='Valid Title',
            text='Valid text.',
            user=self.user
        )

    def test_create_comment_with_valid_data(self):
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='Valid comment text.'
        )
        self.assertEqual(comment.text, 'Valid comment text.')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)

    def test_create_comment_with_empty_text(self):
        comment = Comment(
            post=self.post,
            user=self.user,
            text=''
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_create_comment_with_long_text(self):
        long_text = 'a' * 40001
        comment = Comment(
            post=self.post,
            user=self.user,
            text=long_text
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_comment_delete(self):
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='Text to delete.'
        )
        comment.delete()
        self.assertTrue(comment.is_deleted)
        self.assertEqual(comment.text, '[deleted]')


class PostVoteModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.post = Post.objects.create(
            title='Valid Title',
            text='Valid text.',
            user=self.user
        )

    def test_create_postvote_with_valid_data(self):
        postvote = PostVote.objects.create(
            post=self.post,
            user=self.user,
            vote_type=True
        )
        self.assertEqual(postvote.user, self.user)
        self.assertEqual(postvote.post, self.post)
        self.assertTrue(postvote.vote_type)

    def test_create_postvote_without_user(self):
        postvote = PostVote(
            post=self.post,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            postvote.full_clean()

    def test_create_postvote_without_post(self):
        postvote = PostVote(
            user=self.user,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            postvote.full_clean()

    def test_create_duplicate_postvote(self):
        PostVote.objects.create(
            post=self.post,
            user=self.user,
            vote_type=True
        )
        duplicate_postvote = PostVote(
            post=self.post,
            user=self.user,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            duplicate_postvote.full_clean()


class CommentVoteModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.post = Post.objects.create(
            title='Valid Title',
            text='Valid text.',
            user=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='Valid comment text.'
        )

    def test_create_commentvote_with_valid_data(self):
        commentvote = CommentVote.objects.create(
            comment=self.comment,
            user=self.user,
            vote_type=True
        )
        self.assertEqual(commentvote.user, self.user)
        self.assertEqual(commentvote.comment, self.comment)
        self.assertTrue(commentvote.vote_type)

    def test_create_commentvote_without_user(self):
        commentvote = CommentVote(
            comment=self.comment,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            commentvote.full_clean()

    def test_create_commentvote_without_comment(self):
        commentvote = CommentVote(
            user=self.user,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            commentvote.full_clean()

    def test_create_duplicate_commentvote(self):
        CommentVote.objects.create(
            comment=self.comment,
            user=self.user,
            vote_type=True
        )
        duplicate_commentvote = CommentVote(
            comment=self.comment,
            user=self.user,
            vote_type=True
        )
        with self.assertRaises(ValidationError):
            duplicate_commentvote.full_clean()


if __name__ == '__main__':
    unittest.main()
