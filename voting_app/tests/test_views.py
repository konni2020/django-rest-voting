import json

from rest_framework.test import APIRequestFactory
from django.forms.models import model_to_dict
from django.shortcuts import reverse
from django.test import TestCase

from voting_app.models import Poll, Choice

TEST_POLL = {
    'name': 'john',
    'description': 'What fruit below do you like most?',
    'kk': 3,
    'choices': [
        {'text': 'apple'},
        {'text': 'orange'},
    ],
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


def create_a_choice(poll, instance=None, data=None):
    if instance:
        text = instance.text
        total = instance.total
    elif data:
        text = data['text']
        total = data['total']  
    else:
        text = TEST_CHOICES[0]['text']
        total = 0

    choice = Choice.objects.create(poll=poll, text=text, total=total)

    return choice


def create_a_poll_with_choices():
    poll = create_a_poll()

    for choice_data in TEST_CHOICES:
        create_a_choice(poll, data=choice_data)

    return poll


def get_choices_data(poll):
    # get choices json data from a poll
    return list(poll.choice_set.all().values('text', 'total'))


def get_poll_json_data(poll):
    fields = ['id', 'name', 'description', 'format_modified']
    data = model_to_dict(poll, fields=fields)
    data['choices'] = get_choices_data(poll)
    return data


def get_polls_json_data(polls):
    return [get_poll_json_data(poll) for poll in polls]


class PollAPITest(TestCase):

    def test_post_list_view(self):
        create_a_poll_with_choices()
        data = get_polls_json_data(Poll.objects.all())

        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_poll_detail_view(self):
        poll = create_a_poll_with_choices()
        data = get_poll_json_data(poll)

        url = reverse('polls:poll-detail', kwargs={'pk': poll.id})
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_create_poll_via_poll_viewset(self):
        url = reverse('polls:poll-list')
        response = self.client.post(url, data=TEST_POLL)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Poll.objects.count(), 1)

    def test_create_choices_via_poll_viewset(self):
        url = reverse('polls:poll-list')
        response = self.client.post(url, data=TEST_POLL)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Choice.objects.count(), 2)

        poll = Poll.objects.first()
        choices = Choice.objects.all()
        for choice in choices:
            self.assertEqual(choice.poll, poll)

    def test_response_data_when_create_poll(self):
        url = reverse('polls:poll-list')
        response = self.client.post(url, data=TEST_POLL)

        response_data = json.loads(response.content.decode())
        expect_keys = [
            'id', 'name', 'description', 
            'format_modified', 'choices',
        ]
        for key in expect_keys:
            self.assertIn(key, response_data.keys())

        self.assertEqual(len(expect_keys), len(response_data.keys()))


class ChoiceAPITest(TestCase):

    def test_choice_list_view(self):
        poll = create_a_poll_with_choices()
        data = get_choices_data(poll)

        url = reverse('polls:choice-list', kwargs={'pk': poll.pk})
        response = self.client.get(url) 

        self.assertJSONEqual(response.content.decode(), data)

    def test_create_choice_via_post_method_on_list_view(self):
        poll = create_a_poll()

        url = reverse('polls:choice-list', kwargs={'pk': poll.pk})
        response = self.client.post(url, data=TEST_CHOICES[0])
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Choice.objects.count(), 1)
        self.assertEqual(poll.choice_set.count(), 1)
        self.assertJSONEqual(response.content.decode(), TEST_CHOICES[0])