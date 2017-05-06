# -*- coding: utf-8 -*-

from django.db import models


class Birthday(models.Model):
    charid = models.IntegerField(verbose_name=u'ID', primary_key=True)
    name = models.TextField(verbose_name=u'Имя персонажа')
    day = models.IntegerField(verbose_name=u'День')
    month = models.IntegerField(verbose_name=u'Месяц')
    series = models.TextField(verbose_name=u'Произведение')
    original_name = models.TextField(verbose_name=u'Имя на японском')
    photo = models.TextField(verbose_name=u'Фотография')
    important = models.BooleanField(verbose_name=u'Важный персонаж')

    class Meta:
        unique_together = ('name', 'day', 'month')
        verbose_name = u'День рождения'
        verbose_name_plural = u'Дни рождения'
        db_table = 'birthdays'
        ordering = ['name', 'month', 'day']


class TweetTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    template = models.CharField(max_length=140, verbose_name=u'Шаблон')

    def __unicode__(self):
        return self.template

    class Meta:
        verbose_name = u'Шаблон поздравления'
        verbose_name_plural = u'Шаблоны поздравлений'
        db_table = 'tweet_templates'