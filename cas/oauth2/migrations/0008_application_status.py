# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2', '0007_auto_20150209_0546'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.IntegerField(default=1, max_length=1, choices=[(1, '\u672a\u63d0\u4ea4\u5ba1\u6838'), (2, '\u5ba1\u6838\u4e2d'), (3, '\u5ba1\u6838\u9a73\u56de'), (4, '\u5df2\u4e0a\u7ebf')]),
            preserve_default=True,
        ),
    ]
