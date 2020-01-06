from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, viewsets

from django.shortcuts import get_object_or_404

from .models import Poll, Choice, Vote
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer

# Access Controll
from django.contrib.auth import authenticate
from rest_framework.exceptions import PermissionDenied

from pprint import pprint

class LoginView(APIView):
    # auth ??
    permission_classes = ()
    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserCreate(generics.CreateAPIView):
    # Note the authentication_classes = () and permission_classes = () to exempt UserCreate from global authentication scheme.
    # FYI :
    # While authentication tells us which user is logged in (or not)
    # it’s our responsibility to check if the current user
    # (a valid logged in user or a guest, not logged in visitor) has access to the resource.
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

# DRF chapter 6 - end
# We have seen 4 ways to build API views until now • Pure Django views
# • APIView subclasses
# • generics.* subclasses
# • viewsets.ModelViewSet
# So which one should you use when? My rule of thumb is,
# • Use viewsets.ModelViewSet when you are going to allow all or most of CRUD operations on a model. • Use generics.* when you only want to allow some operations on a model
# • Use APIView when you want to completely customize the behaviour.

# The /polls/ and /polls/<pk>/ urls require two view classes, with the same serializer and base queryset.
# We can group them into a viewset, and connect them to the urls using a router.
class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    # Overwrite : Authenticated users can delete only polls they have created.
    def destroy(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == poll.created_by:
            raise PermissionDenied("You can not delete this poll.")
        return super().destroy(request, *args, **kwargs)
    # FYI The actions provided by the ModelViewSet class are .list(), .retrieve(), .create(), .update(), .partial_update(), and .destroy().
    def create(self, request):
        # Manually add the current user as a created_by
        # =D =D =D
        postData = dict(question=request.data['question'], created_by=request.user.pk)
        # pprint(postData)
        # import pdb; pdb.set_trace()
        # How to unpack request.data using asterisks ? ** ??
        # question => "Not a valid string."
        # {'created_by': 2, 'question': ['lol ?']}
        serializer = PollSerializer(data=postData)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # FYI
# viewsets.ModelViewSet
#     is a combination of
#     mixins.CreateModelMixin
#     + mixins.RetrieveModelMixin
#     + mixins.UpdateModelMixin
#     + mixins.DestroyModelMixin
#     + mixins.ListModelMixin
#     + viewsets.GenericViewSet

# Options available
# class PollList(generics.ListCreateAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer

# # Options available
# class PollDetail(generics.RetrieveDestroyAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer

# Was generics.ListCreateAPIView
class ChoiceList(generics.ListCreateAPIView):
    # Get pk from kwargs (instead of queryset = Choice.objects.all())
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])
        return queryset
    serializer_class = ChoiceSerializer
    # Overwrite : Authenticated users can create choices only for polls they have created.
    def post(self, request, *args, **kwargs):
        # In the URL the pk is a poll.pk ;)
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == poll.created_by:
            raise PermissionDenied("You can not create choice for this poll.")
        return super().post(request, *args, **kwargs)


# Was generics.CreateAPIView
# We subclass this from APIView, rather than a generic view, because we competely customize the behaviour.
class CreateVote(APIView):
    serializer_class = VoteSerializer
    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        # must have voted_by in post data !
        # choice_pk and pk come from URL
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /choices
# class ChoiceList(generics.ListCreateAPIView):
#     queryset = Choice.objects.all()
#     serializer_class = ChoiceSerializer

# /vote
# class CreateVote(generics.CreateAPIView):
#     serializer_class = VoteSerializer

# No options available
# class PollList(APIView):
#     def get(self, request):
#         polls = Poll.objects.all()[:20]
#         data = PollSerializer(polls, many=True).data
#         return Response(data)

# class PollDetail(APIView):
#     def get(self, request, pk):
#         poll = get_object_or_404(Poll, pk=pk)
#         data = PollSerializer(poll).data
#         return Response(data)