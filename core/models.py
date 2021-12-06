from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField

from django.db import models

# Create your models here.

FIELD_OF_WORK = [
    ('Advocacy & Awareness', 'Advocacy & Awareness'),
    ('Agriculture', 'Agriculture'),
    ('Business & Economic Policy', 'Business & Economic Policy'),
    ('Child Education', 'Child Education'),
    ('Youth Empowerment', 'Youth Empowerment'),
    ('Citizenship', 'Citizenship'),
    ('Communication', 'Communication'),
    ('Conflict Resolution', 'Conflict Resolution'),
    ('Peace Building', 'Peace Building'),
    ('ICT', 'ICT'),
    ('Culture & Society', 'Culture & Society'),
    ('Democracy & Civic Rights', 'Democracy & Civic Rights'),
    ('Rural Development', 'Rural Development'),
    ('Disability & Handicap', 'Disability & Handicap'),
    ('Displaced Population & Refugees', 'Displaced Population & Refugees'),
    ('Education', 'Education'),
    ('Environment', 'Environment'),
    ('Family Care', 'Family Care'),
    ('Women’s Rights', 'Women’s Rights'),
    ('Governance', 'Governance'),
    ('Health', 'Health'),
    ('Human Rights', 'Human Rights'),
    ('Charity/Philanthropy', 'Charity/Philanthropy'),
    ('Labor', 'Labor'),
    ('Law & Legal Affairs', 'Law & Legal Affairs'),
    ('Migrant Workers', 'Migrant Workers'),
    ('Relief', 'Relief'),
    ('Reconstruction', 'Reconstruction'),
    ('Rehabilitation', 'Rehabilitation'),
    ('Research & Studies', 'Research & Studies'),
    ('Science', 'Science'),
    ('Social Media', 'Social Media'),
    ('Technology', 'Technology'),
    ('Transparency', 'Transparency'),
    ('Training & Capacity Building', 'Training & Capacity Building'),
]


class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100)
    bank_BSB = models.CharField(max_length=10)
    bank_account_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=20)


class UserCommons(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True)
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('LGBTQ+', 'LGBTQ+'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER)
    phone = PhoneNumberField(blank=True, unique=True, null=True)
    address = models.CharField(max_length=150)
    display_picture = models.ImageField(
        upload_to='display_picture',
        blank=True,
        null=True,
        default='default/default_dp.png'
    )
    citizenship_photo = models.ImageField(
        upload_to='citizenship',
        blank=True,
        null=True,
    )
    verified = models.BooleanField(blank=True, default=False)

    def get_acronym_name(self):
        return ''.join(c[0].capitalize() for c in self.full_name.split())

    class Meta:
        abstract = True


class Post(models.Model):
    related_to = MultiSelectField(choices=FIELD_OF_WORK)
    text_body = models.TextField(max_length=500)
    created_on = models.DateTimeField(auto_now=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    anonymous = models.BooleanField(blank=True, default=False)
    removed = models.BooleanField(blank=True, default=False)
    POST_TYPE = [
        ('Normal', 'Normal'),
        ('Request', 'Request'),
        ('Poll', 'Poll'),
    ]
    post_type = models.CharField(max_length=20, choices=POST_TYPE)


class Report(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    reason = models.TextField(max_length=1000, blank=True)
    ACTION = [
        ('Post Remove', 'Post Remove'),
        ('Account Ban', 'Account Ban'),
        ('Account Delete', 'Account Delete'),
    ]
    action = models.CharField(max_length=20, choices=ACTION, blank=True)
    review = models.BooleanField(blank=True, default=False)


class Staff(UserCommons):
    verified = False
    marital_status = models.BooleanField()
    report_review = models.ManyToManyField(Report, blank=True)

    def __str__(self):
        return f'a{self.pk}-{self.account.username}'


class PeopleUser(UserCommons):
    posted_post = models.ManyToManyField(Post, related_name='people_posted_post_rn', blank=True)

    def __str__(self):
        return f'u{self.pk}-{self.account.username}'


class NGOUser(UserCommons):
    gender = None
    date_of_birth = None
    citizenship_photo = None
    full_name = models.CharField(max_length=150, verbose_name='Organization Name')
    establishment_date = models.DateField()
    field_of_work = MultiSelectField(choices=FIELD_OF_WORK)
    epay_account = models.CharField(max_length=20, blank=True, help_text=(
        '- Default: Khalti as an Electronic Payment Gateway'
    ))
    bank = models.OneToOneField(Bank, on_delete=models.CASCADE, blank=True, null=True, )
    swc_affl_cert = models.ImageField(
        upload_to='ngo/swc',
        blank=True,
        null=True,
        verbose_name="Social Welfare Council Affl Certificate"
    )
    pan_cert = models.ImageField(
        upload_to='ngo/pan',
        blank=True,
        null=True,
        verbose_name="PAN Certificate"
    )
    verified = models.BooleanField(blank=True, default=False)
    posted_post = models.ManyToManyField(Post, blank=True, related_name='ngo_posted_post_rn')
    poked_on = models.ManyToManyField(Post, blank=True, related_name='poked_on_rn')

    def __str__(self):
        return f'n{self.pk}-{self.account.username}'


class PostAttachment(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PostNormal(PostAttachment):
    post_image = models.ImageField(upload_to='post_image_rn', blank=True, null=True)
    up_vote = models.ManyToManyField(PeopleUser, related_name='up_vote_rn', blank=True)
    down_vote = models.ManyToManyField(PeopleUser, related_name='down_vote_rn', blank=True)
    reported_by = models.ManyToManyField(PeopleUser, related_name='normal_reported_by_rn', blank=True)


class PostRequest(PostAttachment):
    min = models.IntegerField()
    max = models.IntegerField(null=True, blank=True)
    target = models.IntegerField()
    ends_on = models.DateField()
    REQUEST = [
        ('Petition', 'Petition'),
        ('Join', 'Join'),
    ]
    request_type = models.CharField(max_length=20, choices=REQUEST)
    reacted_by = models.ManyToManyField(PeopleUser, blank=True)
    reported_by = models.ManyToManyField(PeopleUser, related_name='req_reported_by_rn', blank=True)


class PollOption(models.Model):
    option = models.CharField(max_length=50)
    reacted_by = models.ManyToManyField(PeopleUser, blank=True)

    def __str__(self):
        return f'{self.pk}-{self.option}'


class PostPoll(PostAttachment):
    option = models.ManyToManyField(PollOption)
    ends_on = models.DateField()
    reported_by = models.ManyToManyField(PeopleUser, related_name='poll_reported_by_rn', blank=True)

