# Generated by Django 3.2.8 on 2021-11-30 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_ngouser_epay_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ngouser',
            name='full_name',
            field=models.CharField(max_length=150, verbose_name='Organization Name'),
        ),
    ]
