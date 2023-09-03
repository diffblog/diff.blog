from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import BlogSuggestion, UserProfile
from django.contrib.auth import authenticate
from unittest.mock import patch, Mock

class SuggestViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.create(auth=self.user, github_username='testuser_github')  # fill in any other required fields

        self.staff_user = User.objects.create_user(username='staffuser', password='password', is_staff=True)
        self.staff_user_profile = UserProfile.objects.create(auth=self.staff_user, github_username='staffuser_github')  # fill in any other required fields

    def test_get_suggest_view(self):
        response = self.client.get(reverse('suggest'), {'username': 'test_username'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_username')

    def test_post_suggest_view_as_anonymous(self):
        response = self.client.post(reverse('suggest'), {'username': 'test_username', 'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BlogSuggestion.objects.filter(username='test_username').exists())

    def test_post_suggest_view_as_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('suggest'), {'username': 'test_username', 'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        suggestion = BlogSuggestion.objects.get(username='test_username')
        self.assertEqual(suggestion.suggested_by, self.user.profile)

    @patch('app.views.refresh_profile_from_github')
    @patch('app.views._set_feed_url_from_blog_url')
    def test_post_suggest_view_as_staff(self, mock_set_feed_url, mock_populate_details):
        self.client.login(username='staffuser', password='password')
        response = self.client.post(reverse('suggest'), {'username': 'test_username', 'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(github_username='test_username').exists())

        created_user_profile = UserProfile.objects.get(github_username='test_username')
        mock_populate_details.assert_called_with(created_user_profile)
        mock_set_feed_url.assert_called_with(created_user_profile)
