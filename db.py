import sqlite3 as sql
import logging
from os.path import isfile, getsize
import time

database_file = "kash.db"
conn = None
cur = None #global cursor, can be used in case of select statements

def execute(conn, sql_command, params = None):
	""" execute a given sql statement
	conn -> Connection object
	sql_command -> any sql statement
	params -> a tuple containg variables that can be plugged into the sql_command
	"""
	logging.debug ("sql_command = ["+sql_command+"]")
	try:
		global cur
		cur = conn.cursor()
		if params is None:
			cur.execute(sql_command)
		else:
			cur.execute(sql_command, params)
		conn.commit()
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
		global conn
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

def get_account_types():
	sql_get_account_types = """
							SELECT * FROM account_type 
							"""
	if (not execute(conn, sql_get_account_types)):
		logging.error ("Failed to get data from account_type table")
	
	rows = cur.fetchall()
	return(rows)

def create_new_account_type(type_name, type_logo_id):
	sql_insert_new_account_type = """
									INSERT INTO account_type(name, logo_id)
									VALUES
									(?,?);
								"""
	insert_values = (type_name, type_logo_id)
	if (not execute (conn, sql_insert_new_account_type, insert_values)):
		logging.error("Failed to insert values [%s] and [%s] into account_types table", type_name, type_logo_id)
		return (False, None)
	
	sql_get_lastest_account_type_id = """
									SELECT MAX(id) FROM account_type
									"""
	if (not execute (conn, sql_get_lastest_account_type_id)):
		logging.error("could not get id for latest account id")
		return (False, None)

	return (True, cur.fetchall())

def create_new_account(name, type_id, balance, created = None):
	if (created is None):
		created = int(time.time())

	sql_create_new_account = """
							INSERT INTO account (name, type_id, balance, created)
								VALUES
								(?,?,?,?) 
							"""
	insert_values = (name, type_id, balance, created)
	if (not execute (conn, sql_create_new_account, insert_values)):
		logging.error("Failed to create new accont")
		return False
	
	return True
	