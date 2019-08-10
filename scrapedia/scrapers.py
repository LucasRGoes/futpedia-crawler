"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: Scraper, RootScraper
"""

from .


class Scraper(object):
	"""Core of all of Scrapedia's scrapers. Includes caching and logging
	functionalities.

	Methods: __enter__, __exit__
	"""
	def __init__(self, request_retries: int=10, cache_maxsize: int=10,
				 cache_ttl: int=300):
		"""Scraper's constructor.
		
		Parameters
		----------
		request_retries: int -- number of maximum retries of requests on
		cases where the status code is in a given set (default 10)
		cache_maxsize: int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl: int -- time to live in seconds for internal caching of
		data (default 300)
		"""
		self.request_retries = request_retries
		


class RootScraper(CoreScraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: status, championship, teams, championships
	"""
	def __init__(self, request_retries: int=10, cache_ttl: int=300):
		"""MainScraper's constructor. Builds a pipeline used to fetch
		Futpédia's data.
	
		Parameters @CoreScraper
		"""
		super().__init__(request_retries=request_retries, cache_maxsize=2,
						 cache_ttl=cache_ttl)



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

