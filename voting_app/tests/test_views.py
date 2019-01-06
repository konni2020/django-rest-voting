import json

from django.forms.models import model_to_dict
from django.shortcuts import reverse
from django.test import TestCase

from voting_app.models import Poll, Choice

TEST_POLL = {
    'name': 'john',
    'description': 'What fruit below do you like most?',
}

TEST_CHOICES = [
    {
        'text': 'apple',
        'total': 3,
    },
    {
        'text': 'pear',
        'total': 5,
    },
    {
        'text': 'watermelon',
        'total': 10,
    },
]

def create_a_poll():
    poll = Poll()
    for key, value in TEST_POLL.items():   
        setattr(poll, key, value)
    poll.save()

    return poll

def create_a_choice(poll, instance=None, data=None, text=None, total=0):
    if instance:
        text = instance.text
        total = instance.total
    elif data:
        text = data['text']
        total = data['total']  
    elif not text:
        text = TEST_CHOICES[0]['text']

    choice = Choice.objects.create(poll=poll, text=text, total=total)

    return choice

def create_a_poll_with_choices():
    poll = create_a_poll()

    for choice_data in TEST_CHOICES:
        create_a_choice(poll, data=choice_data)

    return poll


class PollAPITest(TestCase):

    def _get_choices_data(self, poll):
        # get choices json data from a poll
        return list(poll.choice_set.all().values('text', 'total'))

    def _get_poll_json_data(self, poll):
        fields = ['id', 'name', 'description', 'format_modified']
        data = model_to_dict(poll, fields=fields)
        data['choices'] = self._get_choices_data(poll)
        return data

    def _get_polls_json_data(self, polls):
        return [self._get_poll_json_data(poll) for poll in polls]

    def test_post_list_view(self):
        create_a_poll_with_choices()
        data = {
            'results': self._get_polls_json_data(Poll.objects.all())
        }

        url = reverse('polls:poll_list')
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_poll_detail_view(self):
        poll = create_a_poll_with_choices()
        data = self._get_poll_json_data(poll)

        url = reverse('polls:poll_detail', kwargs={'pk': poll.id})
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)