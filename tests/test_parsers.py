"""Collection of unit tests for scrapedia.parsers module's classes and
functions.

Classes: ChampionshipParserTests, SeasonParserTests, TeamParserTests
"""

import unittest
import collections

import scrapedia.models as models
import scrapedia.parsers as parsers
from scrapedia.errors import ScrapediaParseError


MOCK_NO_RAW_DATA = 'none'

MOCK_CHAMP_RAW_DATA = (
	'[{"nome":"Campeonato Brasileiro",'
	'"slug":"campeonato-brasileiro","tipo":"campeonato"}]'
)

MOCK_SEASON_RAW_DATA = (
	'{"campeonato":{"slug":"copa-confederacoes","id":154,'
	'"nome":"Copa das Confederações"},"edicoes":[{"edicao":'
	'{"data_fim":"2013-06-30","nome":"Copa das Confederações 2013",'
	'"slug_editorial":"2013","id":1230,"data_inicio":"2013-06-15",'
	'"slug":"copa-confederacoes-2013","campeonato_id":154},'
	'"campeoes":[2318],"gols":68,"jogos_realizados":16,"jogos":16}]}'
)

MockTag = collections.namedtuple('MockTag', ['string', 'a'])
MOCK_TEAM_RAW_DATA = [
	MockTag('AA Colatina', {'href': '/colatina'}),
	MockTag('AA Internacional', {'href': '/aa-internacional'})
]


class ChampionshipParserTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a ChampionshipParser and
	its methods.

	Tests: test_parse
	"""
	def test_parse(self):
		"""Steps:
		1 - Instantiates a ChampionshipParser
		2 - Uses parse(MOCK_CHAMP_RAW_DATA) and verify response
		3 - Uses search(MOCK_NO_RAW_DATA) and verify if it raises error 
		"""
		parser = parsers.ChampionshipParser()
		res = parser.parse(MOCK_CHAMP_RAW_DATA)
		self.assertIsInstance(res, list)
		self.assertEqual(len(res), 1)
		self.assertEqual(type(res[0]).__name__, 'Championship')

		self.assertEqual(res[0].uid, 0)
		self.assertEqual(res[0].name, 'Campeonato Brasileiro')
		self.assertEqual(res[0].path, '/campeonato/campeonato-brasileiro')

		with self.assertRaises(ScrapediaParseError):
			parser.parse(MOCK_NO_RAW_DATA)


class SeasonParserTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a SeasonParser and its
	methods.

	Tests: test_parse
	"""
	def test_parse(self):
		"""Steps:
		1 - Instantiates a SeasonParser
		2 - Uses parse(MOCK_SEASON_RAW_DATA) and verify response
		3 - Uses search(MOCK_NO_RAW_DATA) and verify if it raises error 
		"""
		parser = parsers.SeasonParser()
		res = parser.parse(MOCK_SEASON_RAW_DATA)
		self.assertIsInstance(res, list)
		self.assertEqual(len(res), 1)
		self.assertEqual(type(res[0]).__name__, 'Season')

		self.assertEqual(res[0].year, 2013)
		self.assertEqual(res[0].start_date, 1371265200000)
		self.assertEqual(res[0].end_date, 1372561200000)
		self.assertEqual(res[0].number_goals, 68)
		self.assertEqual(res[0].number_games, 16)
		self.assertEqual(res[0].path, '/2013')

		with self.assertRaises(ScrapediaParseError):
			parser.parse(MOCK_NO_RAW_DATA)


class TeamParserTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a TeamParser and its
	methods.

	Tests: test_parse
	"""
	def test_parse(self):
		"""Steps:
		1 - Instantiates a TeamParser
		2 - Uses parse(MOCK_TEAM_RAW_DATA) and verify response
		3 - Uses search(MOCK_NO_RAW_DATA) and verify if it raises error 
		"""
		parser = parsers.TeamParser()
		res = parser.parse(MOCK_TEAM_RAW_DATA)
		self.assertIsInstance(res, list)
		self.assertEqual(len(res), 2)
		self.assertEqual(type(res[0]).__name__, 'Team')
		self.assertEqual(type(res[1]).__name__, 'Team')

		self.assertEqual(res[0].uid, 0)
		self.assertEqual(res[0].name, 'AA Colatina')
		self.assertEqual(res[0].path, '/colatina')

		self.assertEqual(res[1].uid, 1)
		self.assertEqual(res[1].name, 'AA Internacional')
		self.assertEqual(res[1].path, '/aa-internacional')

		with self.assertRaises(ScrapediaParseError):
			parser.parse(MOCK_NO_RAW_DATA)


if __name__ == 'main':
	unittest.main()
