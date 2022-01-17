# Generated by Django 3.2.8 on 2022-01-17 11:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=100)),
                ('bank_branch', models.CharField(max_length=100)),
                ('bank_BSB', models.CharField(max_length=10)),
                ('bank_account_name', models.CharField(max_length=100)),
                ('bank_account_number', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PeopleUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150)),
                ('date_of_birth', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('LGBTQ+', 'LGBTQ+')], max_length=6)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('address', models.CharField(max_length=150)),
                ('display_picture', models.ImageField(blank=True, default='default/default_dp.png', null=True, upload_to='display_picture')),
                ('citizenship_photo', models.ImageField(blank=True, null=True, upload_to='citizenship')),
                ('is_verified', models.BooleanField(blank=True, default=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PollOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=50)),
                ('reacted_by', models.ManyToManyField(blank=True, to='core.PeopleUser')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('related_to', multiselectfield.db.fields.MultiSelectField(choices=[('Advocacy & Awareness', 'Advocacy & Awareness'), ('Agriculture', 'Agriculture'), ('Business & Economic Policy', 'Business & Economic Policy'), ('Child Education', 'Child Education'), ('Youth Empowerment', 'Youth Empowerment'), ('Citizenship', 'Citizenship'), ('Communication', 'Communication'), ('Conflict Resolution', 'Conflict Resolution'), ('Peace Building', 'Peace Building'), ('ICT', 'ICT'), ('Culture & Society', 'Culture & Society'), ('Democracy & Civic Rights', 'Democracy & Civic Rights'), ('Rural Development', 'Rural Development'), ('Disability & Handicap', 'Disability & Handicap'), ('Displaced Population & Refugees', 'Displaced Population & Refugees'), ('Education', 'Education'), ('Environment', 'Environment'), ('Family Care', 'Family Care'), ('Women’s Rights', 'Women’s Rights'), ('Governance', 'Governance'), ('Health', 'Health'), ('Human Rights', 'Human Rights'), ('Charity/Philanthropy', 'Charity/Philanthropy'), ('Labor', 'Labor'), ('Law & Legal Affairs', 'Law & Legal Affairs'), ('Migrant Workers', 'Migrant Workers'), ('Relief', 'Relief'), ('Reconstruction', 'Reconstruction'), ('Rehabilitation', 'Rehabilitation'), ('Research & Studies', 'Research & Studies'), ('Science', 'Science'), ('Social Media', 'Social Media'), ('Technology', 'Technology'), ('Transparency', 'Transparency'), ('Training & Capacity Building', 'Training & Capacity Building')], max_length=546)),
                ('post_content', models.TextField(max_length=500)),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('is_anonymous', models.BooleanField(blank=True, default=False)),
                ('is_removed', models.BooleanField(blank=True, default=False)),
                ('post_type', models.CharField(choices=[('Normal', 'Normal'), ('Request', 'Request'), ('Poll', 'Poll')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True, max_length=1000)),
                ('action', models.CharField(blank=True, choices=[('Post Remove', 'Post Remove'), ('Account Ban', 'Account Ban'), ('Ignore', 'Ignore')], max_length=20)),
                ('is_reviewed', models.BooleanField(blank=True, default=False)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150)),
                ('date_of_birth', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('LGBTQ+', 'LGBTQ+')], max_length=6)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('address', models.CharField(max_length=150)),
                ('display_picture', models.ImageField(blank=True, default='default/default_dp.png', null=True, upload_to='display_picture')),
                ('citizenship_photo', models.ImageField(blank=True, null=True, upload_to='citizenship')),
                ('is_married', models.BooleanField()),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('report_review', models.ManyToManyField(blank=True, related_name='report_reviewed_by', to='core.Report')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min', models.IntegerField()),
                ('max', models.IntegerField(blank=True, null=True)),
                ('target', models.IntegerField()),
                ('ends_on', models.DateField()),
                ('request_type', models.CharField(choices=[('Petition', 'Petition'), ('Join', 'Join')], max_length=20)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
                ('reacted_by', models.ManyToManyField(blank=True, to='core.PeopleUser')),
                ('reported_by', models.ManyToManyField(blank=True, related_name='req_reported_by_rn', to='core.PeopleUser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostPoll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ends_on', models.DateField()),
                ('option', models.ManyToManyField(to='core.PollOption')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
                ('reported_by', models.ManyToManyField(blank=True, related_name='poll_reported_by_rn', to='core.PeopleUser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostNormal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_image', models.ImageField(blank=True, null=True, upload_to='post_image_rn')),
                ('down_vote', models.ManyToManyField(blank=True, related_name='down_vote_rn', to='core.PeopleUser')),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
                ('reported_by', models.ManyToManyField(blank=True, related_name='normal_reported_by_rn', to='core.PeopleUser')),
                ('up_vote', models.ManyToManyField(blank=True, related_name='up_vote_rn', to='core.PeopleUser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='peopleuser',
            name='posted_post',
            field=models.ManyToManyField(blank=True, related_name='people_posted_post_rn', to='core.Post'),
        ),
        migrations.CreateModel(
            name='NGOUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, unique=True)),
                ('address', models.CharField(max_length=150)),
                ('display_picture', models.ImageField(blank=True, default='default/default_dp.png', null=True, upload_to='display_picture')),
                ('is_verified', models.BooleanField(blank=True, default=False)),
                ('full_name', models.CharField(max_length=150, verbose_name='Organization Name')),
                ('establishment_date', models.DateField()),
                ('field_of_work', multiselectfield.db.fields.MultiSelectField(choices=[('Advocacy & Awareness', 'Advocacy & Awareness'), ('Agriculture', 'Agriculture'), ('Business & Economic Policy', 'Business & Economic Policy'), ('Child Education', 'Child Education'), ('Youth Empowerment', 'Youth Empowerment'), ('Citizenship', 'Citizenship'), ('Communication', 'Communication'), ('Conflict Resolution', 'Conflict Resolution'), ('Peace Building', 'Peace Building'), ('ICT', 'ICT'), ('Culture & Society', 'Culture & Society'), ('Democracy & Civic Rights', 'Democracy & Civic Rights'), ('Rural Development', 'Rural Development'), ('Disability & Handicap', 'Disability & Handicap'), ('Displaced Population & Refugees', 'Displaced Population & Refugees'), ('Education', 'Education'), ('Environment', 'Environment'), ('Family Care', 'Family Care'), ('Women’s Rights', 'Women’s Rights'), ('Governance', 'Governance'), ('Health', 'Health'), ('Human Rights', 'Human Rights'), ('Charity/Philanthropy', 'Charity/Philanthropy'), ('Labor', 'Labor'), ('Law & Legal Affairs', 'Law & Legal Affairs'), ('Migrant Workers', 'Migrant Workers'), ('Relief', 'Relief'), ('Reconstruction', 'Reconstruction'), ('Rehabilitation', 'Rehabilitation'), ('Research & Studies', 'Research & Studies'), ('Science', 'Science'), ('Social Media', 'Social Media'), ('Technology', 'Technology'), ('Transparency', 'Transparency'), ('Training & Capacity Building', 'Training & Capacity Building')], max_length=546)),
                ('epay_account', models.CharField(blank=True, help_text='- Default: Khalti as an Electronic Payment Gateway', max_length=20)),
                ('swc_affl_cert', models.ImageField(blank=True, null=True, upload_to='ngo/swc', verbose_name='Social Welfare Council Affl Certificate')),
                ('pan_cert', models.ImageField(blank=True, null=True, upload_to='ngo/pan', verbose_name='PAN Certificate')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('bank', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.bank')),
                ('poked_on', models.ManyToManyField(blank=True, related_name='poked_on_rn', to='core.Post')),
                ('posted_post', models.ManyToManyField(blank=True, related_name='ngo_posted_post_rn', to='core.Post')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
