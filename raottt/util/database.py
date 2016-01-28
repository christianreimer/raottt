"""
Mongo Connection
"""

import pymongo


def DatabaseConnection(collection='raottt'):
    """Setup connection to MongoDb"""
    return pymongo.MongoClient()[collection]


def nuke(yes_i_am_sure=False):
	""""Drops all the collections"""
	assert yes_i_am_sure

	db = DatabaseConnection()
	for name in db.collection_names():
		db[name].drop()

def init():
	"""Initialize the score collection"""
	db = DatabaseConnection()
	db.score.insert_one({'color': 'Red', 'turns': 0, 'wins': 0})
	db.score.insert_one({'color': 'Blue', 'turns': 0, 'wins': 0})