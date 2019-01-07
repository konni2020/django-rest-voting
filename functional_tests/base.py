import time

from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException


MAX_WAIT = 3

def wait(fn):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except(AssertionError, WebDriverException) as err:
                if time.time() - start_time > MAX_WAIT:
                    raise err
                time.sleep(0.5)
    return wrapper


class BaseFunctionalTest(StaticLiveServerTestCase):
    """
    ### wait_for: wait for special function
    ### wait_for_check: wait some time to check element
        ### check for equal
    ### wait_for_click: wait some time to click an element ro raise error
    ### wait_for_element: wait some time to get an element and return or raise error
    ### wait_for_elements: similiar to wait_for_element but return multiple elements
    ### wait_for_select: wait for selecting an option, and return the select tag
    ### check_present_url_regex: check browser's url
    ### check_browser_title: check browser's title
    ### check_data_in_page: check if some data in the page source
    ### check_data_not_in_page: check if some data doesn't in the page source
    ### check_css_style: check some element's css property
    ### go_to_url: a shorcut for goint to a special url
    ### submit_form: submit form, only submit simple text input, so it often need be altered in a special app

    """

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except(AssertionError, WebDriverException) as err:
                if time.time() - start_time > MAX_WAIT:
                    raise err
                time.sleep(0.5)

    @wait
    def wait_for_check(self, assertion, element1, element2):
        if assertion =='regex':
            self.assertRegex(element1, element2)
        elif assertion == 'equal':
            self.assertEqual(element1, element2)
        elif assertion == 'in':
            self.assertIn(element1, element2)
        elif assertion == 'not in':
            self.assertNotIn(element1, element2)
        else:
            raise Exception('Here is something go wrong: the assertion can\'t be understood')
        return

    def wait_for_click(self, by, text, target=None):
        self.wait_for_element(by, text, target).click()

    def check_present_url_regex(self, url):
        self.wait_for_check('regex', self.browser.current_url, url)

    def check_for_equal(self, element1, element2):
        self.wait_for_check('equal', element1, element2)

    @wait
    def check_data_in_page(self, data):
        for value in data.values():
            if type(value) == tuple:
                for v in value:
                    self.assert_in_page(v)
            else:
                self.assert_in_page(value)

    @wait
    def check_css_style(self, element, property_name, value):
        # it will check the css property and wait for some time
        self.assertEqual(
            element.value_of_css_property(property_name),
            value
        )

    @wait
    def check_data_not_in_page(self, data):
        for value in data.values():
            if type(value) != tuple:
                self.assert_not_in_page(value)

    @wait
    def assert_in_page(self, text):
        self.assertIn(text, self.browser.page_source)

    @wait
    def assert_not_in_page(self, text):
        self.assertNotIn(text, self.browser.page_source)

    def check_browser_title(self, title):
        self.check_for_equal(self.browser.title, title)

    @wait
    def wait_for_element(self, by, text, target=None):
        # get the target
        if not target:
            target = self.browser

        if by =='id':
            element = target.find_element_by_id(text)
        elif by == 'class':
            element = target.find_element_by_class_name(text)
        elif by == 'tag':
            element = target.find_element_by_tag_name(text)
        elif by == 'link_text':
            element = target.find_element_by_link_text(text)
        elif by == 'name':
            element = target.find_element_by_name(text)
        elif by == 'xpath':
            element = target.find_element_by_xpath(text)
        elif by == 'css':
            element = target.find_element_by_css_selector(text)
        else:
            raise Exception('Here is something go wrong: the assertion can\'t be understood')
        return element

    @wait
    def wait_for_elements(self, by, text, target=None):
        # get multiple target
        if not target:
            target = self.browser

        if by == 'class':
            element_list = target.find_elements_by_class_name(text)
        elif by == 'tag':
            element_list = target.find_elements_by_tag_name(text)
        elif by == 'link_text':
            element_list = target.find_elements_by_link_text(text)
        elif by == 'name':
            element_list = target.find_elements_by_name(text)
        elif by == 'xpath':
            element_list = target.find_elements_by_xpath(text)
        elif by == 'css':
            element_list = target.find_elements_by_css_selector(text)
        else:
            raise Exception('Here is something go wrong: the assertion can\'t be understood')
        return element_list

    @wait
    def wait_for_select(self, tag_id, select_type, value):
        """
        tag_id: the id of select tag
        select_type: how to select the option, by index/visible_text/value
        value: the value use to select option
        """
        # convert value to string
        value = str(value)
        # get element
        element = self.wait_for_element('id', tag_id)
        # convert it to select object
        select = Select(element)

        if select_type == 'index':
            select.select_by_index(value)
        elif select_type == 'text':
            select.select_by_visible_text(value)
        elif select_type == 'value':
            select.select_by_value(value)
        else:
            raise Exception('Here is something go wrong: the assertion can\'t be understood')
        return element

    def go_to_url(self, url):
        self.browser.get(self.live_server_url + url)

    def typing_input(self, target, text, clear=True):
        if clear:
            target.clear()

        target.send_keys(text)

    def submit_form(self, data=None, form=None, submit=True, submit_type='css',
            submit_value='input[type="submit"]'):
        if not data:
            data = dict()

        for key, value in data.items():
            inputbox = self.wait_for_element('name', key, target=form)
            self.typing_input(inputbox, value)

        if submit is True:
            self.wait_for_click(submit_type, submit_value, target=form)
