import unittest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from forum.models import Post, Comment

CustomUser = get_user_model()


class ForumViewsTestCase(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('forums'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum.html')

    def test_view_post_detail(self):
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')

    def test_view_non_existent_post(self):
        response = self.client.get(reverse('post_detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_create_post_with_valid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'title': 'New Post',
            'text': 'This is a new post.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_create_post_with_blank_data(self):
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
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_create_comment_with_valid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.',
            'comment_form': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='This is a new comment.').exists())

    # fails
    def test_create_comment_with_blank_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': '',
            'comment_form': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')
        self.assertContains(response, 'Comment field is required.')  # Assuming the form has this validation message
        self.assertFalse(Comment.objects.filter(post=self.post, user=self.user).exists())

    def test_create_comment_when_not_logged_in(self):
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.'
        })
        self.assertRedirects(response, reverse('login'))

    def test_delete_post_as_post_owner(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_staff(self):
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_non_owner_non_staff(self):
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
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_staff(self):
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_non_owner_non_staff(self):
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


if __name__ == '__main__':
    unittest.main()