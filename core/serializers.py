from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from .models import *


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class NGOListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-ngo-detail')

    class Meta:
        model = NGOUser
        fields = ['url', 'address', 'display_picture', 'full_name', 'establishment_date', 'field_of_work', 'verified']


class NGOSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOUser
        fields = ['id', 'account', 'phone', 'address', 'display_picture', 'full_name', 'establishment_date',
                  'field_of_work', 'epay_account', 'bank', 'swc_affl_cert', 'pan_cert', 'verified']


class NormalPostSerializer(serializers.ModelSerializer):
    # up_vote = serializers.HyperlinkedRelatedField(view_name='api-people-detail', many=True, read_only=True)
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = PostNormal
        fields = '__all__'

    def get_post_image(self, instance):
        request = self.context.get('request')
        print('-----',self,'-----------')
        img = instance.post_image
        if img and hasattr(img, 'url'):
            photo_url = img.url
            print(photo_url)
            return request.build_absolute_uri(photo_url)
        else:
            return None


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = '__all__'


class PollPostSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = PostPoll
        fields = ['id', 'options', 'ends_on', 'reported_by']

    # noinspection PyMethodMayBeStatic
    def get_options(self, instance: PostPoll):
        options_ = instance.option.all()
        return PollOptionSerializer(options_, many=True).data


class RequestPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRequest
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-post-detail')
    is_ngo_poked = serializers.BooleanField(default=False)

    class Meta:
        model = Post
        fields = ['url', 'related_to', 'text_body', 'anonymous', 'is_ngo_poked', 'post_type', 'created_on']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        a = instance.people_posted_post_rn.first()
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
        fields = ['id', 'related_to', 'text_body', 'created_on', 'modified_on', 'anonymous', 'post_type']

    def to_representation(self, instance: Post):
        data = super().to_representation(instance)
        if instance.post_type == 'Normal':
            data['post_normal'] = NormalPostSerializer(instance.postnormal).data
        if instance.post_type == 'Poll':
            data['post_poll'] = PollPostSerializer(instance.postpoll).data
        if instance.post_type == 'Request':
            data['post_request'] = RequestPostSerializer(instance.postrequest).data
        return data


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeopleUser
        fields = '__all__'

    def to_representation(self, instance: PeopleUser):
        data = super().to_representation(instance)
        data['email'] = instance.account.email
        data['date_joined'] = instance.account.date_joined
        return data
