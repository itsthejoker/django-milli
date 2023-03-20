from django.db import models


class SaveMe(models.Model):
    name = models.CharField(max_length=400)

    def __str__(self):
        return self.name

class IgnoreMe(models.Model):
    name = models.CharField(max_length=400)
