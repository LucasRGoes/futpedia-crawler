"""Collection of unit tests for scrapedia.scrapers module's classes and
functions.

Classes: RootScraperTests, ChampionshipScraperTests, SeasonsScraperTests
"""

import unittest

import pandas as pd

import scrapedia.scrapers as scrapers 


class RootScraperTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a RootScraper and its
	methods.

	Tests: test_championship, test_championships, test_teams
	"""
	def setUp(self):
		"""Instantiates a RootScraper."""
		self.scraper = scrapers.RootScraper()

	def test_championship(self):
		"""Steps:
		1 - Uses championship(0) and verify response
		2 - Uses championship(-1) and verify if it raises error
		3 - Uses championship(999) and verify if it raises error
		"""
		champ_scraper = self.scraper.championship(0)
		self.assertIsInstance(champ_scraper, scrapers.ChampionshipScraper)

		with self.assertRaises(ValueError):
			self.scraper.championship(-1)

		with self.assertRaises(ValueError):
			self.scraper.championship(999)

	def test_championships(self):
		"""Steps:
		1 - Uses championships() and verify response
		"""
		validate = lambda x: x.get('name') is not None \
							 and isinstance(x['name'], str) \
							 and x.get('path') is not None \
							 and isinstance(x['path'], str)

		champs = self.scraper.championships()

		self.assertIsInstance(champs, pd.DataFrame)
		self.assertIn('name', champs.columns)
		self.assertIn('path', champs.columns)
		self.assertTrue(all(validate(row) for i, row in champs.iterrows()))

	def test_teams(self):
		"""Steps:
		1 - Instantiates a RootScraper
		2 - Uses teams() and verify response
		"""
		validate = lambda x: x.get('name') is not None \
							 and isinstance(x['name'], str) \
							 and x.get('path') is not None \
							 and isinstance(x['path'], str)

		teams = self.scraper.teams()

		self.assertIsInstance(teams, pd.DataFrame)
		self.assertIn('name', teams.columns)
		self.assertIn('path', teams.columns)
		self.assertTrue(all(validate(row) for i, row in teams.iterrows()))


class ChampionshipScraperTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a ChampionshipScraper and
	its methods.

	Tests: test_season, test_seasons
	"""
	def setUp(self):
		"""Instantiates a RootScraper."""
		self.scraper = scrapers.RootScraper()

	def test_season(self):
		"""Steps:
		1 - Uses season(2010) and verify response
		2 - Uses season(-1) and verify if it raises error
		3 - Uses season(999) and verify if it raises error
		"""
		champ_scraper = self.scraper.championship(0)
		season_scraper = champ_scraper.season(2010)
		self.assertIsInstance(season_scraper, scrapers.SeasonScraper)

		with self.assertRaises(ValueError):
			champ_scraper.season(-1)

		with self.assertRaises(ValueError):
			champ_scraper.season(999)

	def test_seasons(self):
		"""Steps:
		1 - Instantiates a ChampionshipScraper for 10% of the championships
		2 - Uses seasons() on each and verify response
		"""
		validate = lambda x: x.get('start_date') is not None \
							 and isinstance(x['start_date'], float) \
							 and x.get('end_date') is not None \
							 and isinstance(x['end_date'], float) \
							 and x.get('number_goals') is not None \
							 and isinstance(x['number_goals'], int) \
							 and x.get('number_games') is not None \
							 and isinstance(x['number_games'], int) \
							 and x.get('path') is not None \
							 and isinstance(x['path'], str)

		for i, row in self.scraper.championships().sample(frac=.1).iterrows():
			with self.subTest(i=row.get('name')):
				champ_scraper = self.scraper.championship(i)
				seasons = champ_scraper.seasons()

				self.assertIsInstance(seasons, pd.DataFrame)
				self.assertIn('start_date', seasons.columns)
				self.assertIn('end_date', seasons.columns)
				self.assertIn('number_goals', seasons.columns)
				self.assertIn('number_games', seasons.columns)
				self.assertIn('path', seasons.columns)
				self.assertTrue(all(
					validate(row) for i, row in seasons.iterrows()))


class SeasonsScraperTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a SeasonScraper and its
	methods.

	Tests: test_game, test_games
	"""
	def setUp(self):
		"""Instantiates a RootScraper."""
		self.scraper = scrapers.RootScraper()

	def test_game(self):
		"""Steps:
		1 - Instantiates a ChampionshipScraper for 10% of the championships
		2 - Instantiates using each ChampionshipScraper a SeasonScraper for
		10% of the seasons
		2 - Uses games() on each and verify response
		"""
		pass
		# for i, row_c in self.scraper.championships().sample(frac=.1) \
		# 											.iterrows():
		# 	champ_scraper = self.scraper.championship(i)
		# 	for j, row_s in champ_scraper.seasons().sample(frac=.1).iterrows():
		# 		with self.subTest(i=(row_c.get('name'), j)):
		# 			season_scraper = champ_scraper.season(j)

	def test_games(self):
		pass


if __name__ == 'main':
	unittest.main()
