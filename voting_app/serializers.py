from rest_framework import serializers

from voting_app.models import Poll, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('text', 'total',)


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(
        source='choice_set', many=True,
        required=False, read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ('id', 'author', 'description', 'format_modified', 'choices')

    def get_author(self, obj):
        return obj.author.username
