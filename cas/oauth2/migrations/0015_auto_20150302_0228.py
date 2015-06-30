# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0014_auto_20150302_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='comm',
            field=models.TextField(max_length=400, verbose_name='\u5e94\u7528\u7b80\u4ecb'),
            preserve_default=True,
        ),
    ]
