# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-30 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0023_auto_20160324_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='filter_expression',
            field=models.TextField(default='true'),
            preserve_default=False,
        ),
    ]
