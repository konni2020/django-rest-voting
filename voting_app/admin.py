from django.contrib import admin

from voting_app.models import Poll, Choice


admin.site.register(Poll)
admin.site.register(Choice)
