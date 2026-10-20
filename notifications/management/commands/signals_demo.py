from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection, reset_queries

from notifications.models import DeletedPost, Post, Tag


def show_queries(label):
    print(f'  SQL for {label}: {len(connection.queries)} queries')
    for query in connection.queries:
        print(f'    {query["sql"][:100]}')
    reset_queries()


class Command(BaseCommand):
    help = 'Demonstrate the signal receivers'

    def handle(self, *args, **options):
        Post.objects.all().delete()
        DeletedPost.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.filter(username='demo_user').delete()
        reset_queries()

        print('\n1. Creating a post without a slug')
        post = Post.objects.create(title='Django Signals Explained', body='A short post.')
        print(f'  slug is now "{post.slug}"')
        show_queries('create')

        print('\n2. Updating the post, slug is kept')
        post.title = 'Django Signals Explained Again'
        post.save()
        print(f'  slug is still "{post.slug}"')
        show_queries('update')

        print('\n3. Creating a user')
        User.objects.create_user('demo_user', 'demo@example.com', 'pass12345')
        show_queries('user create')

        print('\n4. Adding tags')
        django_tag = Tag.objects.create(name='django')
        python_tag = Tag.objects.create(name='python')
        reset_queries()
        post.tags.add(django_tag, python_tag)
        show_queries('tags add')

        print('\n5. Removing a tag')
        post.tags.remove(python_tag)
        show_queries('tags remove')

        print('\n6. Deleting the post')
        post.delete()
        show_queries('delete')

        backup = DeletedPost.objects.first()
        print(f'\nDeletedPost now holds: "{backup.title}" (slug "{backup.slug}")')
        print(f'Posts left: {Post.objects.count()}, backups: {DeletedPost.objects.count()}')
