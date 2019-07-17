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

		# 1.
		self.assertTrue(isinstance(ret, bool))

	def test_teams(self):
		"""Steps:
		1 - Verifies return type of the method;
		2 - Verifies if the content matches the expected type;
		3 - Verifies if the content matches the expected schema;
		"""
		ret = SCRAPER.teams()

		# 1.
		self.assertTrue(isinstance(ret, list))

		for i in ret:
			# 2.
			self.assertTrue(isinstance(i, dict))

			# 3.
			self.assertTrue('name' in i)

	def test_championships(self):
		"""Steps:
		1 - Verifies return type of the method;
		2 - Verifies if the content matches the expected type;
		3 - Verifies if the content matches the expected schema;
		"""
		ret = SCRAPER.championships()

		# 1.
		self.assertTrue(isinstance(ret, list))

		for i in ret:
			# 2.
			self.assertTrue(isinstance(i, dict))

			# 3.
			self.assertTrue('name' in i)
			self.assertTrue('first_season' in i)
			self.assertTrue('last_season' in i)


if __name__ == 'main':
	unittest.main()
