from djongo import models
from djongo.models import Model


class Specialization(Model):
    title = models.TextField()
    departament = models.JSONField()


class Departament(Model):
    title = models.TextField()

    class Meta:
        abstract = True
