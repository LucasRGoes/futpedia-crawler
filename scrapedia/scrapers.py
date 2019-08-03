"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: CoreScraper, MainScraper, ChampionshipScraper, SeasonScraper
"""

import json
import time
from datetime import datetime
from functools import partial

import requests
import pandas as pd
from bs4 import BeautifulSoup
from cachetools import cachedmethod, TTLCache
from cachetools.keys import hashkey
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .errors import ScrapediaFetchError, ScrapediaParseError, \
					ScrapediaTransformError, ScrapediaNotFoundError


BASE_PROTOCOL = 'http://'
BASE_HOST = 'futpedia.globo.com'
BASE_URL = '{0}{1}'.format(BASE_PROTOCOL, BASE_HOST)


class CoreScraper(object):
	"""Core of all of Scrapedia's scrapers. Includes requesting, caching and
	logging functionalities.

	Methods: __enter__, __exit__
	"""
	def __init__(self, base_url: str=BASE_URL, request_retries: int=12,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""CoreScraper's constructor.
		
		Parameters
		----------
		base_url: str -- base url for all of the scraper requests (default
		BASE_URL)
		request_retries: int -- number of maximum retries of requests on
		cases where the status code is in a given set (default 5)
		cache_maxsize: int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl: int -- time to live in seconds for internal caching of
		data (default 300)
		"""
		self.url = base_url
		self.session = requests.Session()
		self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

		self.request_retries = request_retries

		retries = Retry(total=self.request_retries, backoff_factor=1,
						status_forcelist=[403, 404, 502, 503, 504])

		self.session.mount(BASE_PROTOCOL, HTTPAdapter(max_retries=retries))

	def __enter__(self):
		"""CoreScraper's enter method for Python's 'with' management."""
		return self

	def __exit__(self, type, value, tb):
		"""CoreScraper's exit method for Python's 'with' management."""
		self.session.close()


class SeasonScraper(CoreScraper):
	"""Scraper that provides an interface to obtain data related to specific
	seasons of a championship.

	Methods: status, games
	"""
	def __init__(self, year: int, endpoint: str, base_url: str=BASE_URL,
				 request_retries: int=12, cache_ttl: int=300):
		"""SeasonScraper's constructor.
	
		Parameters
		----------
		year: int -- year in which the season occured
		endpoint: str -- endpoint of the season webpage
		Other parameters @scrapers.CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=1, cache_ttl=cache_ttl)
		self.year = year
		self.endpoint = endpoint

	def status(self) -> bool:
		"""Verifies if Futpédia's season page is currently up.

		Returns
		-------
		flag: bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get(
				'{0}/campeonato{1}'.format(self.url, self.endpoint))
			return True

		except Exception as err:
			return False

	def games(self):
		return self.__scrap_games()

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'games'))
	def __scrap_games(self):
		"""Fetches list of games, parses and transforms it into a data
		object.

		Returns
		-------
		games: pd.DataFrame -- dataframe with the season's games including ...
		and endpoints
		"""

		# Fetches
		try:
			req = self.session.get(
				'{0}/campeonato{1}'.format(self.url, self.endpoint))
		except Exception as err:
			raise ScrapediaFetchError(
				'Futpédia is currently not online.') from err

		return req.content


class ChampionshipScraper(CoreScraper):
	"""Scraper that provides an interface to obtain data related to specific
	championships.

	Methods: status, season, seasons
	"""
	def __init__(self, name: str, endpoint: str, base_url: str=BASE_URL,
				 request_retries: int=12, cache_ttl: int=300):
		"""ChampionshipScraper's constructor.
	
		Parameters
		----------
		name: str -- championship name
		endpoint: str -- endpoint of the championship webpage
		Other parameters @scrapers.CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=1, cache_ttl=cache_ttl)
		self.name = name
		self.endpoint = endpoint

	def status(self) -> bool:
		"""Verifies if Futpédia's championship page is currently up.

		Returns
		-------
		flag: bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get(
				'{0}/campeonato{1}'.format(self.url, self.endpoint))
			return True

		except Exception as err:
			return False

	def season(self, year: int) -> SeasonScraper:
		"""Factory to return an instance of a SeasonScraper class based
		on the chosen season year using cached or requested data.

		Parameters
		----------
		year: int -- year of the season to have a scraper built

		Returns
		-------
		scraper: SeasonScraper -- scraper built targeting the chosen
		season webpage
		"""
		seasons = self.__scrap_seasons()

		# Validates chosen season
		first_year = seasons.index[-1]
		last_year = seasons.index[0]
		if year < first_year or year > last_year:
			raise ValueError(
				'The \'year\' parameter should be between {0} and {1}'
				' for this championship.'.format(first_year, last_year))

		try:
			season = seasons.loc[year, :]
			return SeasonScraper(
				year, '{0}{1}'.format(self.endpoint, season['endpoint']),
				base_url=self.url, request_retries=self.request_retries
			)

		except Exception as err:
			raise ScrapediaNotFoundError(
				'The chosen year could not be found.') from err

	def seasons(self, target: int=None, number: int=1) -> pd.DataFrame:
		"""Returns list of Futpédia's seasons of the instance's championship.
		Obtains teams from private method __scrap_seasons() and modifies the
		response so that only the teams between target and number - 1 are
		returned.

		Parameters
		----------
		target: int -- the season to fetch information about (default None)
		number: int -- the number of seasons to be fetched starting from the
		target parameter (default 1)

		Returns
		-------
		teams: pd.DataFrame -- dataframe with the championship's seasons
		including year, start date, end date, number of goals and number of
		games
		"""
		if number < 1:
			raise ValueError(
				'The \'number\' parameter should be higher than 0.')

		seasons = self.__scrap_seasons()
		seasons = seasons.drop(columns=['endpoint'])

		if target is None:
			return seasons
		else:
			# Validates chosen season
			first_year = seasons.index[-1]
			last_year = seasons.index[0]
			if target < first_year or target > last_year:
				raise ValueError(
					'The \'target\' parameter should be between {0} and {1}'
					' for this championship.'.format(first_year, last_year))

			return seasons.loc[target + number - 1:target, :]

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'seasons'))
	def __scrap_seasons(self) -> pd.DataFrame:
		"""Fetches list of seasons, parses and transforms it into a data
		object.

		Returns
		-------
		seasons: pd.DataFrame -- dataframe with the championship's seasons
		including year, start date, end date, number of goals, number of games
		and endpoints
		"""

		# Fetches
		try:
			req = self.session.get(
				'{0}/campeonato{1}'.format(self.url, self.endpoint))
		except Exception as err:
			raise ScrapediaFetchError(
				'Futpédia is currently not online.') from err

		# Parses
		soup = BeautifulSoup(req.content, 'html.parser')
		raw_seasons = soup.find(
			'script',
			string=lambda s: s is not None and s.find('static_host') != -1
		)

		if raw_seasons is None:
			raise ScrapediaParseError(
				'Page has been fetched but the expected content was not found'
				' while parsing.')

		# Transforms
		try:

			stt = raw_seasons.string.find('{"campeonato":')
			end = raw_seasons.string.find('}]};') + 3
			raw_seasons = raw_seasons.string[stt:end]

			indexes = []
			seasons = []

			for raw_season in json.loads(raw_seasons).get('edicoes'):

				start_date = datetime.strptime(
					raw_season.get('edicao').get('data_inicio'), '%Y-%m-%d')
				end_date = datetime.strptime(
					raw_season.get('edicao').get('data_fim'), '%Y-%m-%d')
				number_goals = raw_season.get('gols')
				number_games = raw_season.get('jogos')
				endpoint = '/{0}'.format(
					raw_season.get('edicao').get('slug_editorial'))

				indexes.append(start_date.year)

				start_date = time.mktime(start_date.timetuple())
				end_date = time.mktime(end_date.timetuple())

				seasons.append([start_date, end_date, number_goals,
								number_games, endpoint])

			return pd.DataFrame(
				seasons, index=indexes, columns=['start_date', 'end_date',
												 'number_goals',
												 'number_games', 'endpoint']
			)

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err


class MainScraper(CoreScraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: status, championship, teams, championships
	"""
	def __init__(self, base_url: str=BASE_URL, request_retries: int=12,
				 cache_ttl: int=300):
		"""MainScraper's constructor.
	
		Parameters @CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=2, cache_ttl=cache_ttl)

	def status(self) -> bool:
		"""Verifies if Futpédia is currently online.

		Returns
		-------
		flag: bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get(self.url)
			return True

		except Exception as err:
			return False

	def championship(self, id_: int) -> ChampionshipScraper:
		"""Factory to return an instance of a ChampionshipScraper class based
		on the chosen championship id using cached or requested data.

		Parameters
		----------
		id_: int -- id of the championship to have a scraper built

		Returns
		-------
		scraper: ChampionshipScraper -- scraper built targeting the chosen
		championship webpage
		"""
		if id_ < 0:
			raise ValueError(
				'The \'id_\' parameter should be higher or equal to 0.')

		champs = self.__scrap_championships()

		try:
			champ = champs.iloc[id_, :]
			return ChampionshipScraper(
				champ['name'], champ['endpoint'], base_url=self.url,
				request_retries=self.request_retries
			)

		except Exception as err:
			raise ScrapediaNotFoundError(
				'The chosen id could not be found.') from err

	def teams(self) -> pd.DataFrame:
		"""Returns list of Futpédia's teams. Obtains teams from private method
		__scrap_teams() and modifies the response so that only the teams ids
		and names are returned.

		Returns
		-------
		teams: pd.DataFrame -- dataframe with the teams's ids and names
		"""
		df = self.__scrap_teams()
		return df.drop(columns=['endpoint'])

	def championships(self) -> pd.DataFrame:
		"""Returns list of Futpédia's championships. Obtains championships
		from private method __scrap_championships() and modifies the response
		so that only the championships ids and names are returned.

		Returns
		-------
		teams: pd.DataFrame -- dataframe with the championship's ids and names
		"""
		df = self.__scrap_championships()
		return df.drop(columns=['endpoint'])

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'teams'))
	def __scrap_teams(self) -> pd.DataFrame:
		"""Fetches list of teams, parses and transforms it into a data object.

		Returns
		-------
		teams: pd.DataFrame -- dataframe with the teams's ids, names and
		endpoints
		"""

		# Fetches
		try:
			req = self.session.get('{0}/times'.format(self.url))
		except Exception as err:
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err

		# Parses
		soup = BeautifulSoup(req.content, 'html.parser')
		raw_teams = soup.find_all(
			name='li', attrs={'itemprop': 'itemListElement'})

		if not len(raw_teams) > 0:
			raise ScrapediaParseError(
				'Page has been fetched but the expected content was not found'
				' while parsing.')

		# Transforms
		try:
			teams = []
			for raw_team in raw_teams:
				teams.append([raw_team.string, raw_team.a.get('href')])

			return pd.DataFrame(teams, columns=['name', 'endpoint'])

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'champs'))
	def __scrap_championships(self) -> pd.DataFrame:
		"""Fetches list of championships, parses and transforms it into a data
		object.

		Returns
		-------
		championships: pd.DataFrame -- dataframe with the championship's ids,
		names and endpoints
		"""

		# Fetches
		try:
			req = self.session.get(self.url)
		except Exception as err:
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err

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
				'Page has been fetched but the expected content was not found'
				' while parsing.')

		# Transforms
		try:
			stt = raw_champs.string.find('[{')
			end = raw_champs.string.find('}]') + 2
			raw_champs = raw_champs.string[stt:end]

			champs = []
			for raw_champ in json.loads(raw_champs):
				if raw_champ.get('nome') != 'Brasileiro Unificado':
					champs.append([raw_champ.get('nome'),
								   '/{0}'.format(raw_champ.get('slug'))])

			return pd.DataFrame(champs, columns=['name', 'endpoint'])

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err
