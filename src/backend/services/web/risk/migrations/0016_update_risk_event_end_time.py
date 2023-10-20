# Generated by Django 3.2.18 on 2023-09-19 03:10

from django.db import migrations
from django.utils import timezone

from services.web.risk.models import Risk


def update_event_end_time(*args, **kwargs):
    Risk.objects.all().update(event_end_time=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ("risk", "0015_risk_event_end_time"),
    ]

    operations = [migrations.RunPython(update_event_end_time)]