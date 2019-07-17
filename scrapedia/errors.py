# -*- coding: utf-8 -*-

class FutpediaRequestError(Exception):
	"""To be raised when an HTTP request error occurs."""
	pass

class FutpediaMissingError(Exception):
	"""To be raised when an expected HTML content from a page is missing."""
	pass
