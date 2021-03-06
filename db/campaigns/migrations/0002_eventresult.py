# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-23 15:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('campaigns', '0001_initial'),
        migrations.swappable_dependency(settings.WQ_SITE_MODEL),
        migrations.swappable_dependency(settings.WQ_RESULT_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='eventresult',
            name='result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.WQ_RESULT_MODEL),
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.WQ_REPORT_MODEL),
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.WQ_PARAMETER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaigns.Campaign'),
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_set', to=settings.WQ_SITE_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='campaign',
            unique_together=set([('slug',)]),
        ),
        migrations.AlterUniqueTogether(
            name='eventresult',
            unique_together=set([('event', 'result_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('campaign', 'site', 'date')]),
        ),
    ]
