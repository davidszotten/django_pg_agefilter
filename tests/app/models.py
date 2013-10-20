from django.db import models

from django_pg_agefilter import AgeFilter, get_age_filter


class Member(models.Model):
    date_of_birth = models.DateField()


class Event(models.Model):
    start_date = models.DateField()


class Application(models.Model):
    event = models.ForeignKey(Event)


class ParticipantQuerySet(models.query.QuerySet):

    def filter(self, *args, **kwargs):
        """ Override the default filter to add age__ operators """
        kwarg, op = get_age_filter(kwargs)
        if kwarg is not None:
            value = kwargs.pop(kwarg)
            self = self.filter(AgeFilter(
                    'application__event__start_date',
                    'member__date_of_birth',
                    op,
                    value,
                )
            )
        return super(ParticipantQuerySet, self).filter(*args, **kwargs)


class ParticipantManager(models.Manager):
    def get_query_set(self):
        return ParticipantQuerySet(self.model, using=self._db)


class Participant(models.Model):
    member = models.ForeignKey(Member)
    application = models.ForeignKey(Application)

    objects = ParticipantManager()
