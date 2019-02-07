from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from voting_app.models import Poll, Choice
from voting_app.serializers import PollSerializer, ChoiceSerializer
from voting_app.helper import OnlyOwnerCanUpdateOrDelete


# class PollList(generics.ListCreateAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer


# class PollDetail(generics.RetrieveDestroyAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = (
        OnlyOwnerCanUpdateOrDelete,
        IsAuthenticatedOrReadOnly
    )

    def create_choices(self, poll, request):
        choices_serializer = ChoiceSerializer(
            data=request.data['choices'],
            many=True,
        )

        if choices_serializer.is_valid():
            # we can also just pass `poll=poll`
            choices_serializer.save(poll_id=poll.id)
        else:
            print(choices_serializer.errors, 'choice serializer error')

    def perform_create(self, serializer):
        poll = serializer.save(author=self.request.user)
        self.create_choices(poll, self.request)


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class CreatePoll(generics.CreateAPIView):
    serializer_class = PollSerializer


class ChoiceList(generics.ListCreateAPIView):
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        queryset = Choice.objects.filter(poll__id=self.kwargs['pk'])
        return queryset

    def post(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        data = self.request.data

        serializer = ChoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(poll=poll)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

    def post(self, request, pk, choice_pk):
        choice = Choice.objects.get(pk=choice_pk)
        choice.total += 1
        choice.save()

        serializer = ChoiceSerializer(choice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
