import random
from collections import deque

from dj_rest_auth.views import LoginView as RestLoginView
from django.core.exceptions import PermissionDenied
from rest_framework import parsers
from rest_framework.generics import *
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.utils import json
from rest_framework.views import APIView

import core.models
from .enums import EReactionType
from .serializers import *


class CustomAPILoginView(RestLoginView):
    serializer_class = CustomLoginSerializer


class NGOList(ListAPIView):
    serializer_class = NGOListSerializer

    def get_queryset(self):
        return get_ngo_querylist(self)


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


class PeopleAdd(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PeopleCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            _ = serializer.save()
            if not _:
                return Response({'Success': serializer.errors}, status=status.HTTP_400_BAD_REQUEST, )
            return Response({'Success': 'User is Registered.'}, status=status.HTTP_201_CREATED, )


class PeopleRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = PeopleRUDSerializer

    def get_obj(self):
        user: User = self.request.user
        if not user.groups.exists() or user.groups.first().name != 'General':
            raise PermissionDenied
        return user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_obj().peopleuser)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_obj().peopleuser
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response({'Success': 'Your profile has been updated!'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_obj()
        Token.objects.get(user=instance).delete()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class PostRetrieveUpdateDelete(APIView):
    parser_classes = (CustomMultipartJsonParser, JSONParser)

    def get_obj(self):
        user: User = self.request.user
        if not user.groups.exists() or user.groups.first().name not in ['General', 'NGO']:
            raise PermissionDenied
        post: Post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if not user.is_active or post.is_removed:
            raise CustomAPIException(p_status_code=404, p_default_detail='Post does not exist.')
        if post.people_posted_post_rn.exists():
            _: PeopleUser = post.people_posted_post_rn.first()
        if post.ngo_posted_post_rn.exists():
            _: NGOUser = post.ngo_posted_post_rn.first()
        if user != _.account:
            raise PermissionDenied
        return post

    def get(self, request, *args, **kwargs):
        serializer = PostRetrieveToUpdateSerializer(self.get_obj(), context={'request': request})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        post: Post = self.get_obj()
        match post.post_type:
            case 'Normal':
                serialized_post = PostNormalSerializer(data=request.data)
            case 'Poll':
                serialized_post = PostPollSerializer(data=request.data)
            case 'Request':
                serialized_post = PostRequestSerializer(data=request.data)
            case _:
                raise HttpResponseServerError
        serialized_post.is_valid(raise_exception=True)
        serialized_post.update(instance=post, validated_data=serialized_post.validated_data)
        return Response({'Success': 'Your post has been updated!'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance: Post = self.get_obj()
        instance.is_removed = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostDetail(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def retrieve(self, request, *args, **kwargs):
        instance: Post = self.get_object()
        if not validate_post(instance):
            return Response({'Fail': 'Post does not exist!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


def validate_post(instance: Post):
    if instance.ngo_posted_post_rn.exists():
        user: PeopleUser = instance.ngo_posted_post_rn.first()
    if instance.people_posted_post_rn.exists():
        user: NGOUser = instance.people_posted_post_rn.first()
    if not user.account.is_active or instance.is_removed:
        return False
    return True


class ToggleUpvoteView(APIView):

    def post(self, request, post_id):
        return react_post(request.user, post_id, EReactionType.Upvote)


class ToggleDownvoteView(APIView):

    def post(self, request, post_id):
        return react_post(request.user, post_id, EReactionType.Downvote)


def get_id_from_post(post):
    if post.ngo_posted_post_rn.exists():
        return post.ngo_posted_post_rn.first().account.id
    if post.people_posted_post_rn.exists():
        return post.people_posted_post_rn.first().account.id


def react_post(user, post_id, reaction_type: EReactionType):
    if user.groups.first().name != 'General':
        return Response({'Fail': f'Only general people can {reaction_type.name.lower()} the normal post!'},
                        status=status.HTTP_403_FORBIDDEN)
    filtered_post = Post.objects.filter(id=post_id)
    if not filtered_post.exists():
        return Response({'Fail': 'Normal post with given post id not found!'}, status=status.HTTP_404_NOT_FOUND)
    post = filtered_post.first()
    if not validate_post(post):
        return Response({'Fail': 'Can\'t react to a non-existing normal post!'}, status=status.HTTP_404_NOT_FOUND)
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
        who_posted = get_id_from_post(post)
        if user.id != who_posted:
            send_notification(title=f'Normal Post',
                              body=f'{user.peopleuser.full_name.title()} has reacted in your post.',
                              notification_for=who_posted,
                              channel=ENotificationChannel['reaction'],
                              post_type=EPostType['Normal'], post_id=post_id)

        return Response({'Done': f'Normal post {reaction_type.name.lower()} done.'}, status=status.HTTP_200_OK)


class PollPostPollView(APIView):

    def post(self, request, post_id, option_id):
        user: User = request.user
        a = validate_request_post_id(user, post_id)
        if isinstance(a, Response):
            return a
        else:
            post = a
        if not validate_post(post):
            return Response({'Fail': 'Can\'t poll to a non-existing poll-post!'}, status=status.HTTP_404_NOT_FOUND)
        if post.post_type != 'Poll':
            return Response({'Fail': f'Can only poll in poll post!'}, status=status.HTTP_400_BAD_REQUEST)
        poll_option = PollOption.objects.filter(id=option_id)
        if not poll_option.exists() or not post.postpoll.option.filter(id=option_id).exists():
            return Response({'Fail': 'Poll option with given option id not found!'}, status=status.HTTP_404_NOT_FOUND)
        if post.postpoll.ends_on and timezone.now() > post.postpoll.ends_on:
            return Response({'Fail': f'Polling date expired.'}, status=status.HTTP_403_FORBIDDEN)
        poll_reactions = poll_option.first().reacted_by
        if user.peopleuser in poll_reactions.all():
            return Response({'Fail': f'Already polled {poll_option.first().option}.'}, status=status.HTTP_200_OK)
        poll_reactions.add(user.peopleuser)

        who_posted = get_id_from_post(post)
        if user.id != who_posted:
            send_notification(title=f'Poll Post',
                              body=f'{user.peopleuser.full_name.title()} has polled an option in your post.',
                              notification_for=who_posted,
                              channel=ENotificationChannel['poll'],
                              post_type=EPostType['Poll'], post_id=post_id)

        return Response({'Success': f'Polled {poll_option.first().option}.'}, status=status.HTTP_200_OK)


class RequestPostParticipateView(APIView):

    def post(self, request, post_id):
        user: User = request.user
        _ = validate_request_post_id(user, post_id)
        if isinstance(_, Response):
            return _
        else:
            post = _
        if not validate_post(post):
            return Response({'Fail': 'Can\'t participate to a non-existing request-post!'},
                            status=status.HTTP_404_NOT_FOUND)
        if post.post_type != 'Request':
            return Response({'Fail': f'Can only participate in request post!'}, status=status.HTTP_400_BAD_REQUEST)
        request_participants = post.postrequest.reacted_by
        if user.peopleuser in request_participants.all():
            return Response({'Fail': f'Already participated.'}, status=status.HTTP_208_ALREADY_REPORTED)
        if timezone.now() > post.postrequest.ends_on:
            return Response({'Fail': f'Post request participation date expired.'}, status=status.HTTP_403_FORBIDDEN)
        request_participants.add(user.peopleuser)

        match post.postrequest.request_type:
            case 'Petition':
                phrase = 'signed'
            case 'Join':
                phrase = 'participated'

        who_posted = get_id_from_post(post)
        if user.id != who_posted:
            send_notification(title=f'{post.postrequest.request_type} Request Post',
                              body=f'{user.peopleuser.full_name.title()} has {phrase} in your post.',
                              notification_for=who_posted,
                              channel=ENotificationChannel[post.postrequest.request_type.lower()],
                              post_type=EPostType[post.post_type], post_id=post_id)

        return Response({'Success': f'Participated'}, status=status.HTTP_200_OK)


staffs_deque: deque = []
try:
    staffs_deque = deque(Staff.objects.all())
    print(staffs_deque)
    print(type(staffs_deque))
except:
    print('----------MIGRATION NEEDED----------')


def get_staff() -> Staff:
    _: Staff = staffs_deque.popleft()
    staffs_deque.append(_)
    print('Reported to ->', _)
    return _


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
            _ = Report.objects.create(post=post)
            get_staff().report_review.add(_)
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
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        _ = super().get_queryset()
        __ = _.filter(is_removed=False)
        ___ = __.filter(people_posted_post_rn__account__is_active=True) | __.filter(
            ngo_posted_post_rn__account__is_active=True)
        queryset = ___.order_by('-created_on')
        return queryset

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        random.shuffle(data)
        return self.paginator.get_paginated_response(data)


class UserPostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        _ = super().get_queryset()
        match self.kwargs['user_type']:
            case 'people':
                people: PeopleUser = get_object_or_404(PeopleUser, pk=self.kwargs['user_id'])
                queryset = _.filter(people_posted_post_rn=people)
            case 'ngo':
                ngo: NGOUser = get_object_or_404(NGOUser, pk=self.kwargs['user_id'])
                queryset = _.filter(ngo_posted_post_rn=ngo)
            case _:
                queryset = _.none()
        return queryset.filter(is_removed=False).order_by('-created_on')


class RelatedOptionList(APIView):

    def get(self, request):
        return Response({'options': [v[0] for v in core.models.FIELD_OF_WORK]}, status=status.HTTP_200_OK, )


class NGOOptionList(ListAPIView):
    serializer_class = NGOOptionSerializer

    def get_queryset(self):
        return get_ngo_querylist(self)


def get_ngo_querylist(self):
    _ = NGOUser.objects.all()
    user: User = self.request.user
    if user.groups.first().name == 'NGO':
        _ = _.exclude(pk=user.ngouser.id)
    return _
