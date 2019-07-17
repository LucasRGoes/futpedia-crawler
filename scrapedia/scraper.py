# -*- coding: utf-8 -*-

import re
import logging
from functools import partial

import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode
from cachetools import cachedmethod, TTLCache
from cachetools.keys import hashkey

from .errors import FutpediaRequestError, FutpediaNotFoundError


BASE_URL = 'http://futpedia.globo.com'


class Scrapedia(object):
	"""Class used as a stub over futpedia.globo.com. Provides easy access to
	its historical data and other resources like lists of teams and
	championships.

	Public methods: status, teams, championship, championships.
	"""
	def __init__(self, disable_logger=False, cache_size=2, cache_ttl=300):
		"""Scrapedia's constructor.
	
		Keyword arguments:
		disable_logger -- a boolean flag to enable or disable logging for the
						  class instance;
		cache_size -- the maximum size of the instance's inner cache;
		cache_ttl -- instance's inner cache time to live;
		"""
		self.logger = logging.getLogger(__name__)
		self.logger.disabled = disable_logger
		self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)

	def status(self):
		"""Requests base url and return True if it answers with 200 OK and
		False otherwise.
		"""
		req = requests.get(BASE_URL)

		if req.status_code == 200:
			self.logger.debug(
				'Request \'{0}\' returned expected status code 200.' \
				.format(BASE_URL))
			return True
		else:
			self.logger.warning(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))
			return False

	def teams(self):
		"""Retrieves list of teams covered by futpedia.globo.com."""
		return [{'name': tv['name']} for tk, tv in self.__full_teams().items()]

	def championship(self, name):
		"""Returns an instance of a ScrapediaChampionship class based on the
		chosen championship.

		Keyword arguments:
		name -- name of the championship to be accessed;
		"""

		# Calculates hash and searches for the championship
		hash_ = unidecode(name.lower().replace(' ', ''))
		hash_table = self.__full_championships()

		champ = hash_table.get(hash_)

		if champ is not None:
			return ScrapediaChampionship(champ['name'], champ['href'])
		else:
			raise FutpediaNotFoundError('the chosen championship couldn\'t be'
										' found, see list of championships'
										' using Scrapedia.championships()')

	def championships(self):
		"""Retrieves list of championships covered by futpedia.globo.com."""
		return [{'name': cv['name'],
				 'first_season': cv['first_season'],
				 'last_season': cv['last_season']} \
				for ck, cv in self.__full_championships().items()]

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'teams'))
	def __full_teams(self):
		"""Retrieves and caches a list of teams with data including: (1) team
		'name' and (2) 'href' to the team page with historical data at
		futpedia.globo.com.

		Notes: This method has its results cached.
		"""
		req = requests.get('{0}/times'.format(BASE_URL))

		if req.status_code == 200:
			self.logger.debug(
				'Request \'{0}/times\' returned expected status code 200.' \
				.format(BASE_URL))
			
			soup = BeautifulSoup(req.content, 'html.parser')
			teams = soup.find_all(name='li',
								  attrs={'itemprop': 'itemListElement'})

			# Verifies if any content has returned from the parsing.
			if not len(teams) > 0:
				raise FutpediaNotFoundError('An expected attribute or tag is '
										    'missing from the requested page.')

			# Creates hash table to cache data
			hash_table = {}
			for team in teams:
				team = {
					'name': team.string,
					'href': team.a.get('href')
				}

				hash_ = unidecode(re.sub(r'\.|-|\ ', '', team['name'].lower()))
				hash_table[hash_] = team

			return hash_table
		else:
			self.logger.error(
				'Request \'{0}/times\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))

			raise FutpediaRequestError(
				'Request \'{0}/times\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))		

	@cachedmethod(
		lambda self: self.cache, key=partial(hashkey, 'championships'))
	def __full_championships(self):
		"""Retrieves and caches a list of championships with data including:
		(1) championship 'name', (2) 'href' to the championship page and years
		of the (3) 'first_season' and (4) 'last_season' covered by
		futpedia.globo.com.

		Notes: This method has its results cached.
		"""
		req = requests.get(BASE_URL)

		if req.status_code == 200:
			self.logger.debug(
				'Request \'{0}\' returned expected status code 200.' \
				.format(BASE_URL))
			
			soup = BeautifulSoup(req.content, 'html.parser')
			champs = soup.find(name='ul', attrs={'class': 'agregador'}) \
						 .find_all(name='a')

			# Verifies if any content has returned from the parsing.
			if not len(champs) > 0:
				raise FutpediaNotFoundError('An expected attribute or tag is '
										    'missing from the requested page.')

			# Creates hash table to cache data
			hash_table = {}
			for champ in champs:

				for txt in champ.strings:
					"""Splits championship's tag internal text and removes
					trailing characters."""
					clean_txt = list(map(lambda x: x.strip(), txt.split(' ')))
					
					# Verifies if any of the strings have alphabetical chars.
					if any(len(i) > 0 and i[0].isalpha() for i in clean_txt):
						name = ' '.join(clean_txt).lstrip()

					# Verifies if any of the strings have numbers.
					if any(len(i) > 0 and i[0].isdigit() for i in clean_txt):
						first_season = int(clean_txt[0])
						last_season = int(clean_txt[2])

				champ = {'name': name,
						 'href': champ.get('href'), 
						 'first_season': first_season,
						 'last_season': last_season}

				hash_ = unidecode(champ['name'].lower().replace(' ', ''))
				hash_table[hash_] = champ

			return hash_table
		else:
			self.logger.error(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))

			raise FutpediaRequestError(
				'Request \'{0}\' returned unexpected status code {1}.' \
				.format(BASE_URL, req.status_code))


class ScrapediaChampionship(object):
	"""Class used as a stub over futpedia.globo.com championship endpoints.

	Public methods: 
	"""
	def __init__(self, name, href):
		"""ScrapediaChampionship's constructor.
	
		Keyword arguments:
		name -- name of the championship to be used on the requests;
		href -- href of the championship webpage;
		"""
		self.logger = logging.getLogger(__name__)
		self.name = name
		self.href = href

	def status(self):
		"""Requests championship url and return True if it answers with 200 OK
		and False otherwise.
		"""
		req = requests.get('{0}/{1}'.format(BASE_URL, self.href))

		if req.status_code == 200:
			self.logger.debug(
				'Request \'{0}/{1}\' returned expected status code 200.' \
				.format(BASE_URL, self.href))
			return True
		else:
			self.logger.warning(
				'Request \'{0}/{1}\' returned unexpected status code {2}.' \
				.format(BASE_URL, self.href, req.status_code))
			return False
