"""
Django admin for ifxsemanticdata
"""
from django.contrib import admin
from ifxsemanticdata.models import SemanticData


class SemanticDataAdmin(admin.ModelAdmin):
    '''
    Admin for Dewars
    '''
    fields = ('name', 'thing', 'property', 'value', 'table', 'key')
    list_display = ('name', 'thing', 'property', 'value', 'table', 'key')
    ordering = ('thing', 'name', 'property', 'value')
    search_fields = ('name', 'thing', 'property', 'value')
    list_filter = ('thing', 'table')


admin.site.register(SemanticData, SemanticDataAdmin)
