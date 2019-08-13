"""The parsers module holds all classes and functions related to parsing raw
data and creating models with the information extracted from them.

ABCs: Parser

Classes: ChampionshipParser, GameParser, SeasonParser, TeamParser
"""

import abc
import json
import time
from datetime import datetime

from .errors import ScrapediaParseError
from .models import Championship, Season, Team


class Parser(abc.ABC):
	"""An abstract base class for other parser classes to implement.

	Methods: parse
	"""
	@abc.abstractmethod
	def parse(self, raw_data: str) -> tuple:
		"""Parses raw data into a tuple of models.

		Parameters
		----------
		raw_data: str -- raw data to be parsed

		Returns: tuple -- tuple with the information of interest
		"""
		pass


class ChampionshipParser(Parser):
	"""A parser class specialized in parsing raw data concerning championships.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		"""ChampionshipParser's constructor."""
		pass

	def parse(self, raw_data: str) -> tuple:
		"""Parses raw data into a tuple of Championship models.

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
				champ = Championship(
					idx, data.get('nome'), 
					'/campeonato/{0}'.format(data.get('slug'))
				)
				models.append(champ)

			return tuple(models)

		except Exception as err:
			raise ScrapediaParseError(
				'The championships raw data could not be parsed: {0}' \
				.format(err)
			)


class GameParser(Parser):
	"""A parser class specialized in parsing raw data concerning games.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		"""GameParser's constructor."""
		pass

	def parse(self, raw_data: str) -> tuple:
		"""Parses raw data into a tuple of Game models.

		Parameters @Parser
		Returns @Parser
		"""
		return (Game(1), )


class SeasonParser(Parser):
	"""A parser class specialized in parsing raw data concerning a
	championship's seasons.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		"""SeasonParser's constructor."""
		pass

	def parse(self, raw_data: str) -> tuple:
		"""Parses raw data into a tuple of Season models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			for raw_season in json.loads(raw_data).get('edicoes'):

				start_date = datetime.strptime(
					raw_season.get('edicao').get('data_inicio'), '%Y-%m-%d')
				end_date = datetime.strptime(
					raw_season.get('edicao').get('data_fim'), '%Y-%m-%d')
				number_goals = raw_season.get('gols')
				number_games = raw_season.get('jogos')
				path = '/{0}'.format(raw_season.get('edicao') \
											   .get('slug_editorial'))

				year = start_date.year
				start_date = time.mktime(start_date.timetuple()) * 1000
				end_date = time.mktime(end_date.timetuple()) * 1000

				season = Season(year, start_date, end_date, number_goals,
								number_games, path)

				models.append(season)

			return tuple(models)

		except Exception as err:
			raise ScrapediaParseError(
				'The championship\'s seasons raw data could not be'
				' parsed: {0}'.format(err)
			)


class TeamParser(Parser):
	"""A parser class specialized in parsing raw data concerning teams.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		"""TeamParser's constructor."""
		pass

	def parse(self, raw_data: list) -> tuple:
		"""Parses raw data into a tuple of Team models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			for idx, raw_team in enumerate(raw_data):
				team = Team(idx, raw_team.string, raw_team.a.get('href'))
				models.append(team)

			return tuple(models)

		except Exception as err:
			raise ScrapediaParseError(
				'The teams raw data could not be parsed: {0}'.format(err))
