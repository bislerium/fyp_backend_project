# Generated by Django 3.2.8 on 2022-06-04 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20220604_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ngouser',
            name='display_picture',
            field=models.ImageField(blank=True, null=True, upload_to='display_picture'),
        ),
        migrations.AlterField(
            model_name='peopleuser',
            name='display_picture',
            field=models.ImageField(blank=True, null=True, upload_to='display_picture'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='display_picture',
            field=models.ImageField(blank=True, null=True, upload_to='display_picture'),
        ),
    ]