"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: Scraper, RootScraper
"""

from .pipeline import DataStructure, PipelineFactory


class Scraper(object):
	"""Core of all of Scrapedia's scrapers."""
	def __init__(self, structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""Scraper's constructor. Builds a pipeline factory for its subclasses
		usage.
		
		Parameters
		----------
		structure: DataStructure -- the data structure built at the end of the
		pipeline (default DataStructure.DATA_FRAME)
		retry_limit: int -- number of maximum retrying of requests on
		cases where the status code is in a given set (default 10)
		backoff_factor: int -- the number in seconds that serves as the wait
		time between failed requests, getting bigger on each failure
		(default 1)
		cache_maxsize: int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl: int -- time to live in seconds for internal caching of
		data (default 300)
		"""
		self._pipeline_factory = PipelineFactory(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)


class RootScraper(Scraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: championship, championships, teams
	"""
	def __init__(self, structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""RootScraper's constructor. Builds a pipeline used to fetch
		Futpédia's data concerning teams and championships.
	
		Parameters @Scraper
		"""
		super().__init__(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)

		self._champs_pipeline = self._pipeline_factory.build('championships')
		self._teams_pipeline = self._pipeline_factory.build('teams')

	# def championship(self, id_: int) -> ChampionshipScraper:
	# 	"""Factory to return an instance of a ChampionshipScraper class based
	# 	on the chosen championship id using cached or requested data.

	# 	Parameters
	# 	----------
	# 	id_: int -- id of the championship to have a scraper built

	# 	Returns
	# 	-------
	# 	scraper: ChampionshipScraper -- scraper built targeting the chosen
	# 	championship webpage
	# 	"""
	# 	if id_ < 0:
	# 		raise ValueError(
	# 			'The \'id_\' parameter should be higher or equal to 0.')

	# 	champs = self.__scrap_championships()

	# 	try:
	# 		champ = champs.iloc[id_, :]
	# 		return ChampionshipScraper(
	# 			champ['name'], champ['endpoint'], base_url=self.url,
	# 			request_retries=self.request_retries
	# 		)

	# 	except Exception as err:
	# 		raise ScrapediaNotFoundError(
	# 			'The chosen id could not be found.') from err

	def championships(self):
		"""Returns a data structure containing Futpédia's championships and
		their metadata.

		Returns -- championship's ids, names and paths
		"""
		return self._champs_pipeline.scrap('/')

	def teams(self):
		"""Returns a data structure containing Futpédia's teams and their
		metadata.

		Returns -- teams's ids, names and paths
		"""
		return self._teams_pipeline.scrap('/times')
