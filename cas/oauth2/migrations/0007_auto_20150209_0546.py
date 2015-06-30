# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0006_auto_20150205_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='authorization_grant_type',
            field=models.CharField(default='authorization-code', max_length=32, choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='application',
            name='client_type',
            field=models.CharField(default='confidential', max_length=32, choices=[('confidential', 'Confidential'), ('public', 'Public')]),
            preserve_default=True,
        ),
    ]
