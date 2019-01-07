from rest_framework import serializers

from voting_app.models import Poll, Choice




class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('text', 'total',)


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(source='choice_set', many=True, required=False)

    class Meta:
        model = Poll
        fields = ('id', 'name', 'description', 'format_modified', 'choices')