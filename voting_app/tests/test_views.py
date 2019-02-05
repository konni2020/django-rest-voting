import json
from unittest import skip

# from rest_framework.test import APIRequestFactory
from django.forms.models import model_to_dict
from django.shortcuts import reverse
from django.test import TestCase, tag
from rest_framework.test import APITestCase

from voting_app.models import Poll, Choice
from accounts.serializers import UserSerializer


TEST_USER = {
    'username': 'konni',
    'email': 'test@test.com',
    'password': 'q,1234',
}

TEST_POLL = {
    'name': 'john',
    'description': 'What fruit below do you like most?',
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


def create_user(data=None):
    if not data:
        data = TEST_USER

    user = UserSerializer(data=data)
    if user.is_valid():
        user.save()

    return user


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


@skip
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
        response = self.client.post(
            url, data=json.dumps(TEST_POLL), 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Poll.objects.count(), 1)

    def test_create_choices_via_poll_viewset(self):
        url = reverse('polls:poll-list')
        response = self.client.post(
            url, data=json.dumps(TEST_POLL), 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Choice.objects.count(), 2)

        poll = Poll.objects.first()
        choices = Choice.objects.all()
        for choice in choices:
            self.assertEqual(choice.poll, poll)

    def test_response_data_when_create_poll(self):
        url = reverse('polls:poll-list')
        response = self.client.post(
            url, data=json.dumps(TEST_POLL), 
            content_type='application/json'
        )

        response_data = json.loads(response.content.decode())

        expect_keys = [
            'id', 'name', 'description', 
            'format_modified', 'choices',
        ]
        for key in expect_keys:
            self.assertIn(key, response_data.keys())

        self.assertEqual(len(expect_keys), len(response_data.keys()))


@skip
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


class TestToken(APITestCase):

    def setUp(self):
        create_user()

    def get_token(self):
        url = reverse('login')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json'
        )
        token = json.loads(response.content.decode())
        return token['token']

    def test_poll_list_view_without_token(self):
        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Authentication credentials were not provided.",
            response.content.decode()
        )

    def test_poll_list_view_with_incorrect_token(self):
        token = self.get_token()
        token_string = 'Token ' + token + 'wrong'
        self.client.credentials(HTTP_AUTHORIZATION=token_string)

        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Invalid token.",
            response.content.decode()
        )

    def test_poll_list_view_with_correct_token(self):
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
