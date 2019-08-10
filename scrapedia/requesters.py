"""The requesters module holds all classes and functions related to fetching
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

STATUS_LIST = [403, 404, 500]


class FutpediaRequester(object):
	"""The FutpediaRequester is used to fetch Futpédia's web pages.

	Magic Methods: __enter__, __exit__

	Methods: fetch
	"""
	def __init__(self, retry_limit: int=10, backoff_factor: int=1):
		"""FutpediaRequester's constructor. Creates an HTTP session to request
		Futpédia's web pages.

		Parameters
		----------
		retry_limit: int -- number of maximum retrying of requests on
		cases where the status code is in a given set (default 10)
		backoff_factor: int -- the number in seconds that serves as the wait
		time between failed requests, getting bigger on each failure
		(default 1)
		"""
		self._session = requests.Session()
		retries = Retry(total=retry_limit, backoff_factor=backoff_factor,
						status_forcelist=STATUS_LIST)
		self._session.mount(BASE_PROTOCOL, HTTPAdapter(max_retries=retries))

	def __enter__(self):
		"""FutpediaRequester's enter method for Python's 'with' management."""
		return self

	def __exit__(self, type, value, tb):
		"""FutpediaRequester's exit method for Python's 'with' management."""
		self._session.close()

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
				' later: {0}'.format(err)
			)
