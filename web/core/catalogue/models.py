# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.db import models
from django.db.models import Avg, Count, Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericRelation
from core.messageset.models import Task
from core.adminlte.constants import DICT_NULL_BLANK_TRUE
# Create your models here.
class Tripitaka(models.Model):
    name = models.CharField(u'名称', max_length=64)
    code = models.CharField(u'编码', max_length=4, unique=True)
    era = models.CharField(u'年代', max_length=32)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = u'经藏'

    class Config:
        list_display_fields = ('name', 'code', 'era', 'id')
        list_form_fields = list_display_fields
        search_fields = list_display_fields

class VariantTripitaka(models.Model):
    tripitaka = models.ForeignKey(Tripitaka, null=False, related_name='variants', verbose_name = u'经藏')
    code = models.CharField(u'编码', max_length=6, unique=True)
    vendor = models.CharField(u'出版商', max_length=64)
    pub_date = models.DateField(u'出版日期')
    pub_version = models.CharField(u'版本批次', max_length=12)
    display = models.CharField(u'名称', max_length=64)

    cover = models.ImageField(u'封面信息', upload_to = 'cover', **DICT_NULL_BLANK_TRUE)
    volumes_count = models.SmallIntegerField(u'总册数', default=1)

    is_electronic = models.BooleanField(u'是否为电子版', default=False)

    def __unicode__(self):
        return self.display

    class Meta:
        verbose_name_plural = verbose_name = u'实体经藏'

    class Config:
        list_display_fields = ('display', 'tripitaka', 'code', 'vendor', 'pub_date', 'is_electronic', 'volumes_count', 'id')
        list_form_fields = ('display', 'tripitaka', 'code', 'vendor', 'id', 'pub_date', 'cover', 'is_electronic', 'volumes_count')
        search_fields = list_display_fields

class Volume(models.Model):
    tripitaka = models.ForeignKey(VariantTripitaka, null=False, related_name='volumes', verbose_name = u'经藏')
    code = models.CharField(u'编码', max_length=12, default='', unique=True)
    vol_num = models.SmallIntegerField(u'册序号', default=1)

    pages_count = models.SmallIntegerField(u'总页数', default=0)
    start_page = models.SmallIntegerField(u'起始页码', default=1)
    end_page = models.SmallIntegerField(u'终止页吗', default=1)

    cover = models.ImageField(u'封面信息', upload_to = 'cover')

    @classmethod
    def format_volume(cls, tripitaka, number):
        return '{0}-TV{1:04}'.format(tripitaka.code, number)

    class Meta:
        verbose_name_plural = verbose_name = u'册'

    def __unicode__(self):
        return u'%s %s' % (self.tripitaka.display, self.vol_num)

    class Config:
        list_display_fields = ('tripitaka', 'code', 'vol_num', 'id', 'pages_count', 'start_page', 'end_page')
        list_form_fields = list_display_fields
        search_fields = list_display_fields

@python_2_unicode_compatible
class LQSutra(models.Model):
    code = models.CharField(u'编码', max_length=6, default='')
    name = models.CharField(u'名称', max_length=128, default='')
    translator = models.CharField(u'译者', max_length=32, default='')
    reels_count = models.SmallIntegerField(u'总卷数', default=1)
    is_opened = models.BooleanField(u'是否开放校对', default=False)

    tasks = GenericRelation(Task, related_query_name='tasks')

    def __str__(self):
        return '%s-%s' % (self.name, self.translator)

    class Meta:
        verbose_name_plural = verbose_name = u'龙泉经目'

    class Config:
        list_display_fields = ('name', 'translator', 'code', 'reels_count',  'is_opened', 'id')
        list_form_fields = list_display_fields
        search_fields = list_display_fields

class Sutra(models.Model):
    code = models.CharField(u'编码', max_length=16, default='', unique=True)
    tripitaka = models.ForeignKey(VariantTripitaka, null=False, related_name='sutras', verbose_name = u'经藏')
    normal_sutra = models.ForeignKey(LQSutra, null=True, verbose_name = u'龙泉经目')
    display = models.CharField(u'经本名称', max_length=128, default='')
    era = models.CharField(u'年代', max_length=12, default='')
    author = models.CharField(u'作者', max_length=32, default='', null=True, blank=True)
    translator = models.CharField(u'译者', max_length=32, default='', null=True, blank=True)
    # 译经之前的原始卷数
    reels_count = models.SmallIntegerField(u'总卷数', default=1)

    start_vol = models.SmallIntegerField(u'起始册码', default=0)
    start_page = models.SmallIntegerField(u'终止册码', default=0)
    end_vol = models.SmallIntegerField(u'终止册码', default=0)
    end_page = models.SmallIntegerField(u'终止页码', default=0)
    discription = models.CharField(u'描述信息', max_length=512, default='')

    def __unicode__(self):
         return self.display

    class Meta:
        verbose_name_plural = verbose_name = u'实体经本'

    class Config:
        list_display_fields = ('normal_sutra', 'display', 'tripitaka', 'era', 'reels_count',  'start_vol', 'start_page', 'end_vol', 'end_page', 'id')
        list_form_fields = ('normal_sutra', 'display', 'tripitaka', 'era', 'reels_count', 'id',
                            'author', 'translator', 'start_vol', 'start_page', 'end_vol', 'end_page', 'discription')

# juan (ancient mode)
class Reel(models.Model):
    sutra = models.ForeignKey(Sutra, null=False, related_name='reels', verbose_name = u'实体经本')
    reel_num = models.SmallIntegerField(u'卷序号', default=1)
    code = models.CharField(u'编码', max_length=20, default='', unique=True)
    start_vol = models.SmallIntegerField(u'起始册码', default=0)
    start_page = models.SmallIntegerField(u'终止册码', default=0)
    end_vol = models.SmallIntegerField(u'终止册码', default=0)
    end_page = models.SmallIntegerField(u'终止页码', default=0)
    text_content_trad = models.TextField(u'卷文本（繁体）', default='')
    text_content_simpl = models.TextField(u'卷文本（简体）', default='')

    def __unicode__(self):
        return u'%s %s' % (self.sutra.display, self.reel_num)

    class Meta:
        verbose_name_plural = verbose_name = u'卷信息'

    class Config:
        list_display_fields = ('sutra', 'reel_num', 'code', 'text_content_trad',  'start_vol', 'start_page', 'end_vol', 'end_page', 'id')
        list_form_fields = ('sutra', 'reel_num', 'code', 'text_content_trad',  'start_vol', 'start_page', 'end_vol', 'end_page', 'id')

class Page(models.Model):
    reel = models.ForeignKey(Reel, related_name='pages', null=True, verbose_name = u'所属卷')
    volume = models.ForeignKey(Volume, related_name='pages', null=True, verbose_name = u'所属册')
    sutra = models.ForeignKey(Sutra, related_name='pages', null=True, verbose_name = u'实体经本')
    code = models.CharField(u'编码', max_length=16, default='', unique=True, null=True, blank=True)
    page_num = models.SmallIntegerField(u'总序号', default=1)
    text_content_trad = models.TextField(u'页文本（繁体）', default='')
    text_content_simpl = models.TextField(u'页文本（简体）', default='')

    class Meta:
        verbose_name_plural = verbose_name = u'页信息'

    class Config:
        list_display_fields = ('reel', 'volume', 'sutra', 'code', 'text_content_trad',  'page_num', 'id')
        list_form_fields = ('reel', 'volume', 'sutra', 'code', 'text_content_trad',  'page_num', 'id')

