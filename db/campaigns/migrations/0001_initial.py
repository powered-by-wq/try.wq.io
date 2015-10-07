# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vera', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=255)),
                ('icon', models.ImageField(upload_to='campaigns')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateField()),
                ('campaign', models.ForeignKey(to='campaigns.Campaign')),
                ('site', models.ForeignKey(to='vera.Site', null=True, blank=True, related_name='event_set')),
            ],
            options={
                'ordering': ('-date', 'campaign', 'site'),
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('is_numeric', models.BooleanField(default=False)),
                ('units', models.CharField(null=True, blank=True, max_length=50)),
                ('description', models.TextField()),
                ('campaign', models.ForeignKey(to='campaigns.Campaign', related_name='parameters')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('entered', models.DateTimeField(blank=True)),
                ('photo', models.ImageField(null=True, blank=True, upload_to='reports')),
                ('event', models.ForeignKey(to='campaigns.Event', related_name='report_set')),
                ('status', models.ForeignKey(to='vera.ReportStatus', null=True, blank=True)),
                ('user', models.ForeignKey(to='auth.User', null=True, blank=True, related_name='campaigns_report')),
            ],
            options={
                'ordering': ('-entered',),
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='campaign',
            unique_together=set([('slug',)]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('campaign', 'site', 'date')]),
        ),
    ]
