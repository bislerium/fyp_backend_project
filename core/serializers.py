from rest_framework import serializers
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
    class Meta:
        model = PostNormal
        fields = '__all__'


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
