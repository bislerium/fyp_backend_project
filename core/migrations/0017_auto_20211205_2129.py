# Generated by Django 3.2.8 on 2021-12-05 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_report_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peopleuser',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('LGBTQ+', 'LGBTQ+')], max_length=6),
        ),
        migrations.AlterField(
            model_name='staff',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('LGBTQ+', 'LGBTQ+')], max_length=6),
        ),
    ]
