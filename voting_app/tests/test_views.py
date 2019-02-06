import json
from unittest import skip

# from rest_framework.test import APIRequestFactory
from django.forms.models import model_to_dict
from django.contrib.auth import get_user
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase, tag
from rest_framework.test import APITestCase

from voting_app.models import Poll, Choice
from voting_app.serializers import PollSerializer, ChoiceSerializer
from accounts.serializers import UserSerializer


User = get_user_model()
"""
204 no content
401 unauthorized
403 forbidden ("You do not have permission to perform this action.")
"""


TEST_USER = {
    'username': 'konni',
    'email': 'test@test.com',
    'password': 'q,1234',
}

SECOND_TEST_USER = {
    'username': 'tom',
    'email': 'tom@test.com',
    'password': 'testpass',
}

TEST_POLL = {
    # 'name': 'konni',
    'description': 'What fruit below do you like most?',
    'choices': [
        {'text': 'apple'},
        {'text': 'orange'},
    ],
}

SECOND_TEST_POLL = {
    # 'name': 'tom',
    'description': 'What language below do you like most?',
    'choices': [
        {'text': 'python'},
        {'text': 'javascript'},
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


class BaseTest(APITestCase):

    @classmethod
    def create_user(cls, data=None):
        if not data:
            data = TEST_USER

        user = UserSerializer(data=data)
        if user.is_valid():
            user.save()

        return user

    @classmethod
    def create_a_poll(cls, user=None):
        if not user:
            user = User.objects.first()

        poll_serializer = PollSerializer(data=TEST_POLL)
        if poll_serializer.is_valid():
            poll = poll_serializer.save(author=user)
        else:
            print(poll_serializer.errors)
            return None

        return poll

    @classmethod
    def create_a_choice(cls, poll, instance=None, data=None):
        if instance:
            text = instance.text
            total = instance.total
        elif data:
            text = data['text']
            total = data['total']
        else:
            text = TEST_CHOICES[0]['text']
            total = 0

        data = {'text': text, 'total': total}
        choice_serializer = ChoiceSerializer(data=data)
        if choice_serializer.is_valid():
            choice = choice_serializer.save(poll=poll)

        return choice

    @classmethod
    def create_a_poll_with_choices(cls):
        poll = cls.create_a_poll()

        for choice_data in TEST_CHOICES:
            cls.create_a_choice(poll, data=choice_data)

        return poll

    @classmethod
    def get_choices_data(cls, poll):
        # get choices json data from a poll
        # -> [
        # {'text': 'apple', 'total': 3},
        # {'text': 'pear', 'total': 5},
        # {'text': 'watermelon', 'total': 10}
        # ]
        return list(poll.choice_set.all().values('text', 'total'))

    @classmethod
    def get_poll_json_data(cls, poll):
        fields = ['id', 'name', 'description', 'format_modified']
        data = model_to_dict(poll, fields=fields)
        data['choices'] = cls.get_choices_data(poll)
        data['author'] = poll.author.username
        return data

    @classmethod
    def get_poll_list_json_data(cls, polls):
        return [cls.get_poll_json_data(poll) for poll in polls]


class BaseViewTest(BaseTest):
    """
    it will auto create a user and login
    """
    def setUp(self):
        self.create_user()
        self.auto_login()

    def auto_login(self, user_data=None):
        if not user_data:
            user_data = TEST_USER

        # True if success login
        return self.client.login(
            username=user_data['username'],
            password=user_data['password'],
        )

    def assert_client_username(self, username):
        user = get_user(self.client)
        self.assertEqual(user.username, username)

    def show_response_content(self, response):
        print(response.content.decode())


class PollAPITest(BaseViewTest):

    def test_post_list_view(self):
        self.create_a_poll_with_choices()
        data = self.get_poll_list_json_data(Poll.objects.all())

        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_post_list_view_without_login(self):
        self.client.logout()
        self.assert_client_username('')

        self.create_a_poll_with_choices()
        data = self.get_poll_list_json_data(Poll.objects.all())

        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_poll_detail_view(self):
        poll = self.create_a_poll_with_choices()
        data = self.get_poll_json_data(poll)

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
            'id', 'author', 'description',
            'format_modified', 'choices',
        ]
        for key in expect_keys:
            self.assertIn(key, response_data.keys())

        self.assertEqual(len(expect_keys), len(response_data.keys()))

    def test_update_poll_use_put_method(self):
        self.create_a_poll_with_choices()
        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        url = reverse('polls:poll-detail', kwargs={'pk': poll.pk})
        response = self.client.put(url, data=SECOND_TEST_POLL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        self.assertEqual(poll.description, SECOND_TEST_POLL['description'])

    def test_update_poll_use_patch_method(self):
        self.create_a_poll_with_choices()
        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        url = reverse('polls:poll-detail', kwargs={'pk': poll.pk})
        new_data = {
            'description': 'new description'
        }
        response = self.client.patch(url, data=new_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        self.assertEqual(poll.description, new_data['description'])

    def test_can_not_update_poll_created_by_other_user(self):
        self.create_a_poll_with_choices()

        self.create_user(data=SECOND_TEST_USER)
        self.auto_login(user_data=SECOND_TEST_USER)

        self.assert_client_username(SECOND_TEST_USER['username'])

        poll = Poll.objects.first()
        url = reverse('polls:poll-detail', kwargs={'pk': poll.pk})
        response = self.client.put(url, data=SECOND_TEST_POLL)

        self.assertEqual(response.status_code, 403)

        poll = Poll.objects.first()
        self.assertEqual(poll.description, TEST_POLL['description'])

    def test_delete_poll(self):
        self.create_a_poll_with_choices()
        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        url = reverse('polls:poll-detail', kwargs={'pk': poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Poll.objects.count(), 0)

    def test_can_not_delete_poll_created_by_other_user(self):
        self.create_a_poll_with_choices()
        self.assertEqual(Poll.objects.count(), 1)

        # login as second user
        self.create_user(data=SECOND_TEST_USER)
        self.auto_login(user_data=SECOND_TEST_USER)

        self.assert_client_username(SECOND_TEST_USER['username'])

        poll = Poll.objects.first()
        url = reverse('polls:poll-detail', kwargs={'pk': poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Poll.objects.count(), 1)


class ChoiceAPITest(BaseViewTest):

    def test_choice_list_view(self):
        poll = self.create_a_poll_with_choices()
        data = self.get_choices_data(poll)

        url = reverse('polls:choice-list', kwargs={'pk': poll.pk})
        response = self.client.get(url)

        self.assertJSONEqual(response.content.decode(), data)

    def test_create_choice_via_post_method_on_list_view(self):
        poll = self.create_a_poll()
        url = reverse('polls:choice-list', kwargs={'pk': poll.id})
        response = self.client.post(url, data=TEST_CHOICES[0])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Choice.objects.count(), 1)
        self.assertEqual(poll.choice_set.count(), 1)
        self.assertJSONEqual(response.content.decode(), TEST_CHOICES[0])


class TestToken(BaseTest):

    def setUp(self):
        self.create_user()

    def get_token(self):
        url = reverse('login')
        response = self.client.post(
            url, json.dumps(TEST_USER),
            content_type='application/json'
        )
        token = json.loads(response.content.decode())
        return token['token']

    def test_poll_list_view_without_token(self):
        # app should allow users to see poll-list without token
        url = reverse('polls:poll-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

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
