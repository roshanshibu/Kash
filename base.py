import sqlite3 as sql
import logging

database = "kash.db"

#logging options
log_to_file = 0
min_log = logging.DEBUG

log_format = '%(asctime)s | %(levelname)s | %(funcName)s() :: %(message)s'

if (log_to_file != 0):
	logging.basicConfig(filename='kash.log', encoding='utf-8', level=min_log, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
else:
	logging.basicConfig(format=log_format, level=min_log, datefmt='%m/%d/%Y %I:%M:%S %p')
#----------------

#create and connect to the db "kash" if not already present
try:
	conn = sql.connect(database)
	print ("Succesfully connected to database [",database,"]")
except sql.Error as e:
	print ("Exception while creating/connecting to database file [",database,"]:\n{",e,"}")

#develop funstions for each functionality

'''
1) create an account and store its details
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



def execute(conn, sql_command, params = None):
	""" execute a given sql statement
	conn -> Connection object
	sql_command -> any sql statement
	params -> a tuple containg variables that can be plugged into the sql_command
	"""
	logging.debug("sql_command = ["+sql_command+"]")
	try:
		c = conn.cursor()
		if params is None:
			c.execute(sql_command)
		else:
			c.execute(sql_command, params)
		return (True)
	except sql.Error as e:
		logging.error(e)
		return (False)
	except:
		logging.error("Unexpected Error!")
		return (False)

