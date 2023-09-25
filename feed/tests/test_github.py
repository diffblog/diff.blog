from feed.github import get_or_create_profile_from_github_id_and_github_username

from django.test import TestCase
from unittest.mock import patch
from app.models import UserProfile

class GetOrCreateProfileFromGithubTest(TestCase):

    @patch('feed.github.refresh_profile_from_github')
    def test_existing_user_with_same_github_id_and_username(self, mock_refresh):
        UserProfile.objects.create(github_id=123, github_username="john_doe")
        user = get_or_create_profile_from_github_id_and_github_username(123, "john_doe")
        self.assertEqual(user.github_id, 123)
        self.assertEqual(user.github_username, "john_doe")
        mock_refresh.assert_not_called()

    @patch('feed.github.refresh_profile_from_github')
    def test_existing_user_with_different_github_username(self, mock_refresh):
        UserProfile.objects.create(github_id=123, github_username="john_doe")
        user = get_or_create_profile_from_github_id_and_github_username(123, "new_john_doe")
        self.assertEqual(user.github_id, 123)
        self.assertEqual(user.github_username, "new_john_doe")
        mock_refresh.assert_not_called()

    @patch('feed.github.refresh_profile_from_github')
    @patch('feed.github.get_user_profile')
    def test_non_existing_user_but_existing_username(self, mock_get_user_profile, mock_refresh):
        mock_user = UserProfile(github_id=999, github_username="john_doe")
        mock_get_user_profile.return_value = mock_user
        user = get_or_create_profile_from_github_id_and_github_username(123, "john_doe")
        self.assertEqual(user.github_id, 999)
        self.assertEqual(user.github_username, "john_doe")
        mock_refresh.assert_not_called()

    @patch('feed.github.refresh_profile_from_github')
    @patch('feed.github.get_user_profile')
    def test_new_user(self, mock_get_user_profile, mock_refresh):
        mock_get_user_profile.return_value = None
        user = get_or_create_profile_from_github_id_and_github_username(123, "john_doe")
        self.assertEqual(user.github_id, 123)
        self.assertEqual(user.github_username, "john_doe")
        mock_refresh.assert_called_once_with(user)
