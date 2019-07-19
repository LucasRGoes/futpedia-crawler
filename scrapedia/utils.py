"""Scrapedia's utilites.

Functions: isjson.
"""

import json


def isjson(s: str): -> bool
	"""A function that verifies if the variable is loadable by the json
	package. Returns True if it is parseable and False otherwise.

	Parameters
	----------
	s : str -- the string to be tested

	Returns
	-------
	flag : bool -- if parseable returns True, otherwise False
	"""
	try:
		json_obj = json.loads(s)
	except:
		return False
	return True
