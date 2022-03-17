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


class EReactionType(enum.Enum):
    Upvote = 0,
    Downvote = 1,


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


class ToggleUpvoteView(APIView):

    def post(self, request, post_id):
        return react_post(request.user, post_id, EReactionType.Upvote)


class ToggleDownvoteView(APIView):

    def post(self, request, post_id):
        return react_post(request.user, post_id, EReactionType.Downvote)


def react_post(user, post_id, reaction_type: EReactionType):
    if user.groups.first().name != 'General':
        return Response({"Fail": f'Only general people can {reaction_type.name.lower()} the normal post!'},
                        status=status.HTTP_403_FORBIDDEN)
    filtered_post = Post.objects.filter(id=post_id)
    if not filtered_post.exists():
        return Response({"Fail": 'Normal post with given post id not found!'}, status=status.HTTP_404_NOT_FOUND)
    post = filtered_post.first()
    if post.post_type != 'Normal':
        return Response({"Fail": f'Can only {reaction_type.name.lower()} normal post!'},
                        status=status.HTTP_400_BAD_REQUEST)
    match reaction_type:
        case EReactionType.Upvote:
            reaction_queryset = post.postnormal.up_vote.all()
        case EReactionType.Downvote:
            reaction_queryset = post.postnormal.down_vote.all()
    if user.peopleuser in reaction_queryset:
        match reaction_type:
            case EReactionType.Upvote: post.postnormal.up_vote.remove(user.peopleuser)
            case EReactionType.Downvote: post.postnormal.down_vote.remove(user.peopleuser)
        return Response({"Undone": f'Normal post {reaction_type.name.lower()} undone.'}, status=status.HTTP_200_OK)
    else:
        match reaction_type:
            case EReactionType.Upvote:
                post.postnormal.up_vote.add(user.peopleuser)
                post.postnormal.down_vote.remove(user.peopleuser)
            case EReactionType.Downvote:
                post.postnormal.down_vote.add(user.peopleuser)
                post.postnormal.up_vote.remove(user.peopleuser)
        return Response({"Done": f'Normal post {reaction_type.name.lower()} done.'}, status=status.HTTP_200_OK)


class PostReportView(APIView):
    pass


class RequestPostParticipateView(APIView):
    pass