from rest_framework.generics import *
from rest_framework.viewsets import *

from .serializers import *


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


class PostDetail(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
