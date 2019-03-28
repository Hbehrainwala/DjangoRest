# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_extensions.db.models import TitleSlugDescriptionModel
from djmoney.models.fields import MoneyField

class Product(TitleSlugDescriptionModel):
    image = models.ImageField(blank=True)
    price = MoneyField(max_digits=6, decimal_places=2, default_currency='USD')
    unit_single_name = models.CharField(max_length=100) # what do you call one of the product (e.g. item)
    unit_multi_name = models.CharField(max_length=100) # what do you call many of the product (e.g. items)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.title