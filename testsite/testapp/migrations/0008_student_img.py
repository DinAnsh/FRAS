# Generated by Django 3.2.18 on 2023-02-27 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0007_rename_admin_system_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='img',
            field=models.ImageField(default=12, upload_to='students'),
            preserve_default=False,
        ),
    ]