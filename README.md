# Django Signals

Signal receivers for model lifecycle events — slug generation, welcome mail,
backup before delete, and tag change logging.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py signals_demo
```

## Receivers

| Receiver | Signal | Does |
|----------|--------|------|
| `add_slug` | pre_save on Post | fills the slug from the title if empty |
| `welcome_new_user` | post_save on User | prints a welcome mail when created |
| `backup_post` | pre_delete on Post | copies the post to DeletedPost |
| `log_deleted_post` | post_delete on Post | logs the deletion |
| `track_tags` | m2m_changed on Post.tags | logs pre_add and post_remove with pk_set |
| `log_saved_post` | post_save on Post | bound with connect() instead of the decorator |

They are registered in `notifications/signals.py`, which is imported from
`NotificationsConfig.ready()`.

`signals_demo` runs through all of it and prints the SQL for each step.

## Layout

```
notifications/
  models.py    Post, Tag, DeletedPost
  signals.py   the receivers
  apps.py      imports signals in ready()
  management/commands/signals_demo.py
```
