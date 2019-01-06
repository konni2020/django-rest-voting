from django.utils import timezone
from django.db import models
from django.db.models import Count

class Poll(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    modified = models.DateTimeField(auto_now=True)
    format_modified = models.CharField(blank=True, null=True, max_length=100)

    def __str__(self):
        return '{id} - {desc}'.format(id=self.id, desc=self.description)

    def save(self, *args, **kwargs):
        self.save_format_modified()
        super().save(*args, **kwargs)

    def save_format_modified(self):
        if self.modified:
            self.format_modified = self.modified.strftime('%Y-%m-%d %H:%M:%S')
        else:
            self.format_modified = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def valid_polls():
        return Poll.objects.annotate(num_choices=Count('choice')) \
                    .filter(num_choices__gt=1)


class Choice(models.Model):
    text = models.CharField(max_length=50)
    total = models.PositiveIntegerField(default=0)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

    def __str__(self):
        return self.text