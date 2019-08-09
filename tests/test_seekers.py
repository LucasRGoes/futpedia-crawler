"""Collection of unit tests for scrapedia.seekers module's classes and
functions.

Classes: ChampionshipSeekerTests, SeasonSeekerTests, TeamSeekerTests
"""

import unittest

import scrapedia.seekers as seekers
from scrapedia.errors import ScrapediaSearchError


MOCK_NO_CONTENT = '<script>none</script>'.encode('utf-8')

MOCK_CHAMP_CONTENT = (
	'<script type="text/javascript" language="javascript" charset="utf-8">'
	'[{"nome":"Campeonato Brasileiro","slug":"campeonato-brasileiro",'
	'"tipo":"campeonato"}]</script>'.encode('utf-8')
)

MOCK_SEASON_CONTENT = (
	'<script>static_host = "http://s.glbimg.com/es/fp/1438373334";'
	'dados = {"campeonato":{"slug":"copa-confederacoes","id":154,'
	'"nome":"Copa das Confedera\u00e7\u00f5es"},"edicoes":[{"edicao":{'
	'"data_fim":"2013-06-30","nome":"Copa das Confedera\u00e7\u00f5es'
	' 2013","slug_editorial":"2013","id":1230,"data_inicio":"2013-06-15",'
	'"slug":"copa-confederacoes-2013","campeonato_id":154},"campeoes":[2318],'
	'"gols":68,"jogos_realizados":16,"jogos":16}]};</script>'.encode('utf-8')
)

MOCK_TEAM_CONTENT = (
	'<ol class="primeiro">'
	'<li itemprop="itemListElement"><a href="/colatina">AA Colatina</a></li>'
	'<li itemprop="itemListElement"><a href="/aa-internacional">AA'
	' Internacional</a></li></ol>'.encode('utf-8')
)


class ChampionshipSeekerTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a ChampionshipSeeker and
	its methods.

	Tests: test_search
	"""
	def test_search(self):
		"""Steps:
		1 - Instantiates a ChampionshipSeeker
		2 - Uses search(MOCK_CHAMP_CONTENT) and verify response
		3 - Uses search(MOCK_NO_CONTENT) and verify if it raises error 
		"""
		seeker = seekers.ChampionshipSeeker()
		res = seeker.search(MOCK_CHAMP_CONTENT)
		self.assertEqual(
			res, 
			'[{"nome":"Campeonato Brasileiro","slug":"campeonato-brasileiro",'
			'"tipo":"campeonato"}]'
		)

		with self.assertRaises(ScrapediaSearchError):
			seeker.search(MOCK_NO_CONTENT)


class SeasonSeekerTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a SeasonSeeker and its
	methods.

	Tests: test_search
	"""
	def test_search(self):
		"""Steps:
		1 - Instantiates a SeasonSeeker
		2 - Uses search(MOCK_SEASON_CONTENT) and verify response
		3 - Uses search(MOCK_NO_CONTENT) and verify if it raises error 
		"""
		seeker = seekers.SeasonSeeker()
		res = seeker.search(MOCK_SEASON_CONTENT)
		self.assertEqual(
			res, 
			'{"campeonato":{"slug":"copa-confederacoes","id":154,'
			'"nome":"Copa das Confederações"},"edicoes":[{"edicao":'
			'{"data_fim":"2013-06-30","nome":"Copa das Confederações 2013",'
			'"slug_editorial":"2013","id":1230,"data_inicio":"2013-06-15",'
			'"slug":"copa-confederacoes-2013","campeonato_id":154},'
			'"campeoes":[2318],"gols":68,"jogos_realizados":16,"jogos":16}]}'
		)

		with self.assertRaises(ScrapediaSearchError):
			seeker.search(MOCK_NO_CONTENT)


class TeamSeekerTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a TeamSeeker and its
	methods.

	Tests: test_search
	"""
	def test_search(self):
		"""Steps:
		1 - Instantiates a TeamSeeker
		2 - Uses search(MOCK_TEAM_CONTENT) and verify response
		3 - Uses search(MOCK_NO_CONTENT) and verify if it raises error 
		"""
		seeker = seekers.TeamSeeker()
		res = seeker.search(MOCK_TEAM_CONTENT)
		self.assertIsInstance(res, list)
		self.assertEqual(len(res), 2)

		with self.assertRaises(ScrapediaSearchError):
			seeker.search(MOCK_NO_CONTENT)


if __name__ == 'main':
	unittest.main()
