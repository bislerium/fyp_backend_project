import enum
from collections import OrderedDict
from datetime import datetime, timedelta
from dj_rest_auth.serializers import TokenSerializer, LoginSerializer
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework import serializers, status

import core.models
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
    class Meta:
        model = NGOUser
        fields = ['id', 'address', 'display_picture', 'full_name', 'establishment_date', 'field_of_work']


class NGOSerializer(serializers.ModelSerializer):
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
    up_vote = serializers.HyperlinkedRelatedField(view_name='api-people-detail', many=True, read_only=True)
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = PostNormal
        exclude = ('reported_by',)

    def get_post_image(self, instance):
        request = self.context.get('request')
        print('-----', self, '-----------')
        img = instance.post_image
        if img and hasattr(img, 'url'):
            photo_url = img.url
            print(photo_url)
            return request.build_absolute_uri(photo_url)
        else:
            return None


class PollOptionSerializer(serializers.ModelSerializer):
    reacted_by = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-people-detail'
    )

    class Meta:
        model = PollOption
        fields = '__all__'


class PollPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPoll
        exclude = ('reported_by', 'post',)

    def to_representation(self, instance: PostPoll):
        data = super().to_representation(instance)
        data['option'] = PollOptionSerializer(instance.option, many=True,
                                              context={'request': self.context.get('request')}).data
        return data


class RequestPostSerializer(serializers.ModelSerializer):
    reacted_by = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-people-detail'
    )

    class Meta:
        model = PostRequest
        exclude = ('reported_by',)


class PostListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-post-detail')
    is_ngo_poked = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ['id', 'url', 'related_to', 'post_content', 'is_anonymous', 'is_ngo_poked', 'post_type', 'created_on']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        a = instance.people_posted_post_rn.first()
        if instance.poked_on_rn.count() > 0:
            data['is_ngo_poked'] = True
        if a is None:
            a = instance.ngo_posted_post_rn.first()
            view = 'api-ngo-detail'
        else:
            view = 'api-people-detail'
        data['posted_by'] = self.context.get('request').build_absolute_uri(reverse_lazy(view, kwargs={'pk': a.id}))
        return data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'related_to', 'post_content', 'created_on', 'modified_on', 'is_anonymous', 'post_type']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        if instance.post_type == 'Normal':
            data['post_normal'] = NormalPostSerializer(instance.postnormal,
                                                       context={'request': self.context.get('request')}).data
        if instance.post_type == 'Poll':
            data['post_poll'] = PollPostSerializer(instance.postpoll,
                                                   context={'request': self.context.get('request')}).data
        if instance.post_type == 'Request':
            data['post_request'] = RequestPostSerializer(instance.postrequest,
                                                         context={'request': self.context.get('request')}).data
        return data


class PeopleCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, allow_blank=False, write_only=True, allow_null=False, )
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, allow_blank=False,
                                     required=True,
                                     allow_null=False)

    class Meta:
        model = PeopleUser
        exclude = ['account', 'posted_post', 'is_verified']
        required = ('date_of_birth', 'gender', 'phone',)

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],
                                   email=validated_data['email'],
                                   )
        user.set_password(validated_data['password'])
        user.groups.add(Group.objects.get(name='General'))
        user.save()
        if validated_data['display_picture'] is None:
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


class NormalPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNormal
        exclude = ('post', 'up_vote', 'down_vote', 'reported_by')


def adequate_poll_options(value: list):
    if not value:
        raise serializers.ValidationError('Must have at least two poll options.')


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
            raise serializers.ValidationError('Must provide two poll options for type: poll post.')
        if attrs.get('ends_on') <= datetime.now().date():
            raise serializers.ValidationError('Poll post must end in future.')
        return attrs


class RequestPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRequest
        exclude = ('post', 'reported_by', 'reacted_by',)

    #YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]
    def validate(self, attrs: OrderedDict):
        if attrs.get('target') == 0:
            raise serializers.ValidationError('Target participants cannot be 0.')
        if attrs.get('min') != 0 and (attrs.get('target') < attrs.get('min')):
            raise serializers.ValidationError('Target participants must be greater than or equal to non-zero minimum '
                                              'participants.')
        if attrs.get('max') and attrs.get('max') < attrs.get('target'):
            raise serializers.ValidationError('Max participants must be equal or greater than the target participants.')
        time_zone = attrs.get('ends_on').tzinfo
        if attrs.get('ends_on') < datetime.now(time_zone) + timedelta(hours=1):
            raise serializers.ValidationError('Request post must end in future.')
        if attrs.get('request_type') == 'Petition' and attrs.get('max'):
            raise serializers.ValidationError('Petition post is not bounded by maximum participants.')
        return attrs


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


class PostNormalSerializer(serializers.Serializer):
    normal_post = NormalPostCreateSerializer(write_only=True, )
    post_head = PostCreateSerializer(write_only=True, )
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(),
                                          write_only=True, allow_empty=True,
                                          )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Normal)


class PostPollSerializer(serializers.Serializer):
    poll_post = PollPostCreateSerializer(write_only=True, )
    post_head = PostCreateSerializer(write_only=True, )
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(),
                                          write_only=True, allow_empty=True,
                                          )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Poll)


class PostRequestSerializer(serializers.Serializer):
    request_post = RequestPostCreateSerializer(write_only=True, )
    post_head = PostCreateSerializer(write_only=True)
    poked_to = serializers.ListSerializer(child=serializers.IntegerField(), required=False,
                                          write_only=True, allow_empty=True,
                                          )

    def create(self, validated_data):
        return create_post(self.context['request'], validated_data=validated_data, post_type=EPostType.Request)


def create_post(request: Request, validated_data, post_type: EPostType):
    user: User = request.user
    poked_ngo = set(validated_data['poked_to'])
    serialized_post_head = PostCreateSerializer(data=validated_data['post_head'], )
    try:
        if user.groups.first().name not in ['NGO', 'General']:
            raise ValueError('Only NGO and general people can post!')
        if user.ngouser.id in poked_ngo:
            raise ValueError(f'You cannot poke yourself!')
        invalid_ngo_id = [i for i in poked_ngo if not User.objects.filter(pk=i).exists()]
        if invalid_ngo_id:
            raise ValueError(f'NGOs with IDs: {invalid_ngo_id} does not exist.')
        if serialized_post_head.is_valid():
            post = serialized_post_head.save()
            match post_type:
                case EPostType.Normal:
                    post.post_type = post_type.name
                    serialized_post_extension = NormalPostCreateSerializer(data=validated_data['normal_post'])
                case EPostType.Poll:
                    post.post_type = post_type.name
                    serialized_post_extension = PollPostCreateSerializer(data=validated_data['poll_post'])
                case EPostType.Request:
                    post.post_type = post_type.name
                    serialized_post_extension = RequestPostCreateSerializer(data=validated_data['request_post'])
            post.save()
            if serialized_post_extension.is_valid():
                post_extension = serialized_post_extension.save()
                post_extension.post = post
                post_extension.save()
                if user.groups.first().name == 'People':
                    user.peopleuser.posted_post.add(post)
                if user.groups.first().name == 'NGO':
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
        return Response({"Success": f"{post_type.name} Post created successfully!"}, status=status.HTTP_201_CREATED)


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
