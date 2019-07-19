"""Scrapedia's source of exception classes.

Classes: ScrapediaError, ScrapediaRequestError, ScrapediaParseError,
ScrapediaNotFoundError.
"""

class ScrapediaError(Exception):
	"""Generic error to be implemented by further classes in order to uncouple
	Scrapedia's exceptions from others.
	"""
	pass


class ScrapediaRequestError(ScrapediaError):
	"""To be raised whenever an error related to an HTTP request of a Futpédia
	page occurs.
	"""
	pass


class ScrapediaParseError(ScrapediaError):
	"""To be raised whenever an error related to parsing occurs like missing
	expected content from a page or data conversion failures.
	"""
	pass


class ScrapediaNotFoundError(ScrapediaError):
	"""To be raised whenever there is an error where a chosen team, game or championship metadata is not found on the requested or cached data."""
	pass
