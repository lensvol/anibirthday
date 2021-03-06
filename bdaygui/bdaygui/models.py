# -*- coding: utf-8 -*-

from django.db import models


def get_default_importance_value():
    return Importance.objects.get_or_create(code=3)[0].id


class Importance(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    code = models.IntegerField(verbose_name=u'Код')
    name = models.CharField(max_length=16, verbose_name=u'Наименование')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Степень важности'
        verbose_name_plural = u'Степени важности'
        db_table = 'importance'
        ordering = ['code']


class Birthday(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=u'ID')
    charid = models.IntegerField(verbose_name=u'ID AniDB', null=True, blank=True)
    name = models.TextField(verbose_name=u'Имя персонажа')
    day = models.IntegerField(verbose_name=u'День')
    month = models.IntegerField(verbose_name=u'Месяц')
    series = models.TextField(verbose_name=u'Произведение', blank=True)
    original_name = models.TextField(verbose_name=u'Имя на японском', blank=True, null=True)
    photo = models.TextField(verbose_name=u'Фотография', blank=True)
    importance = models.ForeignKey(Importance, null=False,
                                   default=get_default_importance_value,
                                   verbose_name=u'Важность персонажа')

    def __unicode__(self):
        return u'Birthday: {0} [#{1}] on {2}.{3}'.format(
            self.name,
            self.charid,
            self.day,
            self.month,
        )

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
