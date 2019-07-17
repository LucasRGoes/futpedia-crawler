# -*- coding: utf-8 -*-

import unittest

from scrapedia import Scrapedia


SCRAPER = Scrapedia(disable_logger=True)


class ScrapediaUnitTests(unittest.TestCase):
	"""Set of unit tests for the class Scrapedia.

	Test set: test_status
	"""
	def test_status(self):
		"""Steps:
		1 - Verifies return type of the method;
		"""
		ret = SCRAPER.status()
		self.assertTrue(isinstance(ret, bool))

	def test_teams(self):
		"""Steps:
		1 - Verifies return type of the method;
		"""
		ret = SCRAPER.teams()
		self.assertTrue(isinstance(ret, list))

	def test_championships(self):
		"""Steps:
		1 - Verifies return type of the method;
		"""
		ret = SCRAPER.championships()
		self.assertTrue(isinstance(ret, list))

if __name__ == 'main':
	unittest.main()
