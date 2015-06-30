# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0002_remove_application_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='icon',
            field=models.ImageField(null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
