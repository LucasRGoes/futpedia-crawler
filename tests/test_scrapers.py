"""Collection of unit tests for scrapers.py module.

Classes: MainScraperTests, ChampionshipScraperTests
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

	Tests: test_status
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
				with self.subTest(i=i):
					with scraper.championship(i) as champ_scraper:
						status = champ_scraper.status()
						self.assertIsInstance(status, bool)
						self.assertTrue(status)


if __name__ == 'main':
	unittest.main()
