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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# class Voting(APIView):

#     def post(self, request, pk, choice_pk):
#         voted_by = request.data.get("voted_by")
#         data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
#         choice = Choice.objects.get(pk=choice_pk)
#         choice.
        