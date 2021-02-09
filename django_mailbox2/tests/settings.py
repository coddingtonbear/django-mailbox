DATABASES = {
    "default": {
        "NAME": "db.sqlite3",
        "ENGINE": "django.db.backends.sqlite3",
    },
}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django_mailbox2",
]
SECRET_KEY = "beepboop"
