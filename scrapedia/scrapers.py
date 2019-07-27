"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: CoreScraper, MainScraper, TeamScraper, GameScraper,
ChampionshipScraper
"""

import json
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
	def __init__(self, base_url: str=BASE_URL, request_retries: int=5,
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

		retries = Retry(total=request_retries, backoff_factor=1,
						status_forcelist=[403, 404, 502, 503, 504])

		self.session.mount(BASE_PROTOCOL, HTTPAdapter(max_retries=retries))

	def __enter__(self):
		"""CoreScraper's enter method for Python's 'with' management."""
		return self

	def __exit__(self, type, value, tb):
		"""CoreScraper's exit method for Python's 'with' management."""
		self.session.close()


class ChampionshipScraper(CoreScraper):
	"""Scraper that provides an interface to obtain data related to specific
	championships.

	Methods: status, seasons.
	"""
	def __init__(self, name: str, endpoint: str, base_url: str=BASE_URL,
				 request_retries: int=5, cache_ttl: int=300):
		"""ChampionshipScraper's constructor.
	
		Parameters
		----------
		name: str -- championship name
		endpoint: str -- endpoint of the championship webpage
		Other parameters @scrapers.CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=10, cache_ttl=cache_ttl)
		self.name = name
		self.endpoint = endpoint

	def status(self) -> bool:
		"""Verifies if Futpédia's championship page is currently up.

		Returns
		-------
		flag: bool -- if online returns True, otherwise False
		"""
		try:
			self.session.get('{0}{1}'.format(self.url, self.endpoint))
			return True

		except Exception as err:
			return False

	def seasons(self, target: int, number: int=1) -> dict:
		"""Returns list of Futpédia's seasons of the instance's championship.
		Obtains teams from private method __scrap_seasons() and modifies the
		response so that only the teams between target and number - 1 are
		returned.

		Parameters
		----------
		target: int -- the season to fetch information about
		number: int -- the number of seasons to be fetched starting with the
		target

		Returns
		-------
		teams: list -- list with dictionaries of seasons including year, 
		start_date, end_date, number_goals and number_games
		"""
		if number < 1:
			raise ValueError(
				'The \'number\' parameter should be higher than 0.')

		seasons = [
			{'year': k, 'start_date': v['start_date'],
			 'end_date': v['end_date'], 'number_goals': v['number_goals'],
			 'number_games': v['number_games']} \
			for k, v in self.__scrap_seasons().items()
		]

		# Validates chosen season
		first_year = seasons[-1]['year']
		last_year = seasons[0]['year']
		if target < first_year or target > last_year:
			raise ValueError(
				'The \'target\' parameter should be between {0} and {1}'
				' for this championship.'.format(first_year, last_year))

		return list(filter(
			lambda x: x['year'] >= target \
					  and x['year'] <= target + number - 1,
			seasons
		))

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'seasons'))
	def __scrap_seasons(self) -> dict:
		"""Fetches list of seasons, parses and transforms it into a data
		object.

		Returns
		-------
		seasons: dict -- {
			start_date: datetime -- date the season started
			end_date: datetime -- date the season ended
			number_goals: int -- number of goals made by all teams
			number_games: int -- number of games played that season
			endpoint: str -- endpoint of the season webpage
		}
		"""

		# Fetches
		try:
			req = self.session.get(
				'{0}/campeonato/{1}'.format(self.url, self.endpoint))
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

			seasons = {}
			for raw_season in json.loads(raw_seasons).get('edicoes'):
				raw_season_dates = raw_season.get('edicao')

				season = {
					'start_date': datetime.strptime(
									raw_season_dates.get('data_inicio'),
									'%Y-%m-%d'
								  ),
					'end_date': datetime.strptime(
									raw_season_dates.get('data_fim'),
									'%Y-%m-%d'
								),
					'number_goals': raw_season.get('gols'),
					'number_games': raw_season.get('jogos'),
					'endpoint': '/{0}'.format(
						raw_season_dates.get('slug_editorial'))
				}

				year = season.get('start_date').year
				seasons[year] = season

			return seasons

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err


class MainScraper(CoreScraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: status, team, teams, game, games, championship, championships.
	"""
	def __init__(self, base_url: str=BASE_URL, request_retries: int=5,
				 cache_ttl: int=300):
		"""MainScraper's constructor.
	
		Parameters @CoreScraper
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=3, cache_ttl=cache_ttl)

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

	def teams(self) -> list:
		"""Returns list of Futpédia's teams.

		Obs: Obtains teams from private method __scrap_teams() and modifies
		the response so that only the teams ids and names are returned.

		Returns
		-------
		teams: list -- list with dictionaries of teams including ids and
		names
		"""
		return [
			{'id': k, 'name': v['name']} \
			for k, v in self.__scrap_teams().items()
		]

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

		champs = self.__scrap_championships()
		champ = champs.get(id_)

		if champ is not None:
			return ChampionshipScraper(
				champ['name'], champ['endpoint'], base_url=self.url)
		else:
			raise ScrapediaNotFoundError('The chosen id could not be found.')

	def championships(self) -> list:
		"""Returns list of Futpédia's championships.

		Obs: Obtains championships from private method __scrap_championships()
		and modifies the response so that only the championships ids and
		names are returned.

		Returns
		-------
		teams: list -- list with dictionaries of championships including ids
		and names
		"""
		return [
			{'id': k, 'name': v['name']} \
			for k, v in self.__scrap_championships().items()
		]

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'teams'))
	def __scrap_teams(self) -> dict:
		"""Fetches list of teams, parses and transforms it into a data object.

		Returns
		-------
		teams: dict -- {
			name: str -- team name
			endpoint: str -- endpoint of the team webpage
		}
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
			teams = {}
			for index, raw_team in enumerate(raw_teams):
				team = {'name': raw_team.string,
						'endpoint': raw_team.a.get('href')}
				teams[index + 1] = team

			return teams

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err

	@cachedmethod(lambda self: self.cache, key=partial(hashkey, 'champs'))
	def __scrap_championships(self) -> dict:
		"""Fetches list of championships, parses and transforms it into a data
		object.

		Returns
		-------
		championships: dict -- {
			name: str -- championship name
			endpoint: str -- endpoint of the championship webpage
		}
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
			
			champs = {}
			for index, raw_champ in enumerate(json.loads(raw_champs)):
				champ = {'name': raw_champ.get('nome'),
						 'endpoint': '/{0}'.format(raw_champ.get('slug'))}
				champs[index + 1] = champ

			return champs

		except Exception as err:
			raise ScrapediaTransformError(
				'Parsed content could not be accessed.') from err
