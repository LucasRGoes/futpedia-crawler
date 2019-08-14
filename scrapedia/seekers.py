"""The seekers module holds all classes and functions related to searching specific excerpts of text on a web page's HTML file.

ABCs: Seeker

Classes: ChampionshipSeeker, GameSeeker, SeasonSeeker, TeamSeeker
"""

import abc

from bs4 import BeautifulSoup

from .errors import ScrapediaSearchError


class Seeker(abc.ABC):
	"""An abstract base class for other seeker classes to implement.

	Methods: search
	"""
	@abc.abstractmethod
	def search(self, content: bytes) -> dict:
		"""Searches web page's content for excerpts that hold data of interest.

		Parameters
		----------
		content: bytes -- the raw HTML text to be searched

		Returns: dict -- the raw data that holds the information to be
		extracted
		"""
		pass


class ChampionshipSeeker(Seeker):
	"""A seeker class specialized in finding data concerning championships.

	Extends: Seeker

	Methods: search
	"""
	def __init__(self):
		"""ChampionshipSeeker's constructor."""
		pass

	def search(self, content: bytes) -> dict:
		"""Search web page's content for raw data concerning championships.

		Parameters @Seeker
		Returns @Seeker
		"""
		soup = BeautifulSoup(content, 'html.parser')
		raw_data = soup.find(name='script', attrs={'type': 'text/javascript',
												   'language': 'javascript',
												   'charset': 'utf-8'})
		if raw_data is None:
			raise ScrapediaSearchError('The expected championships raw data'
									   ' could not be found.')

		stt = raw_data.string.find('[{')
		end = raw_data.string.find('}]') + 2

		return {'content': raw_data.string[stt:end]}


class GameSeeker(Seeker):
	"""A seeker class specialized in finding data concerning a season's games.

	Extends: Seeker

	Methods: search
	"""
	def __init__(self):
		"""GameSeeker's constructor."""
		pass

	def __search_list(self, soup) -> dict:
		"""Searches games within the given soup organized with a list
		structure.

		Returns -- the raw data of the games obtained from the soup
		"""
		raw_data = soup.find(
			'script',
			string=lambda s: s is not None and s.find('JOGOS:') != -1
		)

		stt = raw_data.string.find('JOGOS:') + 7
		end = raw_data.string.find('}],') + 2
		raw_games = raw_data.string[stt:end]

		stt = raw_data.string.find('EQUIPES:') + 9
		end = raw_data.string.find('}},') + 2
		raw_teams = raw_data.string[stt:end]

		return {'raw_games': raw_games, 'raw_teams': raw_teams}

	def search(self, content: bytes) -> dict:
		"""Searches web page's content for raw data concerning a season's
		games.

		Parameters @Seeker
		Returns @Seeker
		"""
		soup = BeautifulSoup(content, 'html.parser')

		if soup.find(name='table', id='tabela-jogos'):
			# Used on Campeonato Brasileiro, seasons 2016 and 2017.
			raw_data = self.__search_list(soup)

		elif soup.find(name='div', id='lista-jogos'):
			# Used on Campeonato Brasileiro, seasons 2003 through 2015.
			raw_data = self.__search_table(soup)

		else:
			raw_data = None

		# Searches for HTML with tables
		# raw_games = soup.find_all(name='li',
		# class_='lista-classificacao-jogo')

		if raw_data is None:
			raise ScrapediaSearchError('The expected season\'s games raw data'
									  ' could not be found.')

		return raw_data


class SeasonSeeker(Seeker):
	"""A seeker class specialized in finding data concerning a championship's
	seasons.

	Extends: Seeker

	Methods: search
	"""
	def __init__(self):
		"""SeasonSeeker's constructor."""
		pass

	def search(self, content: bytes) -> dict:
		"""Search web page's content for raw data concerning a championship's
		seasons.

		Parameters @Seeker
		Returns @Seeker
		"""
		soup = BeautifulSoup(content, 'html.parser')
		raw_data = soup.find(
			'script',
			string=lambda s: s is not None and s.find('static_host') != -1
		)

		if raw_data is None:
			raise ScrapediaSearchError('The expected championship\'s seasons'
									   ' raw data could not be found.')

		stt = raw_data.string.find('{"campeonato":')
		end = raw_data.string.find('}]};') + 3

		return {'content': raw_data.string[stt:end]}


class TeamSeeker(Seeker):
	"""A seeker class specialized in finding data concerning teams.

	Extends: Seeker

	Methods: search
	"""
	def __init__(self):
		"""TeamSeeker's constructor."""
		pass

	def search(self, content: bytes) -> dict:
		"""Search web page's content for raw data concerning teams.

		Parameters @Seeker
		Returns @Seeker
		"""
		soup = BeautifulSoup(content, 'html.parser')
		raw_data = soup.find_all(name='li',
								 attrs={'itemprop': 'itemListElement'})

		if not len(raw_data) > 0:
			raise ScrapediaSearchError('The expected teams raw data could not'
									   ' be found.')

		return {'content': raw_data}
