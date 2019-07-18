# -*- coding: utf-8 -*-

import json


def isjson(j):
	"""A function that verifies if the variable is loadable by the json
	package. Returns True if it is parseable and False otherwise.
	"""
	try:
		json_obj = json.loads(j)
	except:
		return False
	return True
