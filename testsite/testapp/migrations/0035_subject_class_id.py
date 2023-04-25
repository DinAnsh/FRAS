# Generated by Django 3.2.18 on 2023-04-25 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0034_camera_room_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='class_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='testapp.class'),
            preserve_default=False,
        ),
    ]