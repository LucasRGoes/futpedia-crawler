"""Scrapedia's seekers are the pipeline's stage where the requested
information is analyzed and reduced so that only the interesting portions
remain and are returned.

ABCs: Parser

Classes: ChampionshipParser, SeasonParser, TeamParser
"""

import abc
import json

from .errors import ScrapediaParseError
from .models import Championship, Season, Team


class Parser(abc.ABC):
	"""An abstract base class for other parser classes to implement.

	Methods: parse
	"""
	@abc.abstractmethod
	def parse(self, raw_data: str) -> list:
		"""Parses raw data into a list of models.

		Parameters
		----------
		raw_data: str -- the raw data to be parsed

		Returns
		-------
		models: list -- the list with the data of interest
		"""
		pass


class ChampionshipParser(Parser):
	"""A parser class specialized in parsing raw data concerning championships.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		pass

	def parse(self, raw_data: str) -> list:
		"""Parses raw data into a list of Championship models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			parsed_data = list(filter(
				lambda x: x.get('nome') != 'Brasileiro Unificado',
				json.loads(raw_data)
			))

			for idx, data in enumerate(parsed_data):
				champ = Championship(idx, data.get('nome'),
									 '/{0}'.format(data.get('slug')))
				models.append(champ)

			return models

		except Exception as err:
			raise ScrapediaParseError(
				'The championships raw data could not be parsed: {0}' \
				.format(err)
			)
