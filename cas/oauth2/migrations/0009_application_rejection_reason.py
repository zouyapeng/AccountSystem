# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0008_application_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='rejection_reason',
            field=models.TextField(null=True, verbose_name='\u9a73\u56de\u539f\u56e0', blank=True),
            preserve_default=True,
        ),
    ]
