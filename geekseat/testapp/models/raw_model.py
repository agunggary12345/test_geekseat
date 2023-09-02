from django.db import models


class RawModel(models.Model):

    class Meta:
        managed = False
