# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0009_application_rejection_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(unique=True, max_length=255, verbose_name='\u5e94\u7528\u540d\u8bcd', blank=True),
            preserve_default=True,
        ),
    ]
