"""Collection of unit tests for scrapedia.requesters module's classes and
functions.

Classes: FutpediaRequesterTests
"""

import unittest

from scrapedia.requesters import FutpediaRequester
from scrapedia.errors import ScrapediaRequestError


class FutpediaRequesterTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a FutpediaRequester and
	its methods.

	Tests: test_retry_limit, test_fetch
	"""
	def test_retry_limit(self):
		"""Steps:
		1 - Instantiates a FutpediaRequester
		2 - Tests the getter
		3 - Tests the setter
		"""
		with FutpediaRequester(retry_limit=3) as requester:
			self.assertEqual(requester.retry_limit, 3)

			requester.retry_limit = 7
			self.assertEqual(requester.retry_limit, 7)

	def test_fetch(self):
		"""Steps:
		1 - Instantiates a FutpediaRequester
		2 - Uses fetch('/') and test response type
		3 - Uses fetch('/unknown') and verify if it raises error 
		"""
		with FutpediaRequester(retry_limit=5) as requester:
			res = requester.fetch('/')
			self.assertIsInstance(res, bytes)

			requester.retry_limit = 1

			with self.assertRaises(ScrapediaRequestError):
				requester.fetch('/unknown')


if __name__ == 'main':
	unittest.main()
