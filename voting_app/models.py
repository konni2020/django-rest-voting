from django.db import models
from django.db.models import Count

class Poll(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def valid_polls():
        return Poll.objects.annotate(num_choices=Count('choice')) \
                    .filter(num_choices__gt=1)



class Choice(models.Model):
    text = models.CharField(max_length=50)
    total = models.PositiveIntegerField(default=0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)