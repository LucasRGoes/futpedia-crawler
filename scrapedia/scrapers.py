"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: CoreScraper, MainScraper, TeamScraper, GameScraper,
ChampionshipScraper.
"""

import json
import logging
from datetime import datetime
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
		logger_disable: bool -- a flag to enable or disable logging (default
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

	Methods: status, seasons.
	"""
	def __init__(self, name: str, endpoint: str, base_url: str=BASE_URL,
				 request_retries: int=5, cache_ttl: int=300,
				 logger_disable: bool=False):
		"""ChampionshipScraper's constructor.
	
		Parameters @CoreScraper
		-----------------------
		name: str -- championship name
		endpoint: str -- endpoint of the championship webpage
		"""
		super().__init__(base_url=base_url, request_retries=request_retries,
						 cache_maxsize=10, cache_ttl=cache_ttl,
						 logger_disable=logger_disable)
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

			self.logger.debug('Futpédia\'s {0} page is currently online.' \
							  .format(self.name))
			return True
		except Exception as err:
			self.logger.warning(
				'Futpédia\'s {0} page is currently not online: {1}.' \
				.format(self.name, err))
			return False

	def seasons(self, target_season: int, number_seasons: int=1) -> dict:
		"""Returns list of Futpédia's seasons of the instance's championship.

		Obs: Obtains teams from private method __scrap_seasons() and modifies
		the response so that only the teams between target_season and
		number_seasons - 1 are returned.

		Returns
		-------
		teams: list -- list with dictionaries of seasons including year,
		start_date, end_date, number_goals and number_games
		"""
		if number_seasons < 1:
			raise ValueError('The number_seasons parameter should be higher'
							 ' than 0.')

		seasons = [{'year': k, 'start_date': v['start_date'], 
					'end_date': v['end_date'],
					'number_goals': v['number_goals'],
					'number_games': v['number_games']} \
				   for k, v in self.__scrap_seasons().items()]

		# Validates chosen season
		first_year = seasons[-1]['year']
		last_year = seasons[0]['year']
		if target_season < first_year or target_season > last_year:
			raise ValueError('The target_season should be between {0} and {1}'
							 ' for this championship.' \
							 .format(first_year, last_year))

		return list(filter(
			lambda x: x['year'] >= target_season \
					  and x['year'] <= target_season + number_seasons - 1,
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
		try:
			# Fetches
			req = self.session.get(
				'{0}/campeonato/{1}'.format(self.url, self.endpoint))
			self.logger.debug(
				'Request \'{0}/campeonato{1}\' returned expected status code'
				' 200.'.format(self.url, self.endpoint))

		except Exception as err:
			self.logger.error('Futpédia is currently not online: {0}.' \
							  .format(err))
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err

		# Parses
		soup = BeautifulSoup(req.content, 'html.parser')
		raw_seasons = soup.find(
			'script',
			string=lambda s: s is not None and s.find('static_host') != -1
		)

		if raw_seasons is None:
			raise ScrapediaParseError(
				'Expected <script> tag with \'static_host\' at content,'
				' but it was not found while parsing.')

		stt = raw_seasons.string.find('{"campeonato":')
		end = raw_seasons.string.find('}]};') + 3
		raw_seasons = raw_seasons.string[stt:end]

		try:
			# Transforms
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

		except json.decoder.JSONDecodeError as err:
			self.logger.error('Fetched content could not be parsed: {0}.' \
							  .format(err))
			raise ScrapediaParseError(
				'Fetched content could not be parsed.') from err


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
		flag: bool -- if online returns True, otherwise False
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
		the response so that only the teams ids and names are returned.

		Returns
		-------
		teams: list -- list with dictionaries of teams including ids and
		names
		"""
		return [{'id': k, 'name': v['name']} \
				for k, v in self.__scrap_teams().items()]

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
				champ['name'], champ['endpoint'], base_url=self.url,
				logger_disable=self.logger.disabled)
		else:
			raise ScrapediaNotFoundError('The chosen id could not be'
										' found, use a MainScraper instance to'
										' list all championships using'
										' championships() to find the id you'
										' are looking for.')

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
		return [{'id': k, 'name': v['name']} \
				for k, v in self.__scrap_championships().items()]

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
		try:
			# Fetches
			req = self.session.get('{0}/times'.format(self.url))
			self.logger.debug(
				'Request \'{0}/times\' returned expected status code 200.' \
				.format(self.url))

		except Exception as err:
			self.logger.error('Futpédia is currently not online: {0}.' \
							  .format(err))
			raise ScrapediaRequestError(
				'Futpédia is currently not online.') from err

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
		for index, raw_team in enumerate(raw_teams):
			team = {'name': raw_team.string,
					'endpoint': raw_team.a.get('href')}
			teams[index + 1] = team

		return teams

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
		try:
			# Fetches
			req = self.session.get(self.url)
			self.logger.debug(
				'Request \'{0}\' returned expected status code 200.' \
				.format(self.url))

		except Exception as err:
			self.logger.error('Futpédia is currently not online: {0}.' \
							  .format(err))
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
				'Expected <script type="text/javascript"'
				' language="javascript" charset="utf-8"> tag, but it'
				' was not found while parsing.')

		stt = raw_champs.string.find('[{')
		end = raw_champs.string.find('}]') + 2
		raw_champs = raw_champs.string[stt:end]

		try:
			# Transforms
			champs = {}
			for index, raw_champ in enumerate(json.loads(raw_champs)):
				champ = {'name': raw_champ.get('nome'),
						 'endpoint': '/{0}'.format(raw_champ.get('slug'))}
				champs[index + 1] = champ

			return champs

		except json.decoder.JSONDecodeError as err:
			self.logger.error('Fetched content could not be parsed: {0}.' \
							  .format(err))
			raise ScrapediaParseError(
				'Fetched content could not be parsed.') from err
