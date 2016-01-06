"""
Mongo Connection
"""

import pymongo


def DatabaseConnection(collection='raottt'):
	"""Setup connection to MongoDb"""
    return pymongo.MongoClient()[collection]
