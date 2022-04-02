import random

from dj_rest_auth.views import LoginView as ILoginView
from rest_framework import parsers
from rest_framework.generics import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.utils import json
from rest_framework.views import APIView

import core.models
from .serializers import *


class EReactionType(enum.Enum):
    Upvote = 0,
    Downvote = 1,


class CustomLoginView(ILoginView):
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


class PaginationClass(PageNumberPagination):
    page_size = 100


class PeopleAdd(CreateAPIView):
    queryset = PeopleUser.objects.all()
    serializer_class = PeopleCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'Success': 'User is Registered.'}, status=status.HTTP_201_CREATED, )


class PeopleDelete(DestroyAPIView):
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        user: User = self.request.user
        self.perform_destroy(user)
        Token.objects.get(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance: User):
        instance.is_active = False
        instance.save()


class CustomMultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )
        data = {}
        for key, value in result.data.items():
            if '{' in value or "[" in value:
                try:
                    data[key] = json.loads(value)
                except ValueError:
                    print('raised')
            else:
                data[key] = value
        file = {}
        for key, value in result.files.items():
            file[key] = value

        return parsers.DataAndFiles(data, file)


class NormalPostAdd(APIView):
    permission_classes = [AllowAny]
    parser_classes = (CustomMultipartJsonParser,)
    serializer_class = PostNormalSerializer

    def post(self, request):
        return post_a_post(request, post_type=EPostType.Normal)


class PollPostAdd(APIView):
    serializer_class = PostPollSerializer

    def post(self, request):
        return post_a_post(request, post_type=EPostType.Poll)


class RequestPostAdd(APIView):
    serializer_class = PostRequestSerializer

    def post(self, request):
        return post_a_post(request, post_type=EPostType.Request)


def post_a_post(request, post_type: EPostType):
    if not request.user.groups.exists() or request.user.groups.first().name not in ['General', 'NGO']:
        return Response({'Fail': f'Only general people and NGO can post.'},
                        status=status.HTTP_403_FORBIDDEN)
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
        return Response({'Fail': post_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({'Fail': f'Only general people can {reaction_type.name.lower()} the normal post!'},
                        status=status.HTTP_403_FORBIDDEN)
    filtered_post = Post.objects.filter(id=post_id)
    if not filtered_post.exists():
        return Response({'Fail': 'Normal post with given post id not found!'}, status=status.HTTP_404_NOT_FOUND)
    post = filtered_post.first()
    if post.post_type != 'Normal':
        return Response({'Fail': f'Can only {reaction_type.name.lower()} normal post!'},
                        status=status.HTTP_400_BAD_REQUEST)
    match reaction_type:
        case EReactionType.Upvote:
            reaction_queryset = post.postnormal.up_vote.all()
        case EReactionType.Downvote:
            reaction_queryset = post.postnormal.down_vote.all()
    if user.peopleuser in reaction_queryset:
        match reaction_type:
            case EReactionType.Upvote:
                post.postnormal.up_vote.remove(user.peopleuser)
            case EReactionType.Downvote:
                post.postnormal.down_vote.remove(user.peopleuser)
        return Response({'Undone': f'Normal post {reaction_type.name.lower()} undone.'}, status=status.HTTP_200_OK)
    else:
        match reaction_type:
            case EReactionType.Upvote:
                post.postnormal.up_vote.add(user.peopleuser)
                post.postnormal.down_vote.remove(user.peopleuser)
            case EReactionType.Downvote:
                post.postnormal.down_vote.add(user.peopleuser)
                post.postnormal.up_vote.remove(user.peopleuser)
        return Response({'Done': f'Normal post {reaction_type.name.lower()} done.'}, status=status.HTTP_200_OK)


class PollPostPollView(APIView):

    def post(self, request, post_id, option_id):
        user: User = request.user
        a = validate_request_post_id(user, post_id)
        if isinstance(a, Response):
            return a
        else:
            post = a
        if post.post_type != 'Poll':
            return Response({'Fail': f'Can only poll in poll post!'}, status=status.HTTP_400_BAD_REQUEST)
        poll_option = PollOption.objects.filter(id=option_id)
        if not poll_option.exists() or not post.postpoll.option.filter(id=option_id).exists():
            return Response({'Fail': 'Poll option with given option id not found!'}, status=status.HTTP_404_NOT_FOUND)
        if post.postpoll.ends_on and datetime.now(tz=post.postpoll.ends_on.tzinfo) > post.postpoll.ends_on:
            return Response({'Success': f'Polling date expired.'}, status=status.HTTP_403_FORBIDDEN)
        poll_reactions = poll_option.first().reacted_by
        if user.peopleuser in poll_reactions.all():
            return Response({'Success': f'Already polled {poll_option.first().option}.'}, status=status.HTTP_200_OK)
        poll_reactions.add(user.peopleuser)
        return Response({'Success': f'Polled {poll_option.first().option}.'}, status=status.HTTP_200_OK)


class RequestPostParticipateView(APIView):

    def post(self, request, post_id):
        user: User = request.user
        _ = validate_request_post_id(user, post_id)
        if isinstance(_, Response):
            return _
        else:
            post = _
        if post.post_type != 'Request':
            return Response({'Fail': f'Can only participate in request post!'}, status=status.HTTP_400_BAD_REQUEST)
        request_participants = post.postrequest.reacted_by
        if user.peopleuser in request_participants.all():
            return Response({'Success': f'Already participated.'}, status=status.HTTP_208_ALREADY_REPORTED)
        if datetime.now(tz=post.postrequest.ends_on.tzinfo) > post.postrequest.ends_on:
            return Response({'Success': f'Post request participation date expired.'}, status=status.HTTP_403_FORBIDDEN)
        request_participants.add(user.peopleuser)
        return Response({'Success': f'Participated'}, status=status.HTTP_200_OK)


class PostReportView(APIView):

    def post(self, request, post_id):
        user: User = request.user
        a = validate_request_post_id(user, post_id)
        if isinstance(a, Response):
            return a
        else:
            post = a
        match post.post_type:
            case 'Normal':
                post.postnormal.reported_by.add(user.peopleuser)
            case 'Poll':
                post.postpoll.reported_by.add(user.peopleuser)
            case 'Request':
                post.postrequest.reported_by.add(user.peopleuser)
        if not Report.objects.filter(post=post).exists():
            Report.objects.create(post=post)
        return Response({'Success': f'Post has been reported.'}, status=status.HTTP_200_OK)


def validate_request_post_id(user, post_id):
    if not user.groups.exists() or user.groups.first().name != 'General':
        return Response({'Fail': f'Only general people can perform this action!'},
                        status=status.HTTP_403_FORBIDDEN)
    filtered_post = Post.objects.filter(id=post_id)
    if not filtered_post.exists():
        return Response({'Fail': 'Post with given post id not found!'}, status=status.HTTP_404_NOT_FOUND)
    return filtered_post.first()


class TokenVerification(APIView):

    def get(self, request: Request):
        return Response({'Success': 'Token verified.'}, status=status.HTTP_200_OK)


class PostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        _ = super().get_queryset()
        __ = _.filter(people_posted_post_rn__account__is_active=True) | _.filter(ngo_posted_post_rn__account__is_active=True)
        queryset = __.filter(is_removed=False)
        return sorted(queryset, key=lambda x: random.random())


class UserPostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = PaginationClass

    def get_queryset(self):
        _ = super().get_queryset()
        match self.kwargs['user_type']:
            case 'people':
                people: PeopleUser = get_object_or_404(PeopleUser, pk=self.kwargs['user_id'])
                queryset = _.filter(people_posted_post_rn=people)
            case 'ngo':
                ngo: NGOUser = get_object_or_404(NGOUser, pk=self.kwargs['user_id'])
                queryset = _.filter(ngo_posted_post_rn=ngo)
            case _: queryset = _.none()
        return queryset.filter(is_removed=False)


class RelatedOptionList(APIView):

    def get(self, request):
        return Response({'options': [v[0] for v in core.models.FIELD_OF_WORK]}, status=status.HTTP_200_OK, )


class NGOOptionList(ListAPIView):
    queryset = NGOUser.objects.all()
    serializer_class = NGOOptionSerializer


class PostDelete(DestroyAPIView):
    queryset = Post.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance: Post = self.get_object()
        user: User = self.request.user
        if instance.people_posted_post_rn.exists():
            user_who_posted: PeopleUser = instance.people_posted_post_rn.first().account
        if instance.ngo_posted_post_rn.exists():
            user_who_posted: NGOUser = instance.ngo_posted_post_rn.first().account
        if user != user_who_posted:
            return Response({'Fail': 'Post does not belong to the user who requested.'},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance: Post):
        instance.is_removed = True
        instance.save()

