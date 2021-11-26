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
        ('LGBT', 'LGBT'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER)
    phone = PhoneNumberField(blank=True, unique=True, null=True)
    address = models.CharField(max_length=150)
    citizenship_photo = models.ImageField(
        upload_to='citizenship',
        blank=True,
        null=True,
    )
    display_picture = models.ImageField(
        upload_to='display_picture',
        blank=True,
        null=True,
        default='default/default_dp.png'
    )

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
    reason = models.TextField(max_length=500)
    ACTION = [
        ('Post Remove', 'Post Remove'),
        ('Account Ban', 'Account Ban'),
    ]
    action = models.CharField(max_length=20, choices=ACTION)
    review = models.BooleanField(blank=True, default=False)


class Staff(UserCommons):
    marital_status = models.BooleanField()
    report_review = models.ManyToManyField(Report, blank=True)

    def __str__(self):
        return f'a{self.pk}-{self.account.username}'


class NormalUser(UserCommons):
    verified = models.BooleanField(blank=True, default=False)
    posted_post = models.ManyToManyField(Post, blank=True)

    def __str__(self):
        return f'u{self.pk}-{self.account.username}'


class NGOUser(UserCommons):
    gender = None
    date_of_birth = None
    citizenship_photo = None
    establishment_date = models.DateField()
    field_of_work = MultiSelectField(choices=FIELD_OF_WORK)
    epay_account = models.CharField(max_length=20, blank=True)
    bank = models.OneToOneField(Bank, on_delete=models.CASCADE, blank=True, null=True)
    posted_post = models.ManyToManyField(Post, blank=True, related_name='posted_post')
    poked_on = models.ManyToManyField(Post, blank=True, related_name='poked_on')

    def __str__(self):
        return f'n{self.pk}-{self.account.username}'


class PostAttachment(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PostNormal(PostAttachment):
    post_image = models.ImageField(upload_to='post', blank=True, null=True)
    up_vote = models.ManyToManyField(NormalUser, related_name='up_vote', blank=True)
    down_vote = models.ManyToManyField(NormalUser, related_name='down_vote', blank=True)
    reported_by = models.ManyToManyField(NormalUser, related_name='reported_by', blank=True)


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
    reacted_by = models.ManyToManyField(NormalUser, blank=True)


class PollOption(models.Model):
    option = models.CharField(max_length=50)
    reacted_by = models.ManyToManyField(NormalUser, blank=True)

    def __str__(self):
        return f'{self.pk}-{self.option}'


class PostPoll(PostAttachment):
    option = models.ManyToManyField(PollOption)
    ends_on = models.DateField()
