"""The packers module holds all classes and functions related to turning
models into specific data structures.

ABCs: Packer

Classes: DataFramePacker
"""

import abc
from functools import partial

import pandas as pd
from cachetools.keys import hashkey
from cachetools import cachedmethod, TTLCache


class Packer(abc.ABC):
	"""An abstract base class for other packer classes to implement.

	Methods: pack
	"""
	def __init__(self, cache_maxsize: int=10, cache_ttl: int=300):
		"""Packer's constructor.

		Parameters
		----------
		cache_maxsize: int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl: int -- time to live in seconds for internal caching of
		data (default 300)
		"""
		self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

	@abc.abstractmethod
	def pack(self, models: tuple):
		"""Builds a data structure out of a list of model's.

		Parameters
		----------
		model: tuple -- the model list with the data

		Returns -- the data structure with the data
		"""
		pass


class DataFramePacker(Packer):
	"""A packer class specialized in building data frames out of models.

	Extends: Packer

	Methods: pack
	"""
	def __init__(self, cache_maxsize: int=10, cache_ttl: int=300):
		"""DataFramePacker's constructor.

		Parameters @Packer
		"""
		super().__init__(cache_maxsize=cache_maxsize, cache_ttl=cache_ttl)

	@cachedmethod(lambda self: self._cache, key=partial(hashkey, 'storage'))
	def pack(self, models: tuple) -> pd.DataFrame:
		"""Builds a data frame out of a list of model's.

		Parameters @Packer
		Returns @Packer
		"""
		idxs = [i[0] for i in models]
		data = [list(i[1:]) for i in models]
		columns = list(models[0]._fields[1:])

		return pd.DataFrame(data, index=idxs, columns=columns)
