"""Collection of unit tests for scrapers.py module.

Classes: MainScraperTests, ChampionshipScraperTests, SeasonScraperTests
"""

import unittest

import pandas as pd

from scrapedia import scrapers
from scrapedia.errors import ScrapediaNotFoundError


class MainScraperTests(unittest.TestCase):
	"""Set of unit tests for validating an instance of MainScraper.

	Tests: test_status, test_championship, test_teams, test_championships
	"""
	def test_status(self):
		"""Steps:
		1 - Instantiates a MainScraper class with a mock URL
		2 - Calls status() and validates response's type and value
		"""
		with scrapers.MainScraper() as scraper:
			status = scraper.status()
			self.assertIsInstance(status, bool)
			self.assertTrue(status)

	def test_championship(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Calls championship(0) and validates response's type
		3 - Calls championship(-1) and verify if error is raised
		3 - Calls championship(999) and verify if error is raised
		"""
		with scrapers.MainScraper() as scraper:
			champ_scraper = scraper.championship(0)
			self.assertIsInstance(champ_scraper, scrapers.ChampionshipScraper)

			with self.assertRaises(ValueError):
				scraper.championship(-1)

			with self.assertRaises(ScrapediaNotFoundError):
				scraper.championship(999)

	def test_teams(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Calls teams() and validates response's type and value
		"""
		validate = lambda x: x.get('name') is not None \
							 and isinstance(x['name'], str)

		with scrapers.MainScraper() as scraper:
			teams = scraper.teams()
			self.assertIsInstance(teams, pd.DataFrame)
			self.assertIn('name', teams.columns)
			self.assertTrue(all(validate(row) for i, row in teams.iterrows()))

	def test_championships(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Calls championships() and validates response's type and value
		"""
		validate = lambda x: x.get('name') is not None \
							 and isinstance(x['name'], str)

		with scrapers.MainScraper() as scraper:
			champs = scraper.championships()
			self.assertIsInstance(champs, pd.DataFrame)
			self.assertIn('name', champs.columns)
			self.assertTrue(all(validate(row) for i, row in champs.iterrows()))


class ChampionshipScraperTests(unittest.TestCase):
	"""Set of unit tests for validating an instance of ChampionshipScraper.

	Tests: test_status, test_season, test_seasons
	"""
	def test_status(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Retrieves list of championships
		3 - Instantiates a ChampionshipScraper for each championship
		4 - Calls status() for each and validates response's type and value
		"""
		with scrapers.MainScraper() as scraper:
			champs = scraper.championships()
			for i, row in champs.iterrows():
				with self.subTest(i=row.get('name')):
					with scraper.championship(i) as champ_scraper:
						status = champ_scraper.status()
						self.assertIsInstance(status, bool)
						self.assertTrue(status)

	def test_season(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Retrieves list of championships
		3 - Instantiates a ChampionshipScraper for each championship
		4 - Calls season() for each and validates response's type
		5 - Calls season(999) and verify if error is raised
		"""
		with scrapers.MainScraper() as scraper:
			champs = scraper.championships()
			for i, row in champs.iterrows():
				with self.subTest(i=row.get('name')):
					with scraper.championship(i) as champ_scraper:
						seasons = champ_scraper.seasons()
						seasons = [i for i, row in seasons.iterrows()]
						season_scraper = champ_scraper.season(seasons[0])

						self.assertIsInstance(season_scraper,
											  scrapers.SeasonScraper)

						with self.assertRaises(ValueError):
							champ_scraper.season(999)

	def test_seasons(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Retrieves list of championships
		3 - Instantiates a ChampionshipScraper for each championship
		4 - Calls seasons() for each and validates response's type and value
		5 - Calls seasons(number=-1) and verify if error is raised
		6 - Calls seasons(target=999) and verify if error is raised
		"""
		validate = lambda x: x.get('start_date') is not None \
							 and isinstance(x['start_date'], float) \
							 and x.get('end_date') is not None \
							 and isinstance(x['end_date'], float) \
							 and x.get('number_goals') is not None \
							 and isinstance(x['number_goals'], float) \
							 and x.get('number_games') is not None \
							 and isinstance(x['number_games'], float)

		with scrapers.MainScraper() as scraper:
			champs = scraper.championships()
			for i, row in champs.iterrows():
				with self.subTest(i=row.get('name')):
					with scraper.championship(i) as champ_scraper:
						seasons = champ_scraper.seasons()
						self.assertIsInstance(seasons, pd.DataFrame)
						self.assertIn('start_date', seasons.columns)
						self.assertIn('end_date', seasons.columns)
						self.assertIn('number_goals', seasons.columns)
						self.assertIn('number_games', seasons.columns)
						self.assertTrue(all(
							validate(row) for i, row in seasons.iterrows()))

						with self.assertRaises(ValueError):
							champ_scraper.seasons(number=-1)

						with self.assertRaises(ValueError):
							champ_scraper.seasons(target=999)


class SeasonScraperTests(unittest.TestCase):
	"""Set of unit tests for validating an instance of SeasonScraper.

	Tests: test_status
	"""
	def test_status(self):
		"""Steps:
		1 - Instantiates a MainScraper class
		2 - Retrieves list of championships
		3 - Instantiates a ChampionshipScraper for each championship
		4 - Retrieves list of seasons for each championshiop
		5 - Instantiates a SeasonScraper for each season
		4 - Calls status() for each and validates response's type and value
		"""
		with scrapers.MainScraper() as scraper:
			champs = scraper.championships()
			for i, row in champs.iterrows():
				with scraper.championship(i) as champ_scraper:
					seasons = champ_scraper.seasons()
					for j, row2 in seasons.iterrows():
						with self.subTest(i=(row.get('name'), j)):
							with champ_scraper.season(j) as season_scraper:
								status = season_scraper.status()
								self.assertIsInstance(status, bool)
								self.assertTrue(status)


if __name__ == 'main':
	unittest.main()
