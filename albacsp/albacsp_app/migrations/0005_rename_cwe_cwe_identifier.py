# Generated by Django 5.0.4 on 2024-04-15 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('albacsp_app', '0004_rename_identifier_cwe_cwe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cwe',
            old_name='cwe',
            new_name='identifier',
        ),
    ]
