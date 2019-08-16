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

	def __parse_bracket(self, raw_data, extra, idx: int=0) -> list:
		"""Parses raw data that was extracted from a bracket structure.

		Parameters
		----------
		raw_data -- the raw data to be parsed
		extra -- extra data to help with the parsing of the raw data
		idx: int -- the starting point of the games' indexes (default 0)

		Returns: list -- list with models built using the raw data
		"""
		models = []

		phases = []
		extra = [phase.string for phase in extra.find_all(name='h3')]
		if 'Oitavas de final' in extra:
			phases.extend(['best_of_16'] * 8)
		if 'Quartas de final' in extra:
			phases.extend(['quarterfinals'] * 4)
		if 'Semifinal' in extra:
			phases.extend(['semifinals'] * 2)
		if 'Final' in extra:
			phases.append('finals')

		for games in raw_data:
			first_team = games.find(name='div', class_='mandante') \
							  .get_text().strip()
			second_team = games.find(name='div', class_='visitante') \
							   .get_text().strip()
			phase = phases.pop(0)

			# Game 1.
			game_1 = games.find(name='div', class_='jogo_ida dados')
			home_team = first_team
			away_team = second_team

			home_goals = game_1.find(
				name='span', class_='placar primeiro font-face').string
			away_goals = game_1.find(
				name='span', class_='placar font-face').string

			stadium = game_1.find(name='div', class_='content').strong.string
			round_ = None
			path = game_1.a.get('href')

			date = game_1.find(name='div', class_='content').get_text() \
						 .split(' ')
			date = datetime.strptime(
				'{0} {1}'.format(date[1], date[3]), '%d/%m/%Y %Hh%M')
			date = time.mktime(date.timetuple()) * 1000

			models.append(Game(
				idx, home_team, int(home_goals), int(away_goals), away_team,
				stadium, phase, round_, date, path
			))

			idx += 1

			# Game 2.
			game_2 = games.find(name='div', class_='jogo_volta dados')
			if game_2 is not None:

				home_team = second_team
				away_team = first_team

				home_goals = game_2.find(
					name='span', class_='placar font-face').string
				away_goals = game_2.find(
					name='span', class_='placar primeiro font-face').string

				stadium = game_2.find(name='div', class_='content') \
								.strong.string
				round_ = None
				path = game_2.a.get('href')

				date = game_2.find(name='div', class_='content').get_text() \
							 .split(' ')
				date = datetime.strptime(
					'{0} {1}'.format(date[1], date[3]), '%d/%m/%Y %Hh%M')
				date = time.mktime(date.timetuple()) * 1000

				models.append(Game(
					idx, home_team, int(home_goals), int(away_goals),
					away_team, stadium, phase, round_, date, path
				))

				idx += 1

			# Game 3.
			game_3 = games.find(name='div', class_='terceiro_jogo dados')
			if game_3 is not None:

				home_team = second_team
				away_team = first_team

				home_goals = game_2.find(
					name='span', class_='placar font-face').string
				away_goals = game_2.find(
					name='span', class_='placar primeiro font-face').string

				stadium = game_2.find(name='div', class_='content') \
								.strong.string
				round_ = None
				path = game_2.a.get('href')

				date = game_2.find(name='div', class_='content').get_text() \
							 .split(' ')
				date = datetime.strptime(
					'{0} {1}'.format(date[1], date[3]), '%d/%m/%Y %Hh%M')
				date = time.mktime(date.timetuple()) * 1000

				models.append(Game(
					idx, home_team, int(home_goals), int(away_goals),
					away_team, stadium, phase, round_, date, path
				))

				idx += 1

		return models

	def __parse_list(self, raw_data, extra, idx: int=0) -> list:
		"""Parses raw data that was extracted from a list structure.

		Parameters
		----------
		raw_data -- the raw data to be parsed
		extra -- extra data to help with the parsing of the raw data
		idx: int -- the starting point of the games' indexes (default 0)

		Returns: list -- list with models built using the raw data
		"""
		models = []

		games = json.loads(raw_data)
		teams = json.loads(extra)
		games.reverse()

		for game in games:

			home_team = teams[str(game.get('mand'))].get('nome_popular')
			away_team = teams[str(game.get('vis'))].get('nome_popular')

			home_goals = game.get('golm')
			away_goals = game.get('golv')

			stadium = game.get('sede')
			phase = 'first_phase'
			round_ = game.get('rod')
			path = game.get('url')

			date = datetime.strptime(
				'{0} {1}'.format(game.get('dt'), game.get('hr')),
				'%d/%m/%Y %Hh%M'
			)
			date = time.mktime(date.timetuple()) * 1000

			models.append(Game(
				idx, home_team, home_goals, away_goals, away_team, stadium,
				phase, round_, date, path
			))

			idx += 1

		return models

	def __parse_table(self, raw_data, idx: int=0) -> list:
		"""Parses raw data that was extracted from a table structure.

		Parameters
		----------
		raw_data -- the raw data to be parsed
		idx: int -- the starting point of the games' indexes (default 0)

		Returns: list -- list with models built using the raw data
		"""
		models = []

		for game in raw_data:

			home_team = game.find(name='div', class_='time mandante') \
							.meta.get('content')
			away_team = game.find(name='div', class_='time visitante') \
							.meta.get('content')

			home_goals = game.find(name='span', class_='mandante font-face') \
							 .string
			away_goals = game.find(name='span', class_='visitante font-face') \
							 .string

			stadium = game.find(name='span', attrs={'itemprop': 'name'}).string
			phase = 'first_phase'
			round_ = game.get('data-rodada')
			path = game.a.get('href')

			hour = game.find(name='span', class_='horario').string
			if hour is None:
				date = datetime.strptime(game.time.get('datetime'), '%d/%m/%Y')

			else:
				date = datetime.strptime(
					'{0} {1}'.format(game.time.get('datetime'), hour),
					'%d/%m/%Y %Hh%M'
				)
			date = time.mktime(date.timetuple()) * 1000

			models.append(Game(
				idx, home_team, int(home_goals), int(away_goals), away_team,
				stadium, phase, round_, date, path
			))

			idx += 1

		return models

	def parse(self, raw_data: dict) -> tuple:
		"""Parses raw data into a tuple of Game models.

		Parameters @Parser
		Returns @Parser
		"""
		try:

			if raw_data.get('type') == 'bracket_table':
				table_models = self.__parse_table(raw_data['raw']['table'])
				bracket_models = self.__parse_bracket(
					raw_data['raw']['bracket'],
					raw_data['extra']['bracket'],
					idx=len(table_models)
				)

				models = table_models + bracket_models

			elif raw_data.get('type') == 'list':
				models = self.__parse_list(raw_data['raw'], raw_data['extra'])

			elif raw_data.get('type') == 'table':
				models = self.__parse_table(raw_data['raw'])

			return tuple(models)

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
