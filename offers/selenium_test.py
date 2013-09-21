from django.test import LiveServerTestCase
from selenium.webdriver import PhantomJS
from django.core.urlresolvers import reverse


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
        self.driver.find_element_by_id("id_username").send_keys(username)
        self.driver.find_element_by_id("id_password").send_keys(password)
        self.driver.find_element_by_css_selector("button.btn.btn-default").click()

    def open(self, url):
        self.driver.get("%s%s" %(self.live_server_url, url))
