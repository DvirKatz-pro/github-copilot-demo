from django.core.management.base import BaseCommand
from django.db import transaction

from octofit_tracker import test_data
from octofit_tracker.models import Activity, Leaderboard, Team, User, Workout


class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data for users, teams, activity, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.stdout.write('Deleting existing data...')
            for model in (Leaderboard, Activity, Team, Workout, User):
                model.objects.all().delete()

            users = {data['username']: User.objects.create(**data) for data in test_data.USERS}

            for name in test_data.TEAMS:
                team = Team.objects.create(name=name)
                team.members.add(*users.values())

            for username, activity_type, duration in test_data.ACTIVITIES:
                Activity.objects.create(user=users[username], activity_type=activity_type, duration=duration)

            for username, score in test_data.LEADERBOARD:
                Leaderboard.objects.create(user=users[username], score=score)

            for name, description in test_data.WORKOUTS:
                Workout.objects.create(name=name, description=description)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
