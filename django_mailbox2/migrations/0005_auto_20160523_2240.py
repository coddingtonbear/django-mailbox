from django.db import migrations, models
import django_mailbox2.utils


class Migration(migrations.Migration):

    dependencies = [
        ("django_mailbox2", "0004_bytestring_to_unicode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="messageattachment",
            name="document",
            field=models.FileField(
                upload_to=django_mailbox2.utils.get_attachment_save_path,
                verbose_name="Document",
            ),
        ),
    ]
