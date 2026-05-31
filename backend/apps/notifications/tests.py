from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class NotificationsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test_user@petcare.com',
            password='Password123!',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_notifications_list(self):
        response = self.client.get('/api/v1/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'list notifications stub')

    def test_notification_read(self):
        response = self.client.patch('/api/v1/notifications/42/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'mark notification 42 as read stub')

    def test_notification_read_all(self):
        response = self.client.patch('/api/v1/notifications/read-all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'mark all notifications as read stub')
