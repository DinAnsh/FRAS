# Generated by Django 3.2.18 on 2023-02-27 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0008_student_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='img',
            field=models.ImageField(upload_to='testapp/students'),
        ),
    ]