from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from multiselectfield import MultiSelectField

from core.constants import contact_number_regex
# Create your models here.
from fyp_backend import settings

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


def validate_latitude(value):
    if -90 <= value <= 90:
        return
    raise ValidationError('Invalid Latitude: Must be exclusively in a range of -90 to 90!')


def validate_longitude(value):
    if -180 <= value <= 180:
        return
    raise ValidationError('Invalid Longitude: Must be exclusively in a range of -180 to 180!')


# Supports Decimal Degrees (DD) Coordinate format (i.e, Lat & long)
class GeoLocation(models.Model):
    latitude = models.DecimalField(max_digits=22, decimal_places=16, validators=[validate_latitude])
    longitude = models.DecimalField(max_digits=22, decimal_places=16, validators=[validate_longitude])

    @property
    def get_gmap_location_url(self):
        return f'https://maps.google.com/?q={self.latitude},{self.longitude}'

    class Meta:
        abstract = True


class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100)
    bank_BSB = models.CharField(max_length=10)
    bank_account_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=20)


def validate_contact_number(value):
    for regex_tup in contact_number_regex:
        for regex in regex_tup:
            if regex.match(value):
                return
    raise ValidationError('Invalid phone number!')


class UserCommons(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True)
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('LGBTQ+', 'LGBTQ+'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER, )
    phone = models.CharField(unique=True, max_length=14, validators=[validate_contact_number])
    address = models.CharField(max_length=150)
    display_picture = models.ImageField(
        upload_to='display_picture',
        blank=True,
        null=True,
        default=settings.DEFAULT_PEOPLE_DP
    )
    citizenship_photo = models.ImageField(
        upload_to='citizenship',
        blank=True,
        null=True,
    )
    is_verified = models.BooleanField(blank=True, default=False)

    @property
    def get_acronym_name(self):
        return ''.join(c[0].capitalize() for c in self.full_name.split())

    class Meta:
        abstract = True


class Post(models.Model):
    related_to = MultiSelectField(choices=FIELD_OF_WORK)
    post_content = models.TextField(max_length=500)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    # is posted anonymmous rename
    is_anonymous = models.BooleanField(blank=True, default=False)
    is_removed = models.BooleanField(blank=True, default=False)
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
        ('Ignore', 'Ignore'),
    ]
    action = models.CharField(max_length=20, choices=ACTION, blank=True)
    is_reviewed = models.BooleanField(blank=True, default=False)


class Staff(UserCommons):
    is_verified = None
    is_married = models.BooleanField(default=False)
    report_review = models.ManyToManyField(Report, blank=True, related_name='report_reviewed_by')

    def __str__(self):
        return f'a{self.pk}-{self.account.username}'


class PeopleUser(UserCommons):
    posted_post = models.ManyToManyField(Post, related_name='people_posted_post_rn', blank=True)

    def __str__(self):
        return f'u{self.pk}-{self.account.username}'


class NGOUser(UserCommons, GeoLocation):
    gender = None
    date_of_birth = None
    citizenship_photo = None
    # replace by org name
    full_name = models.CharField(max_length=150, verbose_name='Organization Name')
    establishment_date = models.DateField()
    display_picture = models.ImageField(
        upload_to='display_picture',
        blank=True,
        null=True,
        default=settings.DEFAULT_NGO_DP
    )
    field_of_work = MultiSelectField(choices=FIELD_OF_WORK)
    epay_account = models.CharField(max_length=20, blank=True, help_text=(
        '- Default: Khalti as an Electronic Payment Gateway'
    ))
    bank = models.OneToOneField(Bank, on_delete=models.SET_NULL, blank=True, null=True, )
    # Social Welfare Council (SWC)
    swc_affl_cert = models.ImageField(
        upload_to='ngo/swc',
        blank=True,
        null=True,
        verbose_name="Social Welfare Council Affl Certificate"
    )
    # Permanent Account Number Certificate
    pan_cert = models.ImageField(
        upload_to='ngo/pan',
        blank=True,
        null=True,
        verbose_name="PAN Certificate"
    )
    # rename to posts
    posted_post = models.ManyToManyField(Post, blank=True, related_name='ngo_posted_post_rn')
    poked_on = models.ManyToManyField(Post, blank=True, related_name='poked_on_rn')

    def __str__(self):
        return f'n{self.pk}-{self.account.username}'


class PostAttachment(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True


class PostNormal(PostAttachment):
    post_image = models.ImageField(upload_to='post_image', blank=True, null=True)
    up_vote = models.ManyToManyField(PeopleUser, related_name='up_vote_rn', blank=True)
    down_vote = models.ManyToManyField(PeopleUser, related_name='down_vote_rn', blank=True)
    reported_by = models.ManyToManyField(PeopleUser, related_name='normal_reported_by_rn', blank=True)


class PostRequest(PostAttachment):
    min = models.IntegerField()
    max = models.IntegerField(null=True, blank=True)
    target = models.IntegerField()
    ends_on = models.DateTimeField()
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
    # rename to options
    option = models.ManyToManyField(PollOption)
    ends_on = models.DateTimeField(blank=True, null=True)
    reported_by = models.ManyToManyField(PeopleUser, related_name='poll_reported_by_rn', blank=True)
