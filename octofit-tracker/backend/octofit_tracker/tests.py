import os
from datetime import timedelta
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Activity, Leaderboard, Team, User, Workout


class OctofitModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='thundergod', email='thundergod@mhigh.edu', password='thundergodpassword'
        )

    def test_user(self):
        self.assertEqual(str(self.user), 'thundergod')
        self.assertEqual(User.objects.count(), 1)

    def test_team(self):
        team = Team.objects.create(name='Blue Team')
        team.members.add(self.user)
        self.assertEqual(str(team), 'Blue Team')
        self.assertEqual(team.members.count(), 1)

    def test_activity(self):
        activity = Activity.objects.create(
            user=self.user, activity_type='Cycling', duration=timedelta(hours=1)
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.duration, timedelta(hours=1))

    def test_leaderboard(self):
        entry = Leaderboard.objects.create(user=self.user, score=100)
        self.assertEqual(entry.score, 100)

    def test_workout(self):
        workout = Workout.objects.create(name='Cycling Training', description='Road cycling event')
        self.assertEqual(str(workout), 'Cycling Training')


class OctofitApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='metalgeek', email='metalgeek@mhigh.edu', password='metalgeekpassword'
        )
        team = Team.objects.create(name='Gold Team')
        team.members.add(self.user)
        Activity.objects.create(user=self.user, activity_type='Running', duration=timedelta(minutes=90))
        Leaderboard.objects.create(user=self.user, score=90)
        Workout.objects.create(name='Running Training', description='Training for a marathon')

    def test_api_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ('users', 'teams', 'activities', 'leaderboard', 'workouts'):
            self.assertIn(key, response.data)

    def test_api_root_uses_codespace_url(self):
        with mock.patch.dict(os.environ, {'CODESPACE_NAME': 'my-codespace'}):
            response = self.client.get('/')
        self.assertEqual(
            response.data['users'], 'https://my-codespace-8000.app.github.dev/api/users/'
        )

    def test_list_endpoints(self):
        for name in ('user', 'team', 'activity', 'leaderboard', 'workout'):
            response = self.client.get(reverse(f'{name}-list'))
            self.assertEqual(response.status_code, status.HTTP_200_OK, name)
            self.assertEqual(len(response.data), 1, name)

    def test_user_password_not_exposed(self):
        response = self.client.get(reverse('user-list'))
        self.assertNotIn('password', response.data[0])

    def test_create_workout(self):
        response = self.client.post(
            reverse('workout-list'), {'name': 'Swimming Training', 'description': 'Swim meet'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 2)
