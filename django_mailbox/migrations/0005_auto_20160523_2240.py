from django.db import migrations, models
from functools import partial
import django_mailbox.utils


class Migration(migrations.Migration):
    dependencies = [
        ('django_mailbox', '0004_bytestring_to_unicode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageattachment',
            name='document',
            field=models.FileField(
                upload_to=partial(django_mailbox.utils.get_save_path, setting='attachment_upload_to'),
                verbose_name='Document'),
        ),
    ]
