# Generated by Django 2.1.4 on 2019-01-05 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('voting_app', '0001_squashed_0002_poll_modified'), ('voting_app', '0002_poll_format_modified')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=50)),
                ('total', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('format_modified', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='choice',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting_app.Poll'),
        ),
    ]
