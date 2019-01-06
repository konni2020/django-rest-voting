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


class PollModelTest(TestCase):

    def test_create_and_retrieve_poll(self):
        poll = Poll()
        for key, value in TEST_POLL.items():   
            setattr(poll, key, value)
        poll.save()

        self.assertEqual(Poll.objects.count(), 1)

        poll = Poll.objects.first()
        for key, value in TEST_POLL.items():   
            self.assertEqual(getattr(poll, key), value)

    def test_valid_poll_should_has_more_than_one_choice(self):
        poll = create_a_poll()
        self.assertEqual(Poll.valid_polls().count(), 0)

        for i in range(3):
            choice = Choice.objects.create(text='test choice', poll=poll)

        self.assertEqual(Poll.valid_polls().count(), 1)

    def test_polls_should_in_reverse_modified_order(self):
        poll_1 = create_a_poll()
        poll_2 = create_a_poll()

        polls = Poll.objects.all()

        self.assertEqual(poll_2, polls[0])
        self.assertEqual(poll_1, polls[1])


class ChoiceModelTest(TestCase):

    def test_create_and_retrieve_choice(self):
        poll = create_a_poll()
        choice = Choice()
        for key, value in TEST_CHOICES[0].items():
            setattr(choice, key, value)
        choice.poll = poll
        choice.save()

        self.assertEqual(Choice.objects.count(), 1)

        choice = Choice.objects.first()
        for key, value in TEST_CHOICES[0].items():   
            self.assertEqual(getattr(choice, key), value)

    def test_default_total_is_zero(self):
        poll = create_a_poll()
        Choice.objects.create(text='test choice', poll=poll)
        choice = Choice.objects.get(text='test choice')

        self.assertEqual(choice.total, 0)

    def test_add_choices_to_poll(self):
        poll = create_a_poll()
        for choice_data in TEST_CHOICES:
            choice = Choice()

            for key, value in choice_data.items():
                setattr(choice, key, value)

            choice.poll = poll
            choice.save()    

        self.assertEqual(poll.choice_set.count(), 3)