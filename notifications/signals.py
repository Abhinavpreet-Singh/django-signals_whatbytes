from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from .models import DeletedPost, Post


def send_welcome_email(user_email):
    print(f'[email] Welcome mail sent to {user_email}')


@receiver(pre_save, sender=Post)
def add_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
        print(f'[pre_save] slug set to "{instance.slug}" for "{instance.title}"')


@receiver(post_save, sender=User)
def welcome_new_user(sender, instance, created, **kwargs):
    if created:
        print(f'[post_save] new user {instance.username}')
        send_welcome_email(instance.email)


@receiver(pre_delete, sender=Post)
def backup_post(sender, instance, **kwargs):
    DeletedPost.objects.create(title=instance.title, slug=instance.slug, body=instance.body)
    print(f'[pre_delete] backed up "{instance.title}" to DeletedPost')


@receiver(post_delete, sender=Post)
def log_deleted_post(sender, instance, **kwargs):
    print(f'[post_delete] "{instance.title}" removed at {timezone.now():%H:%M:%S}')


@receiver(m2m_changed, sender=Post.tags.through)
def track_tags(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':
        print(f'[m2m pre_add] adding tags {sorted(pk_set)} to "{instance.title}" at {timezone.now():%H:%M:%S}')
    elif action == 'post_remove':
        print(f'[m2m post_remove] removed tags {sorted(pk_set)} from "{instance.title}" at {timezone.now():%H:%M:%S}')


def log_saved_post(sender, instance, created, **kwargs):
    state = 'created' if created else 'updated'
    print(f'[post_save] post "{instance.title}" {state}')


post_save.connect(log_saved_post, sender=Post)
