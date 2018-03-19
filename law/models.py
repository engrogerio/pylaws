# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Law(models.Model):
    # EMENDA = 1
    # COMPLEMENTAR = 2
    # ORDINARIA = 3
    # DELEGADA = 4
    # PROVISORIA = 5
    # DECRETO = 6
    # RESOLUCAO = 7

    # TYPES=(
    #     (EMENDA, 'Emenda à Constituição'),
    #     (COMPLEMENTAR, 'lei complementar'),
    #     (ORDINARIA, 'lei ordinária'),
    #     (DELEGADA, 'lei delegada'),
    #     (PROVISORIA, 'medida provisória'),
    #     (DECRETO, 'decreto legislativo'),
    #     (RESOLUCAO, 'resolução')
    #     )

    city = models.CharField(max_length=50, blank='true', null='true')
    number = models.CharField(max_length=10, blank='true', null='true')
    summary = models.CharField(max_length=500, blank='true', null='true')
    created_date = models.DateField( blank='true', null='true')
    issued_date = models.DateField( blank='true', null='true')
    is_active = models.IntegerField( blank='true', null='true')
    law_type = models.CharField(max_length=50, blank='true', null='true') #IntegerField(choices = TYPES, default = ORDINARIA)
    created_by = models.CharField(max_length=30, blank='true', null='true')
    text = models.CharField(max_length=60000, blank='true', null='true')
    law_url = models.URLField(blank='true', null='true')
    
    def __unicode__(self):
        return ''.join(self.number)
    
    class Meta:
        unique_together = ('city', 'number',)
