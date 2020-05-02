# -*- coding: utf-8 -*-

'''
Semantic data model for migrating semantic data into ifx applications

Created on  2020-04-30

@author: Meghan Correa <mportermahoney@g.harvard.edu>
@copyright: 2020 The Presidents and Fellows of Harvard College.
All rights reserved.
@license: GPL v2.0
'''
from django.db import models

class SemanticData(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, default=None)
    thing = models.CharField(max_length=255, blank=True, null=True, default=None)
    property = models.CharField(max_length=255, blank=True, null=True, default=None)
    value = models.CharField(max_length=255, blank=True, null=True, default=None)
    table = models.CharField(max_length=255, blank=True, null=True, default=None)
    key = models.IntegerField(
        help_text='id for this data in the table from table column',
        default=None,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'semantic_data'

    def __str__(self):
        return '{} {} {}'.format(self.thing, self.name, self.property)
