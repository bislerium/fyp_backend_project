import enum
from collections import OrderedDict
from datetime import datetime, timedelta

from dj_rest_auth.serializers import TokenSerializer, LoginSerializer
from django.contrib.auth.models import Group
from django.http.response import HttpResponseServerError
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import serializers, status

import core.models
from .exception import CustomAPIException
from .models import *


class EPostType(enum.Enum):
    Normal = 0
    Poll = 1
    Request = 2


class CustomLoginSerializer(LoginSerializer):

    def _validate_username_email(self, username, email, password):
        user: User = super()._validate_username_email(username, email, password)
        if user:
            if user.groups.exists() and user.groups.first().name in ['NGO', 'General']:
                return user
        return None


class CustomTokenSerializer(TokenSerializer):

    def to_representation(self, instance: Token):
        data = super().to_representation(instance)
        user: User = User.objects.get(username=instance.user)
        group = user.groups.first().name
        data['group'] = group
        data['account_id'] = user.id
        if group == 'General':
            data['profile_id'] = user.peopleuser.id
        if group == 'NGO':
            data['profile_id'] = user.ngouser.id
        return data


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class NGOListSerializer(serializers.ModelSerializer):
    field_of_work = serializers.ListSerializer(child=serializers.CharField(), )

    class Meta:
        model = NGOUser
        fields = ['id', 'address', 'display_picture', 'full_name', 'establishment_date', 'field_of_work']


class NGOSerializer(serializers.ModelSerializer):
    field_of_work = serializers.ListSerializer(child=serializers.CharField(), )

    class Meta:
        model = NGOUser
        exclude = ['poked_on', 'account']

    def to_representation(self, instance: NGOUser):
        data = super().to_representation(instance)
        if instance.bank is not None:
            data['bank'] = BankSerializer(instance.bank).data
        data['username'] = instance.account.username
        data['email'] = instance.account.email
        data['date_joined'] = instance.account.date_joined
        return data


class NormalPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNormal
        exclude = ('reported_by', 'post')

    def to_representation(self, instance: PostNormal):
        data = super().to_representation(instance)
        user: User = self.context.get('request').user
        if user.groups.first().name == 'General':
            if user.peopleuser in instance.up_vote.all():
                data['up_voted'] = True
            if user.peopleuser in instance.down_vote.all():
                data['down_voted'] = True
        return data


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = '__all__'


class PollPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPoll
        exclude = ('reported_by', 'post', 'option')

    def to_representation(self, instance: PostPoll):
        data = super().to_representation(instance)
        user: User = self.context.get('request').user
        if user.groups.first().name == 'General':
            for option in instance.option.all():
                if user.peopleuser in option.reacted_by.all():
                    data['choice'] = option.id
        data['options'] = PollOptionSerializer(instance.option, many=True,
                                               context={'request': self.context.get('request')}).data
        return data


class RequestPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRequest
        exclude = ('reported_by', 'post',)

    def to_representation(self, instance: PostRequest):
        data = super().to_representation(instance)
        user: User = self.context.get('request').user
        if user.groups.first().name == 'General' and user.peopleuser in instance.reacted_by.all():
            data['is_participated'] = True
        return data


class PostListSerializer(serializers.ModelSerializer):
    is_ngo_poked = serializers.BooleanField(default=False)
    related_to = serializers.ListSerializer(child=serializers.CharField(), )

    class Meta:
        model = Post
        fields = ['id', 'related_to', 'post_content', 'is_anonymous', 'is_ngo_poked', 'post_type', 'created_on']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        if instance.post_type == EPostType.Request.name:
            data['post_type'] = f'{instance.postrequest.request_type} {data["post_type"]}'
        if instance.poked_on_rn.count() > 0:
            data['is_ngo_poked'] = True
        else:
            data['is_ngo_poked'] = False
        return data


class NGOOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOUser
        fields = ['id', 'full_name', 'display_picture']


class PostSerializer(serializers.ModelSerializer):
    related_to = serializers.ListSerializer(child=serializers.CharField(), )

    class Meta:
        model = Post
        fields = ['id', 'related_to', 'post_content', 'created_on', 'modified_on', 'is_anonymous', 'post_type']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        data['poked_ngo'] = NGOOptionSerializer(instance.poked_on_rn.all(), many=True,
                                                context={'request': self.context.get('request')}).data
        if not instance.is_anonymous:
            if instance.people_posted_post_rn.exists():
                data['author'] = instance.people_posted_post_rn.first().full_name
                data['author_id'] = instance.people_posted_post_rn.first().id
            if instance.ngo_posted_post_rn.exists():
                data['author'] = instance.ngo_posted_post_rn.first().full_name
                data['author_id'] = instance.ngo_posted_post_rn.first().id
        if instance.post_type == EPostType.Normal.name:
            data['post_normal'] = NormalPostSerializer(instance.postnormal,
                                                       context={'request': self.context.get('request')}).data
        if instance.post_type == EPostType.Poll.name:
            data['post_poll'] = PollPostSerializer(instance.postpoll,
                                                   context={'request': self.context.get('request')}).data
        if instance.post_type == EPostType.Request.name:
            data['post_request'] = RequestPostSerializer(instance.postrequest,
                                                         context={'request': self.context.get('request')}).data
        return data


class PeopleCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, allow_blank=False, write_only=True, allow_null=False, )
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, allow_blank=False,
                                     required=True,
                                     allow_null=False)
    display_picture = serializers.ImageField(default=None, )
    citizenship_photo = serializers.ImageField(default=None, )

    class Meta:
        model = PeopleUser
        exclude = ['id', 'account', 'posted_post', 'is_verified']
        required = ('date_of_birth', 'gender', 'phone',)

    def create(self, validated_data):
        if validated_data['username'] in User.objects.values_list('username', flat=True):
            raise ParseError()
        user = User.objects.create(username=validated_data['username'],
                                   email=validated_data['email'],
                                   )
        user.set_password(validated_data['password'])
        user.groups.add(Group.objects.get(name='General'))
        user.save()
        if not validated_data['display_picture']:
            validated_data['display_picture'] = settings.DEFAULT_PEOPLE_DP
        return PeopleUser.objects.create(account=user,
                                         full_name=validated_data['full_name'],
                                         date_of_birth=validated_data['date_of_birth'],
                                         gender=validated_data['gender'],
                                         phone=validated_data['phone'],
                                         address=validated_data['address'],
                                         display_picture=validated_data['display_picture'],
                                         citizenship_photo=validated_data['citizenship_photo'],
                                         )


class PeopleRUDSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, write_only=True)
    display_picture = serializers.ImageField(default=None, )
    citizenship_photo = serializers.ImageField(default=None, )
    is_verified = serializers.BooleanField(read_only=True, )

    class Meta:
        model = PeopleUser
        exclude = ['id', 'account', 'posted_post', ]

    def update(self, instance, validated_data):
        user: User = instance.account
        user.email = validated_data.get('email', user.email)
        user.save()
        if not validated_data['display_picture']:
            validated_data['display_picture'] = settings.DEFAULT_PEOPLE_DP
        if instance.is_verified:
            validated_data['citizenship_photo'] = instance.citizenship_photo
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['email'] = instance.account.email
        return data


class NormalPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNormal
        exclude = ('post', 'up_vote', 'down_vote', 'reported_by')


class PollPostCreateSerializer(serializers.ModelSerializer):
    option = serializers.ListSerializer(child=serializers.CharField(),
                                        write_only=True, allow_empty=False, )

    class Meta:
        model = PostPoll
        exclude = ('post', 'reported_by',)

    def create(self, validated_data):
        poll_post = PostPoll.objects.create(ends_on=validated_data['ends_on'], )
        for i in [PollOption.objects.create(option=i) for i in validated_data['option']]:
            poll_post.option.add(i)
        return poll_post

    def validate(self, attrs: OrderedDict):
        if len(attrs.get('option')) < 2:
            raise serializers.ValidationError('Must provide minimum of two poll options for type: poll post.')
        if attrs.get('ends_on') and attrs.get('ends_on') <= datetime.now(tz=attrs.get('ends_on').tzinfo) \
                + timedelta(minutes=50):
            raise serializers.ValidationError('Poll post must end in future.')
        return attrs

    def update(self, instance: PostPoll, validated_data):
        instance.ends_on = validated_data['ends_on']
        option_data = validated_data['option']
        instance_options = instance.option.filter(option__in=option_data)
        to_remove = instance.option.exclude(option__in=option_data)
        for i in to_remove:
            instance.option.remove(i)
        to_add = set(option_data).difference([i.option for i in instance_options])
        for i in [PollOption.objects.create(option=i) for i in to_add]:
            instance.option.add(i)
        return instance.save()


class RequestPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRequest
        exclude = ('post', 'reported_by', 'reacted_by',)

    # YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
    def validate(self, attrs: OrderedDict):
        if attrs.get('target') == 0:
            raise serializers.ValidationError('Target participants cannot be 0.')
        if attrs.get('min') != 0 and (attrs.get('target') < attrs.get('min')):
            raise serializers.ValidationError('Target participants must be greater than or equal to non-zero minimum '
                                              'participants.')
        if attrs.get('max') and attrs.get('max') < attrs.get('target'):
            raise serializers.ValidationError('Max participants must be equal or greater than the target participants.')
        if attrs.get('ends_on') < datetime.now(attrs.get('ends_on').tzinfo) + timedelta(minutes=50):
            raise serializers.ValidationError('Request post must end in future.')
        if attrs.get('request_type') == 'Petition' and attrs.get('max'):
            raise serializers.ValidationError('Petition post is not bounded by maximum participants.')
        return attrs

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class PostCreateSerializer(serializers.ModelSerializer):
    related_to = serializers.MultipleChoiceField(choices=core.models.FIELD_OF_WORK, write_only=True,
                                                 allow_empty=False, )

    class Meta:
        model = Post
        exclude = ('modified_on', 'is_removed', 'post_type')

    def create(self, validated_data):
        return Post.objects.create(related_to=validated_data['related_to'],
                                   post_content=validated_data['post_content'],
                                   is_anonymous=validated_data['is_anonymous'],
                                   )

    def update(self, instance: Post, validated_data):
        _ = super().update(instance, validated_data)
        _.modified_on = timezone.now()
        return _.save()


class PostNormalSerializer(serializers.Serializer):
    post_head = PostCreateSerializer(write_only=True, )
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(),
                                          write_only=True, allow_empty=True,
                                          )
    post_image = serializers.ImageField(default=None, )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Normal)

    def update(self, instance: Post, validated_data):
        poked_to_data = validated_data.pop('poked_to')
        post_image_data = validated_data.pop('post_image')

        check_ngo(poked_to_data)
        update_post(instance, validated_data)

        update_post_poked_ngo(instance, poked_to_data)
        post_normal: PostNormal = instance.postnormal
        post_normal.post_image = post_image_data
        return post_normal.save()


class PostPollSerializer(serializers.Serializer):
    poll_post = PollPostCreateSerializer(write_only=True, )
    post_head = PostCreateSerializer(write_only=True, )
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(),
                                          write_only=True, allow_empty=True,
                                          )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Poll)

    def update(self, instance, validated_data):
        poked_to_data = validated_data.pop('poked_to')
        poll_post_data = validated_data.pop('poll_post')
        serialized_poll_post = PollPostCreateSerializer(data=poll_post_data)

        check_ngo(poked_to_data)
        serialized_poll_post.is_valid(raise_exception=True)
        update_post(instance, validated_data)

        update_post_poked_ngo(instance, poked_to_data)
        return serialized_poll_post.update(instance=instance.postpoll,
                                           validated_data=serialized_poll_post.validated_data)


class PostRequestSerializer(serializers.Serializer):
    request_post = RequestPostCreateSerializer(write_only=True, )
    post_head = PostCreateSerializer(write_only=True)
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(), required=False,
                                          write_only=True, allow_empty=True, )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Request)

    def update(self, instance, validated_data):
        poked_to_data = validated_data.pop('poked_to')
        request_post_data = validated_data.pop('request_post')
        serialized_request_post = RequestPostCreateSerializer(data=request_post_data)

        check_ngo(poked_to_data)
        serialized_request_post.is_valid(raise_exception=True)
        update_post(instance, validated_data)

        update_post_poked_ngo(instance, poked_to_data)
        return serialized_request_post.update(instance=instance.postrequest,
                                              validated_data=serialized_request_post.validated_data)


def check_ngo(poked_to: list[int]):
    invalid_ngo_id = [i for i in poked_to if not User.objects.filter(pk=i).exists()]
    if invalid_ngo_id:
        raise CustomAPIException(p_status_code=404,
                                 p_default_detail=f'NGOs with IDs: {invalid_ngo_id} does not exist.',)


def update_post_poked_ngo(instance: Post, new_poked_to):
    old_poked_to = [i.id for i in instance.poked_on_rn.all()]
    old_set = set(old_poked_to)
    new_set = set(new_poked_to)
    to_remove = old_set.difference(new_set)
    to_add = new_set.difference(old_set)
    for i in to_remove:
        NGOUser.objects.get(id=i).poked_on.remove(instance)
    for i in to_add:
        NGOUser.objects.get(id=i).poked_on.add(instance)


def update_post(instance: Post, validated_data):
    serialized_post = PostCreateSerializer(data=validated_data['post_head'])
    serialized_post.is_valid(raise_exception=True)
    return serialized_post.update(instance=instance, validated_data=serialized_post.validated_data)


def create_post(request: Request, validated_data, post_type: EPostType):
    user: User = request.user
    poked_ngo = set(validated_data['poked_to'])
    serialized_post_head = PostCreateSerializer(data=validated_data['post_head'], )
    try:
        group = user.groups.first().name
        if group not in ['NGO', 'General']:
            raise ValueError('Only NGO and general people can post!')
        if group == 'NGO' and user.ngouser.id in poked_ngo:
            raise ValueError(f'You cannot poke yourself!')
        invalid_ngo_id = [i for i in poked_ngo if not User.objects.filter(pk=i).exists()]
        if invalid_ngo_id:
            raise ValueError(f'NGOs with IDs: {invalid_ngo_id} does not exist.')
        if serialized_post_head.is_valid():
            post: Post = serialized_post_head.save()
            match post_type:
                case EPostType.Normal:
                    post.post_type = post_type.name
                    serialized_post_extension = NormalPostCreateSerializer(
                        data={'post_image': validated_data['post_image']})
                case EPostType.Poll:
                    post.post_type = post_type.name
                    serialized_post_extension = PollPostCreateSerializer(data=validated_data['poll_post'])
                case EPostType.Request:
                    post.post_type = post_type.name
                    serialized_post_extension = RequestPostCreateSerializer(data=validated_data['request_post'])
                case _:
                    raise HttpResponseServerError
            post.save()
            if serialized_post_extension.is_valid():
                post_extension = serialized_post_extension.save()
                post_extension.post = post
                post_extension.save()
                if group == 'General':
                    user.peopleuser.posted_post.add(post)
                if group == 'NGO':
                    user.ngouser.posted_post.add(post)
                for i in poked_ngo:
                    NGOUser.objects.get(id=i).poked_on.add(post)
            else:
                post.delete()
                raise ValueError(serialized_post_extension.errors)
        else:
            raise ValueError(serialized_post_head.errors)
    except ValueError as e:
        return Response({"Fail": e.args}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Success": f"{post_type.name} Post created successfully!",
                         "post_data": PostListSerializer(post, ).data}, status=status.HTTP_201_CREATED)


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeopleUser
        exclude = ['account']
        read_only_fields = ('posted_post',)

    def create(self, validated_data):
        return super().create(validated_data)

    def to_representation(self, instance: PeopleUser):
        data = super().to_representation(instance)
        data['username'] = instance.account.username
        data['email'] = instance.account.email
        data['date_joined'] = instance.account.date_joined
        return data
