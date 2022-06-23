from django.contrib import admin

# Register your models here.
from core.models import *

admin.site.register([Staff, PeopleUser, NGOUser, Bank, Post, PostNormal, PostRequest, PostPoll, Report, PollOption])
