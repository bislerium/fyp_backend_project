from django.contrib import admin

# Register your models here.
from core.models import *

admin.site.register([AdministrativeUser, NormalUser, NGOUser, Bank, Post, PostAttachment, PostNormal, PostRequest, PostPoll, Report, PollOption])
