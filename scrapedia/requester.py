"""The requester module holds all classes and functions related to fetching
Futpédia's web pages.

Classes: FutpediaRequester
"""

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .errors import ScrapediaRequestError


BASE_PROTOCOL = 'http://'
BASE_HOST = 'futpedia.globo.com'
BASE_URL = '{0}{1}'.format(BASE_PROTOCOL, BASE_HOST)

BACKOFF_FACTOR = 1
STATUS_LIST = [403, 404, 502, 503, 504]


class FutpediaRequester(object):
	"""The FutpediaRequester is used to fetch Futpédia's web pages.

	Magic Methods: __enter__, __exit__

	Getters and Setters: retry_limit

	Methods: fetch
	"""
	def __init__(self, retry_limit: int=10):
		"""FutpediaRequester's constructor. Creates an HTTP session to allow
		web page requesting.

		Parameters
		----------
		retry_limit: int -- number of maximum retrying of requests on
		cases where the status code is in a given set (default 10)
		"""
		self._retry_limit = retry_limit

		self._session = requests.Session()
		self._retries = Retry(total=self._retry_limit,
							  backoff_factor=BACKOFF_FACTOR,
							  status_forcelist=STATUS_LIST)
		self._session.mount(BASE_PROTOCOL,
							HTTPAdapter(max_retries=self._retries))

	def __enter__(self):
		"""FutpediaRequester's enter method for Python's 'with' management."""
		return self

	def __exit__(self, type, value, tb):
		"""FutpediaRequester's exit method for Python's 'with' management."""
		self._session.close()

	@property
	def retry_limit(self) -> int:
		"""Getter for retry_limit parameter."""
		return self._retry_limit
	
	@retry_limit.setter
	def retry_limit(self, new_value: int):
		"""Setter for retry_limit parameter.

		Throws ValueError
		"""
		if not new_value > 0:
			raise ValueError('Parameter \'new_value\' should be higher than 0')
		else:
			self._retry_limit = new_value

			self._retries = Retry(total=self._retry_limit,
								  backoff_factor=BACKOFF_FACTOR,
							  	  status_forcelist=STATUS_LIST)
			self._session.mount(BASE_PROTOCOL,
								HTTPAdapter(max_retries=self._retries))

	def fetch(self, path: str) -> bytes:
		"""Fetches a web page's content accessible from the base URL plus
		the chosen path.

		Returns: bytes -- the chosen web page's content as bytes

		Throws ScrapediaRequestError
		"""
		try:
			res = self._session.get('{0}{1}'.format(BASE_URL, path))
			return res.content
		except Exception as err:
			raise ScrapediaRequestError(
				'Futpédia\'s chosen web page couldn\'t be accessed, try again'
				' later'
			) from err
