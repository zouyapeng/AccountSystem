# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0005_accesstoken_created'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accesstoken',
            options={'ordering': ['-created', '-id']},
        ),
        migrations.AddField(
            model_name='application',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
