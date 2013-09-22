from django.test import LiveServerTestCase
from selenium.webdriver import PhantomJS
from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException


class SeleniumTestCase(LiveServerTestCase):
    def _pre_setup(self):
        super(SeleniumTestCase, self)._pre_setup()
        self.driver = PhantomJS()

    def _post_teardown(self):
        self.driver.quit()
        super(SeleniumTestCase, self)._post_teardown()

    def login(self, username='user', password='password', url='login'):
        """
        Login to the server and be authenticated
        """
        self.open(reverse(url))
        self.driver.find_element_by_id("id_username").clear()
        self.driver.find_element_by_id("id_username").send_keys(username)
        self.driver.find_element_by_id("id_password").clear()
        self.driver.find_element_by_id("id_password").send_keys(password)
        self.driver.find_element_by_id("submit-id-login").click()

    def open(self, url):
        self.driver.get("%s%s" %(self.live_server_url, url))

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

    def assertUrlContains(self, url):
        self.assertIn(url, self.driver.current_url)

    def selectOptionBoxById(self, id_name, option_name):
        element = self.driver.find_element_by_id(id_name)
        for option in element.find_elements_by_tag_name('option'):
            if option.text == option_name:
                option.click()
