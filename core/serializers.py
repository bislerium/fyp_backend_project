from abc import ABC, ABCMeta

from dj_rest_auth.serializers import TokenSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse_lazy
from rest_framework import serializers

from .models import *


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


class PeopleSerializer(serializers.ModelSerializer):

    posted_post = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-post-detail'
    )

    username = serializers.CharField(required=False, allow_blank=False, allow_null=False,)
    email = serializers.EmailField(required=False, allow_blank=False, allow_null=False,)
    password = serializers.CharField(style={'input_type': 'password'}, allow_null=False,)

    class Meta:
        model = PeopleUser
        exclude = ['account']

    def to_representation(self, instance: PeopleUser):
        data = super().to_representation(instance)
        data['username'] = instance.account.username
        data['email'] = instance.account.email
        data['date_joined'] = instance.account.date_joined
        return data
