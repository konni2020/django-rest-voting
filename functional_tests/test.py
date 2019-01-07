from .base import BaseFunctionalTest
import time

class NewVisitorTest(BaseFunctionalTest):
    # port = 8080

    def setUp(self):
        super().setUp()
        self.live_server_url = 'http://127.0.0.1:8080'

    # def test_index_page(self):
    #     self.go_to_url('')
    #     self.assertIn('Welcome to Your Voting App', self.browser.page_source)

    def test_create_new_poll(self):
        poll_data = {
            'name': 'john',
            'description': 'what fruit do you like most?',
        }
        choices_data = [
            {'text': 'apple'},
            {'text': 'orange'},
            {'text': 'mango'},
        ]

        # John want to make a new poll. he goes to the index page
        self.go_to_url('')

        # then fill the new poll form
        form = self.wait_for_element('class', 'create-voting-form')
        self.submit_form(data=poll_data, form=form, submit=False)

        choice_inputs = self.wait_for_elements('css', 'input[name^="choice-"]', target=form)
        for i, choice in enumerate(choices_data):
            self.typing_input(choice_inputs[i], choice['text'])
        
        self.submit_form(form=form, submit_value='button')
        time.sleep(2)
        # he sees the new poll display in the page's voting list
        voting_list = self.wait_for_elements('class', 'voting__item')

        self.assertEqual(len(voting_list), 1)

