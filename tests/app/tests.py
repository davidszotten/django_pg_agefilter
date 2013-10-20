from __future__ import absolute_import

from datetime import date

from django.core.exceptions import FieldError
from django.test import TestCase

from django_pg_agefilter import AgeFilter
from tests.app.models import Member, Event, Participant, Application



def age_gt(value):
    return AgeFilter(
        'application__event__start_date',
        'member__date_of_birth',
        "> %s",
        value,
    )


class TestFilter(TestCase):
    def setUp(self):
        member = Member.objects.create(date_of_birth=date(2000, 1, 1))
        event = Event.objects.create(start_date=date(2010, 1, 1))
        application = Application.objects.create(event=event)
        Participant.objects.create(application=application, member=member)

        self.assertEqual(
            Participant.objects.count(),
            1
        )

    def test_basic(self):
        self.assertEqual(
            Participant.objects.filter(age_gt(5)).count(),
            1
        )

        self.assertEqual(
            Participant.objects.filter(age_gt(15)).count(),
            0
        )

    def test_subquery(self):
        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.filter(age_gt(5))
            ).count(),
            1
        )

        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.filter(age_gt(15))
            ).count(),
            0
        )

    def test_age_operator(self):
        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.filter(age__gt=5)
            ).count(),
            1
        )

        self.assertEqual(
            Participant.objects.filter(id__in=
                Participant.objects.filter(age__gt=15)
            ).count(),
            0
        )

    def test_exclude(self):
        self.assertEqual(
            Participant.objects.exclude(age_gt(5)).count(),
            0
        )

        self.assertEqual(
            Participant.objects.exclude(age_gt(15)).count(),
            1
        )

    def test_missing_field(self):
        with self.assertRaises(FieldError):
            Participant.objects.filter(
                AgeFilter(
                    'foo',
                    'bar',
                    "> %s",
                    0,
                )
            )
