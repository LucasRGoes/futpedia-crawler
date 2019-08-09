"""Collection of unit tests for scrapedia.packers module's classes and
functions.

Classes: DataFramePackerTests
"""

import unittest

import pandas as pd

import scrapedia.models as models
import scrapedia.packers as packers


MOCK_CHAMP_MODEL = [models.Championship(
	0, 'Campeonato Brasileiro', '/campeonato/campeonato-brasileiro')]


class DataFramePackerTests(unittest.TestCase):
	"""Set of unit tests to validate an instance of a DataFramePacker and
	its methods.

	Tests: test_pack
	"""
	def test_pack(self):
		"""Steps:
		1 - Instantiates a DataFramePacker
		2 - Uses pack(MOCK_CHAMP_MODEL) and verify response
		"""
		packer = packers.DataFramePacker()
		res = packer.pack(MOCK_CHAMP_MODEL)
		self.assertIsInstance(res, pd.DataFrame)
		self.assertEqual(len(res.columns), 2)
		self.assertEqual(len(res.index), 1)


if __name__ == 'main':
	unittest.main()
