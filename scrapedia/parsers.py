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
from .models import Championship, Game, Season, Team


class Parser(abc.ABC):
	"""An abstract base class for other parser classes to implement.

	Methods: parse
	"""
	@abc.abstractmethod
	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of models.

		Parameters
		----------
		raw_data: dict -- raw data to be parsed

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

	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of Championship models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			parsed_data = list(filter(
				lambda x: x.get('nome') != 'Brasileiro Unificado',
				json.loads(raw_data.get('content'))
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

	def __round_robin_playoffs(self, raw_data: dict) -> tuple:
		"""Parses raw data that was extracted from a table plus a bracket
		structure.

		Returns: tuple -- tuple with models built with the data
		"""
		models = []

		round_robin = raw_data.get('content').get('round_robin')
		playoffs = raw_data.get('content').get('playoffs')

		# Takes care of round-robin games.
		for idx, raw_game in enumerate(round_robin):

			home_team = raw_game.find(name='div', class_='time mandante') \
								.meta.get('content')
			away_team = raw_game.find(name='div', class_='time visitante') \
								.meta.get('content')
			home_goals = int(raw_game.find(
				name='span', class_='mandante font-face').string)
			away_goals = int(raw_game.find(
				name='span', class_='visitante font-face').string)

			stadium = raw_game.find(
				name='span', attrs={'itemprop': 'name'}).string
			phase = 'first_phase'
			round_ = raw_game.get('data-rodada')
			path = raw_game.a.get('href')

			date = datetime.strptime(raw_game.time.get('datetime'), '%d/%m/%Y')
			date = time.mktime(date.timetuple()) * 1000

			game = Game(idx, home_team, home_goals, away_goals, away_team,
					    stadium, phase, round_, date, path)
			models.append(game)

		# Takes care of playoffs.
		for raw_games in playoffs:
			first_team = raw_games.find(name='div', class_='mandante') \
								  .strong.string
			second_team = raw_games.find(name='div', class_='visitante') \
								   .strong.string

			# Game 1.
			game_1 = raw_games.find(name='div', class_='jogo_ida dados')

			home_team = first_team
			away_team = second_team
			home_goals = int(game_1.find(
				name='span', class_='placar primeiro font-face').string)
			away_goals = int(game_1.find(
				name='span', class_='placar font-face').string)

			stadium = game_1.find(name='div', class_='content').strong.string
			phase = None
			round_ = None
			path = game_1.a.get('href')

			date = game_1.find(name='div', class_='content').string

			idx = idx + 1
			game = Game(idx, home_team, home_goals, away_goals, away_team,
					    stadium, phase, round_, date, path)
			models.append(game)

			# Game 2.
			game_2 = raw_games.find(name='div', class_='jogo_volta dados')

			home_team = second_team
			away_team = first_team
			home_goals = int(game_2.find(
				name='span', class_='placar font-face').string)
			away_goals = int(game_2.find(
				name='span', class_='placar primeiro font-face').string)

			stadium = game_2.find(name='div', class_='content').strong.string
			phase = None
			round_ = None
			path = game_2.a.get('href')

			date = game_2.find(name='div', class_='content').string

			idx = idx + 1
			game = Game(idx, home_team, home_goals, away_goals, away_team,
					    stadium, phase, round_, date, path)
			models.append(game)


		# Takes care of playoffs.
		# phases = []
		# qtty = (len(playoffs) - 1) / 2
		# if qtty >= 1:
		# 	phases.append('finals')
		# if qtty >= 2:
		# 	phases.append(['semifinals'] * 2)
		# if qtty >= 3:
		# 	phases.append(['quarterfinals'] * 4)
		# if qtty >= 4:
		# 	phases.append(['round_of_sixteen'] * 8)
		# phases.reverse()

		return tuple(models)

	def __round_robin_table(self, raw_data: dict) -> tuple:
		"""Parses raw data that was extracted from a table structure.

		Returns: tuple -- tuple with models built with the data
		"""
		models = []

		for idx, raw_game in enumerate(raw_data.get('content')):

			home_team = raw_game.find(name='div', class_='time mandante') \
								.meta.get('content')
			away_team = raw_game.find(name='div', class_='time visitante') \
								.meta.get('content')
			home_goals = int(raw_game.find(
				name='span', class_='mandante font-face').string)
			away_goals = int(raw_game.find(
				name='span', class_='visitante font-face').string)

			stadium = raw_game.find(
				name='span', attrs={'itemprop': 'name'}).string
			phase = 'first_phase'
			round_ = raw_game.get('data-rodada')
			path = raw_game.a.get('href')

			date = datetime.strptime(
				'{0} {1}'.format(
					raw_game.time.get('datetime'),
					raw_game.find(name='span', class_='horario').string
				),
				'%d/%m/%Y %Hh%M'
			)
			date = time.mktime(date.timetuple()) * 1000

			game = Game(idx, home_team, home_goals, away_goals, away_team,
					    stadium, phase, round_, date, path)
			models.append(game)

		return tuple(models)

	def __round_robin_list(self, raw_data: dict) -> tuple:
		"""Parses raw data that was extracted from a list structure.

		Returns: tuple -- tuple with models built with the data
		"""
		models = []

		raw_games = json.loads(raw_data.get('content').get('games'))
		raw_teams = json.loads(raw_data.get('content').get('teams'))

		for idx, raw_game in enumerate(raw_games):

			home_team = raw_teams[str(raw_game['mand'])]['nome_popular']
			away_team = raw_teams[str(raw_game['vis'])]['nome_popular']

			home_goals = raw_game.get('golm')
			away_goals = raw_game.get('golv')

			stadium = raw_game.get('sede')
			phase = 'first_phase'
			round_ = raw_game.get('rod')
			path = raw_game.get('url')

			date = datetime.strptime(
				'{0} {1}'.format(raw_game.get('dt'), raw_game.get('hr')),
				'%d/%m/%Y %Hh%M'
			)
			date = time.mktime(date.timetuple()) * 1000

			game = Game(idx, home_team, home_goals, away_goals, away_team,
					    stadium, phase, round_, date, path)
			models.append(game)

		return tuple(models)

	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of Game models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			if raw_data.get('meta').get('type') == 'rr_playoffs':
				return self.__round_robin_playoffs(raw_data)

			elif raw_data.get('meta').get('type') == 'rr_table':
				return self.__round_robin_table(raw_data)

			elif raw_data.get('meta').get('type') == 'rr_list':
				return self.__round_robin_list(raw_data)

		except Exception as err:
			raise ScrapediaParseError(
				'The teams raw data could not be parsed: {0}'.format(err))


class SeasonParser(Parser):
	"""A parser class specialized in parsing raw data concerning a
	championship's seasons.

	Extends: Parser

	Methods: parse
	"""
	def __init__(self):
		"""SeasonParser's constructor."""
		pass

	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of Season models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			for raw_season \
				in json.loads(raw_data.get('content')).get('edicoes'):

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

	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of Team models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			models = []

			for idx, raw_team in enumerate(raw_data.get('content')):
				team = Team(idx, raw_team.string, raw_team.a.get('href'))
				models.append(team)

			return tuple(models)

		except Exception as err:
			raise ScrapediaParseError(
				'The teams raw data could not be parsed: {0}'.format(err))
