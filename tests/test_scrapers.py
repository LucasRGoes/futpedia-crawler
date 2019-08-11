"""Collection of unit tests for scrapedia.scrapers module's classes and
functions.

Classes: RootScraperTests, ChampionshipScraperTests
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

	Tests: test_seasons
	"""
	def setUp(self):
		"""Instantiates a RootScraper."""
		self.scraper = scrapers.RootScraper()

	def test_seasons(self):
		"""Steps:
		1 - Instantiates a ChampionshipScraper for each championship
		2 - Uses seasons() and verify response
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

		for i in range(len(self.scraper.championships().index)):
			champ_scraper = self.scraper.championship(0)
			seasons = champ_scraper.seasons()

			self.assertIsInstance(seasons, pd.DataFrame)
			self.assertIn('start_date', seasons.columns)
			self.assertIn('end_date', seasons.columns)
			self.assertIn('number_goals', seasons.columns)
			self.assertIn('number_games', seasons.columns)
			self.assertIn('path', seasons.columns)
			self.assertTrue(all(
				validate(row) for i, row in seasons.iterrows()))


if __name__ == 'main':
	unittest.main()


# class ChampionshipScraperTests(unittest.TestCase):
# 	"""Set of unit tests for validating an instance of ChampionshipScraper.

# 	Tests: test_status, test_season, test_seasons
# 	"""
# 	def test_status(self):
# 		"""Steps:
# 		1 - Instantiates a MainScraper class
# 		2 - Retrieves list of championships
# 		3 - Instantiates a ChampionshipScraper for each championship
# 		4 - Calls status() for each and validates response's type and value
# 		"""
# 		with scrapers.MainScraper(request_retries=REQUEST_RETRIES) as scraper:
# 			for i, row in scraper.championships().iterrows():
# 				with self.subTest(i=row.get('name')):
# 					with scraper.championship(i) as champ_scraper:
# 						status = champ_scraper.status()
# 						self.assertIsInstance(status, bool)
# 						self.assertTrue(status)

# 	def test_season(self):
# 		"""Steps:
# 		1 - Instantiates a MainScraper class
# 		2 - Retrieves list of championships
# 		3 - Instantiates a ChampionshipScraper for each championship
# 		4 - Calls season() for each and validates response's type
# 		5 - Calls season(999) and verify if error is raised
# 		"""
# 		with scrapers.MainScraper(request_retries=REQUEST_RETRIES) as scraper:
# 			for i, row in scraper.championships().iterrows():
# 				with self.subTest(i=row.get('name')):
# 					with scraper.championship(i) as champ_scraper:
# 						seasons = champ_scraper.seasons()
# 						seasons = [i for i, row in seasons.iterrows()]
# 						season_scraper = champ_scraper.season(seasons[0])

# 						self.assertIsInstance(season_scraper,
# 											  scrapers.SeasonScraper)

# 						with self.assertRaises(ValueError):
# 							champ_scraper.season(999)

# 	def test_seasons(self):
# 		"""Steps:
# 		1 - Instantiates a MainScraper class
# 		2 - Retrieves list of championships
# 		3 - Instantiates a ChampionshipScraper for each championship
# 		4 - Calls seasons() for each and validates response's type and value
# 		5 - Calls seasons(number=-1) and verify if error is raised
# 		6 - Calls seasons(target=999) and verify if error is raised
# 		"""
# 		validate = lambda x: x.get('start_date') is not None \
# 							 and isinstance(x['start_date'], float) \
# 							 and x.get('end_date') is not None \
# 							 and isinstance(x['end_date'], float) \
# 							 and x.get('number_goals') is not None \
# 							 and isinstance(x['number_goals'], float) \
# 							 and x.get('number_games') is not None \
# 							 and isinstance(x['number_games'], float)

# 		with scrapers.MainScraper(request_retries=REQUEST_RETRIES) as scraper:
# 			for i, row in scraper.championships().iterrows():
# 				with self.subTest(i=row.get('name')):
# 					with scraper.championship(i) as champ_scraper:
# 						seasons = champ_scraper.seasons()
# 						self.assertIsInstance(seasons, pd.DataFrame)
# 						self.assertIn('start_date', seasons.columns)
# 						self.assertIn('end_date', seasons.columns)
# 						self.assertIn('number_goals', seasons.columns)
# 						self.assertIn('number_games', seasons.columns)
# 						self.assertTrue(all(
# 							validate(row) for i, row in seasons.iterrows()))

# 						with self.assertRaises(ValueError):
# 							champ_scraper.seasons(number=-1)

# 						with self.assertRaises(ValueError):
# 							champ_scraper.seasons(target=999)
