from django.db import models

from django_pg_agefilter import get_age_mixin


class Member(models.Model):
    date_of_birth = models.DateField()


class Event(models.Model):
    start_date = models.DateField()


class Application(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


AgeMixin = get_age_mixin(
    'application__event__start_date',
    'member__date_of_birth',
)


class ParticipantQuerySet(AgeMixin, models.query.QuerySet):
    pass


class ParticipantManager(models.Manager):
    def get_queryset(self):
        return ParticipantQuerySet(self.model, using=self._db)
    get_query_set = get_queryset


class Participant(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    objects = ParticipantManager()
