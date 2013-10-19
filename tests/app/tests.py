from __future__ import absolute_import

from datetime import date

from django.test import TestCase
from tests.app.models import Member, Event, Participant, Application


class TestFilter(TestCase):
    def setUp(self):
        member = Member.objects.create(date_of_birth=date(2000, 1, 1))
        event = Event.objects.create(start_date=date(2010, 1, 1))
        application = Application.objects.create(event=event)
        Participant.objects.create(application=application, member=member)

    def test_basic(self):
        self.assertEqual(
            Participant.objects.all().count(),
            1
        )
        self.assertEqual(
            Participant.objects.all().test("> %s", 5).count(),
            1
        )
        self.assertEqual(
            Participant.objects.all().test("> %s", 15).count(),
            0
        )

    def test_subquery(self):
        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.all().test("> %s", 5)
            ).count(),
            1
        )

        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.all().test("> %s", 15)
            ).count(),
            0
        )
