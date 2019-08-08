"""Source of exception classes for Scrapedia's pipelines.

Classes: ScrapediaError
"""

class ScrapediaError(Exception):
	"""Generic error to be implemented by further classes in order to uncouple
	Scrapedia's exceptions from others.
	"""
	pass
