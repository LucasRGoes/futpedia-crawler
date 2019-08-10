"""The models that hold data concerning Futpédia's scraped information.

NamedTuples: Championship, Season, Team
"""

import collections


Championship = collections.namedtuple('Championship', ['uid', 'name', 'path'])


Season = collections.namedtuple('Season', ['year', 'start_date', 'end_date',
										   'number_goals', 'number_games',
										   'path'])


Team = collections.namedtuple('Team', ['uid', 'name', 'path'])
