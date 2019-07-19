"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: CoreScraper, MainScraper, TeamScraper, GameScraper,
ChampionshipScraper.
"""

import json
import logging
from functools import partial

import requests
import pandas as pd
from bs4 import BeautifulSoup
from cachetools import cachedmethod, TTLCache
from cachetools.keys import hashkey
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .errors import ScrapediaRequestError, ScrapediaParseError, \
					ScrapediaNotFoundError


BASE_PROTOCOL = 'http://'
BASE_HOST = 'futpedia.globo.com'
BASE_URL = '{0}{1}'.format(BASE_PROTOCOL, BASE_HOST)


class CoreScraper(object):
	"""Core of all of Scrapedia's scrapers that includes requesting, caching
	and logging functionalities."""

	def __init__(self, base_url: str=BASE_URL, request_retries: int=5,
				 cache_maxsize: int=10, cache_ttl: int=300,
				 logger_disable: bool=False):
		"""CoreScraper constructor.
		
		Parameters
		----------
		base_url: str -- base url for all of the scraper requests (default
		BASE_URL)
		request_retries : int -- number of maximum retries of requests on
		cases where the status code is in a given set (default 5)
		cache_maxsize : int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl : int -- time to live in seconds for internal caching of
		data (default 300)
		logger_disable : bool -- a flag to enable or disable logging (default
		False)
		"""
		self.url = base_url
		self.session = requests.Session()
		self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
		self.logger = logging.getLogger(self.__class__.__name__)

		retries = Retry(total=request_retries, backoff_factor=1,
						status_forcelist=[403, 404, 502, 503, 504])

		self.session.mount(BASE_PROTOCOL, HTTPAdapter(max_retries=retries))
		self.logger.disabled = logger_disable

	def __enter__(self):
		"""CoreScraper's enter method for context management."""
		return self

	def __exit__(self, type, value, tb):
		"""CoreScraper's exit method for context management."""
		self.session.close()


class ChampionshipScraper(CoreScraper):
	"""Scraper that provides an interface to obtain data related to specific
	championships.

	Methods: status.
	"""
	def __init__(self, name, endpoint, base_url: str=BASE_URL,
				 request_retries: int=5, cache_ttl: int=300,
				 logger_disable: bool=False):
		"""ChampionshipScraper's constructor.
	
		Parameters @CoreScraper
		-----------------------
		name : str -- championship name
		endpoint : str -- endpoint of the championship webpage
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=10, cache_ttl=cache_ttl,
						 logger_disable=logger_disable)
		self.name = name
		self.endpoint = endpoint

	def status(self):
		"""Verifies if Futpédia's championship page is currently up.

		Returns
		-------
		flag : bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get('{0}{1}'.format(self.url, self.endpoint))

			self.logger.debug('Futpédia\'s {0} page is currently online.' \
							  .format(self.name))
			return True
		except Exception as err:
			self.logger.warning(
				'Futpédia\'s {0} page is currently not online: {1}.' \
				.format(self.name, err))
			return False

	def fetch(self, target_season, number_seasons=1):
		"""Fetches data of each seasons of the championship between the
		target_season and target_season + number_seasons - 1.
		
		Keyword arguments:
		target_season -- the starting season to fetch;
		number_seasons -- number of seasons to be fetched;
		"""
		req = self.session.get('{0}/{1}'.format(BASE_URL, self.href))

		if req.status_code == 200:
			self.logger.debug(
				'Request \'{0}/{1}\' returned expected status code 200.' \
				.format(BASE_URL, self.href))
			
			soup = BeautifulSoup(req.content, 'html.parser')
			tag = soup.find(
				'script',
				string=lambda s: s is not None and s.find('static_host') != -1
			)

			# Finds target text at tag to parse it
			stt = tag.string.find('{"campeonato":')
			end = tag.string.find('}]};') + 3
			championships = json.loads(tag.string[stt:end])

			return championships['edicoes']

		else:
			self.logger.error(
				'Request \'{0}/{1}\' returned unexpected status code {2}.' \
				.format(BASE_URL, self.href, req.status_code))

			raise FutpediaRequestError(
				'Request \'{0}/{1}\' returned unexpected status code {2}.' \
				.format(BASE_URL, self.href, req.status_code))


class MainScraper(CoreScraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: status, team, teams, game, games, championship, championships.
	"""
	def __init__(self, base_url: str=BASE_URL, request_retries: int=5,
				 cache_ttl: int=300, logger_disable: bool=False):
		"""MainScraper's constructor.
	
		Parameters @CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=3, cache_ttl=cache_ttl,
						 logger_disable=logger_disable)

	def status(self) -> bool:
		"""Verifies if Futpédia is currently online.

		Returns
		-------
		flag : bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get(self.url)

			self.logger.debug('Futpédia is currently online.')
			return True
		except Exception as err:
			self.logger.warning('Futpédia is currently not online: {0}.' \
								.format(err))
			return False

	def teams(self) -> list:
		"""Returns list of Futpédia's teams.

		Obs: Obtains teams from private method __scrap_teams() and modifies
		the response so that only the teams uids and names are returned.

		Returns
		-------
		teams : list -- list with dictionaries of teams including uids and
		names
		"""
		return [{'uid': v['uid'], 'name': v['name']} \
				for k, v in self.__scrap_teams().items()]

	def championship(self, uid: int) -> ChampionshipScraper:
		"""Factory to return an instance of a ChampionshipScraper class based
		on the chosen championship uid using cached or requested data.

		Parameters
		----------
		uid : int -- uid of the championship to have a scraper built

		Returns
		-------
		parser : ChampionshipScraper -- scraper built targeting the chosen
		championship webpage
		"""

		champs = self.__scrap_championships()
		champ = champs.get(uid)

		if champ is not None:
			return ChampionshipScraper(
				champ['name'], champ['endpoint'], base_url=self.url,
				logger_disable=self.logger.disabled)
		else:
			raise ScrapediaNotFoundError('The chosen uid could not be'
										' found, use a MainScraper instance to'
										' list all championships using'
										' championships() to find the uid you'
										' are looking for.')

	def championships(self) -> list:
		"""Returns list of Futpédia's championships.

		Obs: Obtains championships from private method __scrap_championships()
		and modifies the response so that only the championships uids and
		names are returned.

		Returns
		-------
		teams : list -- list with dictionaries of championships including uids
		and names
		"""
		return [{'uid': v['uid'], 'name': v['name']} \
				for k, v in self.__scrap_championships().items()]

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'teams'))
	def __scrap_teams(self) -> dict:
		"""Fetches list of teams, parses and transforms it into a data object.

		Returns
		-------
		teams : dict -- {
			name : str -- team name
			endpoint : str -- endpoint of the team webpage
		}
		"""
		try:
			# Fetches
			req = self.session.get('{0}/times'.format(self.url))
			self.logger.debug(
				'Request \'{0}/times\' returned expected status code 200.' \
				.format(self.url))

			# Parses
			soup = BeautifulSoup(req.content, 'html.parser')
			raw_teams = soup.find_all(
				name='li', attrs={'itemprop': 'itemListElement'})

			if not len(raw_teams) > 0:
				raise ScrapediaParseError(
					'Expected <li itemprop="itemListElement"> tags, but none'
					' were found while parsing.')

			# Transforms
			teams = {}
			for raw_team in raw_teams:
				team = {'name': raw_team.string,
						'endpoint': raw_team.a.get('href')}

				team['uid'] = hash(team['name'])
				teams[team['uid']] = team

			return teams

		except Exception as err:
			self.logger.error('Futpédia is currently not online: {0}.' \
							  .format(err))
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'champs'))
	def __scrap_championships(self) -> dict:
		"""Fetches list of championships, parses and transforms it into a data
		object.

		Returns
		-------
		championships : dict -- {
			name : str -- championship name
			endpoint : str -- endpoint of the championship webpage
		}
		"""
		try:
			# Fetches
			req = self.session.get(self.url)
			self.logger.debug(
				'Request \'{0}\' returned expected status code 200.' \
				.format(self.url))

			# Parses
			soup = BeautifulSoup(req.content, 'html.parser')
			raw_champs = soup.find(
				name='script',
				attrs={'type': 'text/javascript',
					   'language': 'javascript',
					   'charset': 'utf-8'}
			)

			if not len(raw_champs) > 0:
				raise ScrapediaParseError(
					'Expected <script type="text/javascript"'
					' language="javascript" charset="utf-8"> tag, but it'
					' was not found while parsing.')

			stt = raw_champs.string.find('[{')
			end = raw_champs.string.find('}]') + 2
			raw_champs = raw_champs.string[stt:end]

			# Transforms
			champs = {}
			for raw_champ in json.loads(raw_champs):
				champ = {'name': raw_champ['nome'],
						 'endpoint': '/{0}'.format(raw_champ['slug'])}

				champ['uid'] = hash(champ['name'])
				champs[champ['uid']] = champ

			return champs

		except json.decoder.JSONDecodeError as err:
			self.logger.error('Fetched content could not be parsed: {0}.' \
							  .format(err))
			raise ScrapediaParseError(
				'Fetched content could not be parsed.') from err

		except Exception as err:
			self.logger.error('Futpédia is currently not online: {0}.' \
							  .format(err))
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err
