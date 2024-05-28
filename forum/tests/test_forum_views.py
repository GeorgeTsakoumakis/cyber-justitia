import unittest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from forum.models import Post, Comment, PostVote, CommentVote

CustomUser = get_user_model()


class ForumViewsTestCase(TestCase):
    """
    Test case for forum views.
    """

    def setUp(self):
        """
        TFV1: Set up a test client, user, staff user, post, and comment for use in the tests.
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.staff_user = get_user_model().objects.create_user(
            username='staffuser',
            password='StaffPassword123!',
            email='staffuser@example.com',
            is_staff=True
        )
        self.post = Post.objects.create(
            title='Test Post',
            text='This is a test post.',
            user=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='This is a test comment.'
        )

    def test_access_forums_page(self):
        """
        TFV2: Test accessing the forums page.
        """
        response = self.client.get(reverse('forums'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum.html')

    def test_view_post_detail(self):
        """
        TFV3: Test viewing a post detail page.
        """
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')

    def test_view_non_existent_post(self):
        """
        TFV4: Test viewing a non-existent post.
        """
        response = self.client.get(reverse('post_detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_create_post_with_valid_data(self):
        """
        TFV5: Test creating a post with valid data.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'title': 'New Post',
            'text': 'This is a new post.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_create_post_with_blank_data(self):
        """
        TFV6: Test creating a post with blank data.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'title': '',
            'text': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'postcreation.html')
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('title', form.errors)
        self.assertIn('text', form.errors)

    def test_create_post_when_not_logged_in(self):
        """
        TFV7: Test creating a post when not logged in.
        """
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_create_comment_with_valid_data(self):
        """
        TFV8: Test creating a comment with valid data.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.',
            'comment_form': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='This is a new comment.').exists())

    def test_create_comment_with_blank_data(self):
        """
        TFV9: Test creating a comment with blank data.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': '',
            'comment_form': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')
        self.assertContains(response, 'Comment field is required.')
        self.assertFalse(Comment.objects.filter(post=self.post, user=self.user, text='').exists())

    def test_create_comment_when_not_logged_in(self):
        """
        TFV10: Test creating a comment when not logged in.
        """
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.'
        })
        self.assertRedirects(response, reverse('login'))

    def test_delete_post_as_post_owner(self):
        """
        TFV11: Test deleting a post as the post owner.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_staff(self):
        """
        TFV12: Test deleting a post as a staff member.
        """
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_non_owner_non_staff(self):
        """
        TFV13: Test deleting a post as a non-owner and non-staff member.
        """
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='OtherPassword123!',
            email='otheruser@example.com'
        )
        self.client.login(username='otheruser', password='OtherPassword123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_deleted)

    def test_delete_comment_as_comment_owner(self):
        """
        TFV14: Test deleting a comment as the comment owner.
        """
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_staff(self):
        """
        TFV15: Test deleting a comment as a staff member.
        """
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_non_owner_non_staff(self):
        """
        TFV16: Test deleting a comment as a non-owner and non-staff member.
        """
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='OtherPassword123!',
            email='otheruser@example.com'
        )
        self.client.login(username='otheruser', password='OtherPassword123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_deleted)

    def test_vote_post_upvote(self):
        """
        TFV17: Test upvoting a post.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_post', args=[self.post.slug]), {
            'vote_type': PostVote.VoteType.UPVOTE
        })
        self.assertRedirects(response, reverse('post_detail', args=[self.post.slug]))
        self.assertTrue(PostVote.objects.filter(user=self.user, post=self.post, vote_type=PostVote.VoteType.UPVOTE).exists())

    def test_vote_post_downvote(self):
        """
        TFV18: Test downvoting a post.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_post', args=[self.post.slug]), {
            'vote_type': PostVote.VoteType.DOWNVOTE
        })
        self.assertRedirects(response, reverse('post_detail', args=[self.post.slug]))
        self.assertTrue(PostVote.objects.filter(user=self.user, post=self.post, vote_type=PostVote.VoteType.DOWNVOTE).exists())

    def test_vote_post_invalid_form(self):
        """
        TFV19: Test voting on a post with an invalid form.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_post', args=[self.post.slug]), {
            'vote_type': 'invalid_vote_type'
        })
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'errors/400.html')

    def test_vote_comment_upvote(self):
        """
        TFV20: Test upvoting a comment.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_comment', args=[self.post.slug, self.comment.comment_id]), {
            'vote_type': CommentVote.VoteType.UPVOTE
        })
        self.assertRedirects(response, reverse('post_detail', args=[self.post.slug]))
        self.assertTrue(CommentVote.objects.filter(user=self.user, comment=self.comment, vote_type=CommentVote.VoteType.UPVOTE).exists())

    def test_vote_comment_downvote(self):
        """
        TFV21: Test downvoting a comment.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_comment', args=[self.post.slug, self.comment.comment_id]), {
            'vote_type': CommentVote.VoteType.DOWNVOTE
        })
        self.assertRedirects(response, reverse('post_detail', args=[self.post.slug]))
        self.assertTrue(CommentVote.objects.filter(user=self.user, comment=self.comment, vote_type=CommentVote.VoteType.DOWNVOTE).exists())

    def test_vote_comment_invalid_form(self):
        """
        TFV22: Test voting on a comment with an invalid form.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('vote_comment', args=[self.post.slug, self.comment.comment_id]), {
            'vote_type': 'invalid_vote_type'
        })
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'errors/400.html')



if __name__ == '__main__':
    unittest.main()