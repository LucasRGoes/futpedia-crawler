"""The models that hold data concerning Futpédia's available information.

NamedTuples: Championship, Season, Team
"""

import collections


Championship = collections.namedtuple('Championship', ['uid', 'name',
													   'endpoint'])


Season = collections.namedtuple('Season', ['year', 'start_date', 'end_date',
										   'number_goals', 'number_games',
										   'endpoint'])


Team = collections.namedtuple('Team', ['uid', 'name', 'endpoint'])
