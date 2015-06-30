# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0004_auto_20150205_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
