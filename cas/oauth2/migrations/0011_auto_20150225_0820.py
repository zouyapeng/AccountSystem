# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth2', '0010_auto_20150210_0741'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOpenID',
            fields=[
                ('openid', models.AutoField(serialize=False, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('application', models.ForeignKey(to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['-created', '-id']},
        ),
    ]
