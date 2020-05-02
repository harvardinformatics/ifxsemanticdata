"""ifxsemanticdata URL Configuration

This is just for testing purposes
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(r'semanticdata/djadmin/', admin.site.urls),
]
