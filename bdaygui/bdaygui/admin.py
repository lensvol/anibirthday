# -*- coding: utf-8 -*-

import datetime

from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from .models import Birthday, TweetTemplate


class CategoryFilter(SimpleListFilter):
    title = (u'Категории')

    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [
            (u'upcoming', u'Грядущие'),
            (u'past', u'Прошедшие'),
            (u'today', u'Сегодня'),
        ]

    def queryset(self, request, queryset):
        today = datetime.date.today()

        if self.value() == 'upcoming':
            return queryset.filter(month__gte=today.month - 1,
                                   day__gte=today.day)
        elif self.value() == 'past':
            return queryset.filter(month__lt=today.month - 1,
                                   day__lt=today.day)
        elif self.value() == 'today':
            return queryset.filter(month=today.month - 1,
                                   day=today.day)
        else:
            return queryset


class BirthdayAdmin(admin.ModelAdmin):
    list_display = ('charid', 'name', 'prepared_series', 'day', 'human_readable_month')
    list_filter = (CategoryFilter, )

    def prepared_series(self, obj):
        return obj.series.replace('\n', '<br>')

    def human_readable_month(self, obj):
        months = [
            u'Январь',
            u'Февраль',
            u'Март',
            u'Апрель',
            u'Май',
            u'Июнь',
            u'Июль',
            u'Август',
            u'Сентябрь',
            u'Октябрь',
            u'Ноябрь',
            u'Декабрь',
        ]

        try:
            return months[obj.month]
        except IndexError:
            return u'???'

    human_readable_month.short_description = u'Месяц'
    human_readable_month.admin_order_field = 'month'
    prepared_series.allow_tags = True


class TweetTemplateAdmin(admin.ModelAdmin):
    list_display = ('template', )


admin.site.register(Birthday, BirthdayAdmin)
admin.site.register(TweetTemplate, TweetTemplateAdmin)