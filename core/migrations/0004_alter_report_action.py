# Generated by Django 3.2.8 on 2022-01-13 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_staff_report_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='action',
            field=models.CharField(blank=True, choices=[('Post Remove', 'Post Remove'), ('Account Ban', 'Account Ban'), ('Ignore', 'Ignore')], max_length=20),
        ),
    ]
