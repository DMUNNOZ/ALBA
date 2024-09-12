# Generated by Django 5.0.4 on 2024-04-16 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albacsp_app', '0007_rename_app_cap_device_apps_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='connection',
            name='wireless',
        ),
        migrations.AddField(
            model_name='connectivity',
            name='wireless',
            field=models.BooleanField(default=True),
        ),
    ]
