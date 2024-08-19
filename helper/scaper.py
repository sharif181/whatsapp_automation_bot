import os
import pickle
import random
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    InvalidArgumentException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 30

	def __init__(self, url):
		self.url = url
		self.setup_done = False

		self.setup_driver_options()
		self.setup_driver()

	# Automatically close driver on destruction of the object
	def __del__(self):
		# self.driver.close()
		pass

	# Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
	# Also change the 'cdc_' string in the chromedriver.exe with Notepad++ for example with 'abc_' to prevent detecting it as a bot
	def setup_driver_options(self):
		self.driver_options = Options()

		arguments = [
			'--disable-blink-features=AutomationControlled',
			# '--headless'
		]

		experimental_options = {
			'excludeSwitches': ['enable-automation', 'enable-logging'],
			'prefs': {'profile.default_content_setting_values.notifications': 2},
			'detach': True
		}

		for argument in arguments:
			# self.driver_options.add_argument('--headless')
			self.driver_options.add_argument(argument)

		for key, value in experimental_options.items():
			self.driver_options.add_experimental_option(key, value)

	# Setup chrome driver with predefined options
	def setup_driver(self):
		chrome_driver_path = ChromeDriverManager(driver_version='127.0.6533.119').install()
		service = Service(executable_path=chrome_driver_path)
		self.driver = webdriver.Chrome(service=service, options = self.driver_options)
		self.driver.get(self.url)
		self.driver.maximize_window()
		self.setup_done = True


	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	def wait_random_time(self):
		random_sleep_seconds = round(random.uniform(0.20, 1.20), 2)

		time.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	def go_to_page(self, page, flag=False, xpath=None):
		# Wait random time before refreshing the page to prevent the detection as a bot
		self.wait_random_time()
		# Refresh the site url with the loaded cookies so the user will be logged in
		self.driver.get(page)
		if flag:
			self.scroll_page()
			print("waiting for page...")
			WebDriverWait(self.driver, 30).until(
				EC.element_to_be_clickable((By.XPATH, xpath)))
			print("page is loaded")


	def find_element(self, selector, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				print('ERROR: Timed out waiting for the element with css selector "' + selector + '" to load')
				# End the program execution because we cannot find the element
				exit()
			else:
				return False

		return element

	def find_element_by_xpath(self, xpath, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.XPATH, xpath))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				exit()
			else:
				return False

		return element

	# Wait random time before cliking on the element
	def element_click(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

	# Wait random time before cliking on the element
	def element_click_by_xpath(self, xpath, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)


	# Wait random time before sending the keys to the element
	def element_send_keys(self, selector, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)

		element.send_keys(text)

	# Wait random time before sending the keys to the element
	def element_send_keys_by_xpath(self, xpath, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		
		element.send_keys(text)

	def input_file_add_files(self, selector, files):
		# Intialize the condition to wait
		wait_until = EC.presence_of_element_located((By.CSS_SELECTOR, selector))

		try:
			# Wait for input_file to load
			input_file = WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except:
			print('ERROR: Timed out waiting for the input_file with selector "' + selector + '" to load')
			# End the program execution because we cannot find the input_file
			exit()

		self.wait_random_time()

		try:
			input_file.send_keys(files)
		except InvalidArgumentException:
			print('ERROR: Exiting from the program! Please check if these file paths are correct:\n' + files)
			exit()

	# Wait random time before clearing the element
	def element_clear(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		element.clear()

	def element_delete_text(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)
		
		# Select all of the text in the input
		element.send_keys(Keys.LEFT_SHIFT + Keys.HOME)
		# Remove the selected text with backspace
		element.send_keys(Keys.BACK_SPACE)

	def element_wait_to_be_invisible(self, selector):
		wait_until = EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))

		try:
			WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except:
			print('Error waiting the element with selector "' + selector + '" to be invisible')
	
	def scroll_to_element(self, selector):
		element = self.find_element(selector)

		self.driver.execute_script('arguments[0].scrollIntoView(true);', element)

	def scroll_to_element_by_xpath(self, xpath):
		element = self.find_element_by_xpath(xpath)

		self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
	
	def find_elements_by_custom_tag_name(self, tag_name, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.TAG_NAME, tag_name))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
			links = self.driver.find_elements(By.TAG_NAME, tag_name)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + tag_name + '" to load')
				exit()
			else:
				return False

		return links
	
	def get_page_source(self):
		self.wait_random_time()
		return self.driver.page_source
		# element = self.driver.find_element(By.TAG_NAME, 'body')
		# return element.get_attribute('innerHTML')

	def scroll_page(self):
		# print("scrolling down")
		time_to_sleep = round(random.uniform(2, 20), 2)


		time.sleep(time_to_sleep // 2)
		# Scroll down gradually
		scroll_height = self.driver.execute_script('return document.documentElement.scrollHeight')
		for i in range(0, scroll_height, 100):
			self.driver.execute_script(f'window.scrollTo(0, {i});')
			time.sleep(0.05)  # Adjust the sleep duration to control the scrolling speed
		
		# print("scrolling up")
		time.sleep(time_to_sleep // 2)
		# Scroll up gradually
		for i in range(scroll_height, 0, -100):
			self.driver.execute_script(f'window.scrollTo(0, {i});')
			time.sleep(0.06)  # Adjust the sleep duration to control the scrolling speed