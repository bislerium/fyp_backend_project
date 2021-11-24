# Generated by Django 3.2.8 on 2021-11-23 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postnormal',
            name='report',
        ),
        migrations.AddField(
            model_name='postnormal',
            name='reported_by',
            field=models.ManyToManyField(blank=True, related_name='reported_by', to='core.NormalUser'),
        ),
    ]
