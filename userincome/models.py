from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.

class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserIncome(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    date = models.DateField(default=now)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.source

    class Meta:
        ordering = ['-date']
        