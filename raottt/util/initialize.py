""""
Contains functions to initialize the game environement for the first time
"""

from .database import DatabaseConnection

def database():
	db = DatabaseConnection()
	db.score.insert_one({'color': 'Red', 'turns': 0, 'wins': 0})
	db.score.insert_one({'color': 'Blue', 'turns': 0, 'wins': 0})
