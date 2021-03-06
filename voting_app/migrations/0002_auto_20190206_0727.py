# Generated by Django 2.1.4 on 2019-02-06 07:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('voting_app', '0001_squashed_0002_poll_format_modified'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='poll',
            options={'ordering': ('-modified',)},
        ),
        migrations.AddField(
            model_name='poll',
            name='author',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
