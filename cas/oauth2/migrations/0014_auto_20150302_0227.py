# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0013_auto_20150302_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='name',
            field=models.CharField(max_length=20, verbose_name='\u5e94\u7528\u540d\u8bcd'),
            preserve_default=True,
        ),
    ]
