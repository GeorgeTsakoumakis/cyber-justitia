import unittest

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from forum.models import Post, Comment, PostVote, CommentVote

# Get the CustomUser model
CustomUser = get_user_model()


class PostModelTests(TestCase):
    """
    Test case for the Post model.
    """

    def setUp(self):
        """
        TFM1: Set up a test user for use in the tests.
        """
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )

    def test_create_post_with_valid_data(self):
        """
        TFM2: Test creating a post with valid data.
        """
        post = Post.objects.create(
            title='Valid Title',
            text='Valid text.',
            user=self.user
        )
        self.assertEqual(post.title, 'Valid Title')
        self.assertEqual(post.text, 'Valid text.')
        self.assertEqual(post.user, self.user)

    def test_create_post_with_empty_title(self):
        """
        TFM3: Test creating a post with an empty title.
        """
        post = Post(
            title='',
            text='Valid text.',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_long_title(self):
        """
        TFM4: Test creating a post with a title exceeding the maximum length.
        """
        long_title = 'a' * 257
        post = Post(
            title=long_title,
            text='Valid text.',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_empty_text(self):
        """
        TFM5: Test creating a post with empty text.
        """
        post = Post(
            title='Valid Title',
            text='',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_create_post_with_long_text(self):
        """
        TFM6: Test creating a post with text exceeding the maximum length.
        """
        long_text = 'a' * 40001
        post = Post(
            title='Valid Title',
            text=long_text,
            user=self.user
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_post_slug_is_unique(self):
        """
        TFM7: Test that each post has a unique slug.
        """
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
        """
        TFM8: Test deleting a post.
        """
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
    """
    Test case for the Comment model.
    """

    def setUp(self):
        """
        TFM9: Set up a test user and post for use in the tests.
        """
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
        """
        TFM10: Test creating a comment with valid data.
        """
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='Valid comment text.'
        )
        self.assertEqual(comment.text, 'Valid comment text.')
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)

    def test_create_comment_with_empty_text(self):
        """
        TFM11: Test creating a comment with an empty text.
        """
        comment = Comment(
            post=self.post,
            user=self.user,
            text=''
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_create_comment_with_long_text(self):
        """
        TFM12: Test creating a comment with text exceeding the maximum length.
        """
        long_text = 'a' * 40001
        comment = Comment(
            post=self.post,
            user=self.user,
            text=long_text
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_comment_delete(self):
        """
        TFM13: Test deleting a comment.
        """
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='Text to delete.'
        )
        comment.delete()
        self.assertTrue(comment.is_deleted)
        self.assertEqual(comment.text, '[deleted]')


class PostVoteModelTests(TestCase):
    """
    Test case for the PostVote model.
    """

    def setUp(self):
        """
        TFM14: Set up a test user and post for use in the tests.
        """
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
        """
        TFM15: Test creating a PostVote with valid data.
        """
        postvote = PostVote.objects.create(
            post=self.post,
            user=self.user,
            vote_type="up"
        )
        self.assertEqual(postvote.user, self.user)
        self.assertEqual(postvote.post, self.post)
        self.assertTrue(postvote.vote_type)

    def test_create_postvote_without_user(self):
        """
        TFM16: Test creating a PostVote without specifying a user.
        """
        postvote = PostVote(
            post=self.post,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            postvote.full_clean()

    def test_create_postvote_without_post(self):
        """
        TFM17: Test creating a PostVote without specifying a post.
        """
        postvote = PostVote(
            user=self.user,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            postvote.full_clean()

    def test_create_duplicate_postvote(self):
        """
        TFM18: Test creating a duplicate PostVote.
        """
        PostVote.objects.create(
            post=self.post,
            user=self.user,
            vote_type="up"
        )
        duplicate_postvote = PostVote(
            post=self.post,
            user=self.user,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            duplicate_postvote.full_clean()


class CommentVoteModelTests(TestCase):
    """
    Test case for the CommentVote model.
    """

    def setUp(self):
        """
        TFM19: Set up a test user, post, and comment for use in the tests.
        """
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
        """
        TFM20: Test creating a CommentVote with valid data.
        """
        commentvote = CommentVote.objects.create(
            comment=self.comment,
            user=self.user,
            vote_type="up"
        )
        self.assertEqual(commentvote.user, self.user)
        self.assertEqual(commentvote.comment, self.comment)
        self.assertTrue(commentvote.vote_type)

    def test_create_commentvote_without_user(self):
        """
        TFM21: Test creating a CommentVote without specifying a user.
        """
        commentvote = CommentVote(
            comment=self.comment,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            commentvote.full_clean()

    def test_create_commentvote_without_comment(self):
        """
        TFM22: Test creating a CommentVote without specifying a comment.
        """
        commentvote = CommentVote(
            user=self.user,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            commentvote.full_clean()

    def test_create_duplicate_commentvote(self):
        """
        TFM23: Test creating a duplicate CommentVote.
        """
        CommentVote.objects.create(
            comment=self.comment,
            user=self.user,
            vote_type="up"
        )
        duplicate_commentvote = CommentVote(
            comment=self.comment,
            user=self.user,
            vote_type="up"
        )
        with self.assertRaises(ValidationError):
            duplicate_commentvote.full_clean()


if __name__ == '__main__':
    unittest.main()