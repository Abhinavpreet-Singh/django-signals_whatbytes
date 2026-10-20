# Signals Report

All receivers live in `notifications/signals.py`. The module is imported from
`NotificationsConfig.ready()` so the receivers are registered when the app loads.

## add_slug

**Signal:** `pre_save`, sender `Post`
**Arguments used:** `instance`

Fills in the slug from the title with `slugify()`, but only when the slug is empty,
so an existing slug is never overwritten. It changes `instance.slug` and returns.
It does not call `instance.save()` — the save that triggered the signal has not
finished yet and will write the new value itself. Calling `save()` here would send
`pre_save` again and loop forever.

```
[pre_save] slug set to "django-signals-explained" for "Django Signals Explained"
```

On a later save the slug is already set, so the receiver does nothing and the title
change does not drag the slug along with it.

## welcome_new_user

**Signal:** `post_save`, sender `User`
**Arguments used:** `instance`, `created`

Runs on every user save but only acts when `created` is True, which keeps it from
firing again on later updates. It calls `send_welcome_email()`, a stand-in that
prints instead of sending. Since it never saves the user, there is no recursion.

```
[post_save] new user demo_user
[email] Welcome mail sent to demo@example.com
```

## backup_post

**Signal:** `pre_delete`, sender `Post`
**Arguments used:** `instance`

Copies the post into `DeletedPost` before the row goes away. It has to be `pre_delete`
because by the time `post_delete` runs the row is gone. The receiver only creates the
copy and returns, so the delete carries on as normal.

```
[pre_delete] backed up "Django Signals Explained Again" to DeletedPost
```

## log_deleted_post

**Signal:** `post_delete`, sender `Post`
**Arguments used:** `instance`, `timezone.now()`

Logs after the row is deleted. `instance` is still usable in memory here even though
the database row is gone.

```
[post_delete] "Django Signals Explained Again" removed at 11:17:32
```

## track_tags

**Signal:** `m2m_changed`, sender `Post.tags.through`
**Arguments used:** `instance`, `action`, `pk_set`, `timezone.now()`

`m2m_changed` fires several times per operation, so the receiver checks `action` and
only logs on `pre_add` and `post_remove`. `pk_set` holds the tag ids being added or
removed. The sender is the automatic through model, not `Post`.

```
[m2m pre_add] adding tags [1, 2] to "Django Signals Explained Again" at 11:17:32
[m2m post_remove] removed tags [2] from "Django Signals Explained Again" at 11:17:32
```

## log_saved_post

**Signal:** `post_save`, sender `Post`
**Arguments used:** `instance`, `created`

Bound with `post_save.connect(log_saved_post, sender=Post)` instead of the decorator,
to show both ways of registering. It is a module-level function rather than a lambda
because Django stores receivers as weak references and a lambda would be collected
straight away and never fire.

```
[post_save] post "Django Signals Explained" created
[post_save] post "Django Signals Explained Again" updated
```

## Avoiding recursion

None of the receivers save the model that triggered them. `add_slug` mutates the
instance in place during `pre_save`, and the two `post_save` receivers only read and
print. Where a save inside a receiver is genuinely needed, the usual ways out are
`Model.objects.filter(pk=...).update(...)`, which sends no signals, or a flag on the
instance that the receiver checks before acting.

## Queries

`signals_demo` prints `connection.queries` after each step. Worth noting the delete:

```
BEGIN
INSERT INTO "notifications_deletedpost" (...)
DELETE FROM "notifications_post_tags" WHERE post_id IN (1)
DELETE FROM "notifications_post" WHERE id IN (1)
COMMIT
```

The backup insert from `pre_delete` sits inside the same transaction as the delete,
so if the delete fails the backup is rolled back too.

`connection.queries` is only filled when `DEBUG = True`.
