from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    def __str__(self):
        return self.title


class DeletedPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (deleted)'
