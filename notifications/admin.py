from django.contrib import admin

from .models import DeletedPost, Post, Tag

admin.site.register([Post, Tag, DeletedPost])
