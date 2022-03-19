import sqlite3 as sql
import logging
from os.path import isfile, getsize

database_file = "kash.db"
	
def execute(conn, sql_command, params = None):
	""" execute a given sql statement
	conn -> Connection object
	sql_command -> any sql statement
	params -> a tuple containg variables that can be plugged into the sql_command
	"""
	logging.debug ("sql_command = ["+sql_command+"]")
	try:
		c = conn.cursor()
		if params is None:
			c.execute(sql_command)
		else:
			c.execute(sql_command, params)
		return (True)
	except sql.Error as e:
		logging.error (e)
		return (False)
	except:
		logging.error ("Unexpected Error!")
		return (False)

def init():
	should_init = False
	#check if db is present
	if not isfile(database_file):
		should_init = True
	elif getsize(database_file) < 100: # SQLite database file header is 100 bytes
		should_init = True
	
	try:
		conn = sql.connect(database_file)
		logging.debug ("Succesfully connected to database ["+database_file+"]")
	except sql.Error as e:
		logging.error ("Exception while creating/connecting to database file ["+database_file+"]:\n{"+e+"}")
		exit(0)

	if should_init == True:
		'''
		create all the required tables
		1) account and account_type table
		'''
		#create table account and account_type if not already present
		sql_create_account_table = """ CREATE TABLE IF NOT EXISTS account (
											id INTEGER PRIMARY KEY AUTOINCREMENT,
											name TEXT,
											type_id INT,
											balance INT,
											created INT,
											FOREIGN KEY (type_id) REFERENCES account_type (id)									
										); """
		sql_create_account_type_table = """ CREATE TABLE IF NOT EXISTS account_type (
											id INTEGER PRIMARY KEY AUTOINCREMENT,
											name TEXT,
											logo_id TEXT
										); """

		if (not execute(conn, sql_create_account_type_table)):
			logging.error ("Failed to create table account_type. Exiting...")
			exit(0)

		if (not execute(conn, sql_create_account_table)):
			logging.error ("Failed to create table account. Exiting...")
			exit(0)
