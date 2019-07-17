# -*- coding: utf-8 -*-

class FutpediaRequestError(Exception):
	"""To be raised when an HTTP request error occurs."""
	pass

class FutpediaNotFoundError(Exception):
	"""To be raised when an expected HTML content from a page is missing or
	when a chosen team or championship is not found.
	"""
	pass
