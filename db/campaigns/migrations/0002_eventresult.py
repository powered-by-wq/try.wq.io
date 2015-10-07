# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vera', '0003_result'),
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventResult',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('event_date', models.DateField()),
                ('result_value_numeric', models.FloatField(null=True, blank=True)),
                ('result_value_text', models.TextField(null=True, blank=True)),
                ('result_empty', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to='campaigns.Event')),
                ('event_campaign', models.ForeignKey(to='campaigns.Campaign')),
                ('event_site', models.ForeignKey(to='vera.Site', null=True, blank=True)),
                ('result', models.ForeignKey(to='vera.Result')),
            ],
            options={
                'abstract': False,
                'db_table': 'wq_eventresult',
            },
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_report',
            field=models.ForeignKey(to='campaigns.Report'),
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_type',
            field=models.ForeignKey(to='campaigns.Parameter'),
        ),
        migrations.AlterUniqueTogether(
            name='eventresult',
            unique_together=set([('event', 'result_type')]),
        ),
    ]
