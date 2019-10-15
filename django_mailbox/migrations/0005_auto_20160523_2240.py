from django.db import migrations, models
import django_mailbox.utils


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0004_bytestring_to_unicode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageattachment',
            name='document',
            field=models.FileField(upload_to=django_mailbox.utils.get_attachment_save_path, verbose_name='Document'),
        ),
    ]
