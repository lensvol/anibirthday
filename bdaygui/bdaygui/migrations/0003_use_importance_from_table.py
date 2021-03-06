# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-23 08:02
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.migrations import RunPython
from django.template.backends import django

import bdaygui


def convert_current_values(apps, schema_editor):
    Importance = apps.get_model('bdaygui', 'Importance')
    Birthday = apps.get_model('bdaygui', 'Birthday')
    db_alias = schema_editor.connection.alias

    important = Importance.objects.get(code=1)
    not_important = Importance.objects.get(code=2)

    Birthday.objects.using(db_alias).filter(
        important=True
    ).update(
        importance=important
    )

    Birthday.objects.using(db_alias).filter(
        important=False
    ).update(
        importance=not_important
    )


def reverse_conversion(apps, schema_editor):
    Importance = apps.get_model('bdaygui', 'Importance')
    Birthday = apps.get_model('bdaygui', 'Birthday')
    db_alias = schema_editor.connection.alias

    important = Importance.objects.get(code=1)
    not_important = Importance.objects.get(code=2)

    Birthday.objects.using(db_alias).filter(
        importance=important
    ).update(
        important=True
    )

    Birthday.objects.using(db_alias).filter(
        importance=not_important
    ).update(
        important=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ('bdaygui', '0002_importance'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthday',
            name='importance',
            field=models.ForeignKey(default=bdaygui.models.get_default_importance_value,
                                    on_delete=models.deletion.CASCADE,
                                    to='bdaygui.Importance',
                                    verbose_name='\u0412\u0430\u0436\u043d\u043e\u0441\u0442\u044c \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0430'),
        ),
        RunPython(convert_current_values, reverse_conversion),
    ]
