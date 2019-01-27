import json
from ast import literal_eval

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from voting_app.models import Poll, Choice
from voting_app.serializers import PollSerializer, ChoiceSerializer


# class PollList(generics.ListCreateAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer


# class PollDetail(generics.RetrieveDestroyAPIView):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def create_choices(self, poll, request):
        dict_data = dict(request.data)
        choices_data = [literal_eval(c) for c in dict_data['choices']]
        choices_serializer = ChoiceSerializer(data=choices_data, many=True)
        if choices_serializer.is_valid():
            # we can also just pass `poll=poll`
            choices_serializer.save(poll_id=poll.id)
        else:
            print(choices_serializer.errors)

    def create(self, request):
        poll_serializer = PollSerializer(data=request.data)
        if poll_serializer.is_valid():
            poll = poll_serializer.save()
            self.create_choices(poll, request)

            return Response(
                poll_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                poll_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

# class Voting(APIView):

#     def post(self, request, pk, choice_pk):
#         voted_by = request.data.get("voted_by")
#         data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
#         choice = Choice.objects.get(pk=choice_pk)
#         choice.
