import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .server_tools import reset_database


MAX_WAIT = 5


def wait(fn):
	def modified_fn(*args, **kwargs):
		start_time = time.time()
		while True:
			try:
				return fn(*args, **kwargs)
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)
	return modified_fn



class FunctionalTest(StaticLiveServerTestCase):
	"""Функциональный тест."""


	def setUp(self):
		"""Установка."""
		self.browser = webdriver.Chrome()
		self.staging_server = os.environ.get('STAGING_SERVER')
		if self.staging_server:
			self.live_server_url = 'http://' + self.staging_server
			reset_database(self.staging_server)


	def tearDown(self):
		"""Демонтаж."""
		self.browser.quit()


	@wait
	def wait_for_row_in_list_table(self, row_text):
		"""Ожидает строку в таблице списка."""
		table = self.browser.find_element(By.ID, 'id_list_table')
		rows = table.find_elements(By.TAG_NAME, 'tr')
		self.assertIn(row_text, [row.text for row in rows])


	@wait
	def wait_for(self, fn):
		"""Добавляет ожидание."""
		return fn()


	def get_item_input_box(self):
		"""Получить поле ввода для элемента."""
		return self.browser.find_element(By.ID, 'id_text')


	@wait
	def wait_to_be_logged_in(self, email):
		"""Ожидать входа в систему."""
		self.browser.find_element(By.LINK_TEXT, 'Log out')
		navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
		self.assertIn(email, navbar.text)


	@wait
	def wait_to_be_logged_out(self, email):
		"""Ожидать выхода из системы."""
		self.browser.find_element(By.NAME, 'email')
		navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
		self.assertNotIn(email, navbar.text)


	def add_list_item(self, item_text):
		"""Добавить элемент списка."""
		num_rows = len(
			self.browser.find_elements(By.CSS_SELECTOR, '#id_list_table tr')
		)
		self.get_item_input_box().send_keys(item_text)
		self.get_item_input_box().send_keys(Keys.ENTER)
		item_number = num_rows + 1
		self.wait_for_row_in_list_table(f'{item_number}: {item_text}')
