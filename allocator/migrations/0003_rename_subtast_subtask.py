# Generated by Django 4.2.2 on 2023-07-11 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('allocator', '0002_project_remove_user_phone_remove_user_photo_url_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SubTast',
            new_name='SubTask',
        ),
    ]
