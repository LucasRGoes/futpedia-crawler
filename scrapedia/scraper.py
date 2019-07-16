# -*- coding: utf-8 -*-

import logging

import requests
import pandas as pd
from bs4 import BeautifulSoup

from .errors import FutpediaRequestError


BASE_URL = 'http://futpedia.globo.com'

LOGGER = logging.getLogger(__name__)


class Scrapedia(object):
	"""The object used as an abstraction over futpedia.globo.com. Provides
	easy access to its historical data and resources.
	"""
	def __init__(self):
		pass

	def status(self):
		"""Makes a request to the base url to see if it answers with 200 OK."""
		req = requests.get(BASE_URL)

		if req.status_code == 200:
			LOGGER.debug('Request \'{0}\' returned expected status code 200.' \
						 .format(BASE_URL))
			return True
		else:
			LOGGER.warning(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))
			return False

	def teams(self):
		"""Returns a list of all teams with historical data at
		futpedia.globo.com.
		"""
		req = requests.get('{0}/times'.format(BASE_URL))

		if req.status_code == 200:
			LOGGER.debug(
				'Request \'{0}/times\' returned expected status code 200.' \
				.format(BASE_URL))
			
			soup = BeautifulSoup(req.content, 'html.parser')
			teams = soup.find_all(name='li',
								  attrs={'itemprop': 'itemListElement'})

			return [team.string for team in teams]
		else:
			LOGGER.error(
				'Request \'{0}/times\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))

			raise FutpediaRequestError(
				'Request \'{0}/times\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))

	def championships(self):
		"""Returns a list of all championships covered by futpedia.globo.com.
		"""
		req = requests.get(BASE_URL)

		if req.status_code == 200:
			LOGGER.debug(
				'Request \'{0}\' returned expected status code 200.' \
				.format(BASE_URL))
			
			soup = BeautifulSoup(req.content, 'html.parser')
			championships_table = soup.find(name='ul',
											attrs={'class': 'agregador'})

			print(championships_table)

			# return [team.string for team in teams]
			return []
		else:
			LOGGER.error(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))

			raise FutpediaRequestError(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))
