# Generated by Django 4.2.2 on 2023-08-06 06:20

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('letter', '0002_alter_mailmessage_id_alter_subscribers_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmessage',
            name='message',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='message'),
        ),
    ]
