import django
import rest_framework
from dj_rest_auth.views import LoginView as LV
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.generics import *
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class CustomLoginView(LV):
    serializer_class = CustomLoginSerializer


class NGOList(ListAPIView):
    queryset = NGOUser.objects.all()
    serializer_class = NGOListSerializer


class NGODetail(RetrieveAPIView):
    queryset = NGOUser.objects.all()
    serializer_class = NGOSerializer


class BankDetail(RetrieveAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer


class PeopleList(ListAPIView):
    queryset = PeopleUser.objects.all()
    serializer_class = PeopleSerializer


class PeopleDetail(RetrieveAPIView):
    queryset = PeopleUser.objects.all()
    serializer_class = PeopleSerializer


class PostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer

    def get_queryset(self):
        return super().get_queryset().filter(is_removed=False)


class PeopleAdd(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = PeopleUser.objects.all()
    serializer_class = PeopleCreateSerializer

    def post(self, request, *args, **kwargs):
        response: Response = super().post(request, *args, **kwargs)
        print(response.headers.get()['status_code'])
        print(response)


class NormalPostAdd(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostNormalSerializer

    def post(self, request):
        return post_a_post(self, request, post_type=EPostType.Normal)


class PollPostAdd(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostPollSerializer

    def post(self, request):
        return post_a_post(self, request, post_type=EPostType.Poll)


class RequestPostAdd(APIView):
    permission_classes = [AllowAny]
    serializer_class = PostRequestSerializer

    def post(self, request):
        return post_a_post(self, request, post_type=EPostType.Request)


def post_a_post(self, request, post_type: EPostType):
    match post_type:
        case EPostType.Normal:
            post_serializer = PostNormalSerializer(data=request.data, context={'request': request})
        case EPostType.Poll:
            post_serializer = PostPollSerializer(data=request.data, context={'request': request})
        case EPostType.Request:
            post_serializer = PostRequestSerializer(data=request.data, context={'request': request})
    if post_serializer.is_valid():
        return post_serializer.save()
    else:
        return Response({"Fail": post_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
