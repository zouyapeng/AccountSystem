# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0003_application_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='comm',
            field=models.TextField(default=1, verbose_name='\u5e94\u7528\u7b80\u4ecb'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u5e94\u7528\u540d\u8bcd', blank=True),
            preserve_default=True,
        ),
    ]
