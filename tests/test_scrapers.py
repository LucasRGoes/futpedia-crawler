"""Collection of unit tests for scrapers.py script.

Classes: MainScraperTests.
"""

import unittest

from scrapedia import scrapers


class MainScraperTests(unittest.TestCase):
	"""Set of unit tests for validating an instance of MainScraper.

	Tests: test_status, test_teams, test_championships.
	"""
	def test_status(self):
		"""Steps:
		1 - Instantiates a MainScraper class;
		2 - Calls status() and validates return type;
		"""
		with scrapers.MainScraper(base_url='https://google.com', # Mock URL
								  logger_disable=True) as scraper:
			ret = scraper.status()
			self.assertTrue(isinstance(ret, bool))

	def test_teams(self):
		"""Steps:
		1 - Instantiates a MainScraper class;
		2 - Calls teams() and validates return type and schema;
		"""
		with scrapers.MainScraper(logger_disable=True) as scraper:
			ret = scraper.teams()

			self.assertTrue(isinstance(ret, list))
			self.assertTrue(all(isinstance(i, dict) for i in ret))

	def test_championships(self):
		"""Steps:
		1 - Instantiates a MainScraper class;
		2 - Calls championships() and validates return type and schema;
		"""
		with scrapers.MainScraper(logger_disable=True) as scraper:
			ret = scraper.championships()

			self.assertTrue(isinstance(ret, list))
			self.assertTrue(all(isinstance(i, dict) for i in ret))


if __name__ == 'main':
	unittest.main()
