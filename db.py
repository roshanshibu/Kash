import sqlite3 as sql
import logging
from os.path import isfile, getsize
import time

database_file = "kash.db"
conn = None
cur = None #global cursor, can be used in case of select statements

transcation_type = {'CREDIT':1, 'DEBIT':2, 'TRANSFER':3}


def execute(conn, sql_command, params = None, exec_script = False):
	""" execute a given sql statement
	conn -> Connection object
	sql_command -> any sql statement
	params -> a tuple containg variables that can be plugged into the sql_command
	"""
	logging.debug ("sql_command = ["+sql_command+"]")
	try:
		global cur
		cur = conn.cursor()
		if not exec_script:
			if params is None:
				cur.execute(sql_command)
			else:
				cur.execute(sql_command, params)
		else:
			cur.executescript(sql_command)
		conn.commit()
		return (True)
	except sql.Error as e:
		logging.error (e)
		return (False)
	except Exception as e:
		logging.error ("Unexpected Error! :"+str(e))
		return (False)


def get_account_types():
	sql_get_account_types = """
							SELECT * FROM account_type 
							"""
	if (not execute(conn, sql_get_account_types)):
		logging.error ("Failed to get data from account_type table")
		return None
	
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
		logging.error("could not get id for latest account type id")
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

def get_all_accounts():
	sql_get_all_account_types = """
								SELECT * FROM account
								"""
	if (not execute(conn, sql_get_all_account_types)):
		logging.error ("Failed to get data from account_type table")
		return None
	
	rows = cur.fetchall()
	return(rows)


def create_transcation(t_name, t_type, category_id, account_id, amount, sys_note, created = None):
	if (created is None):
		created = int(time.time())
	
	sql_insert_new_transcation = """
									INSERT INTO transactions(name, type, category_id, account_id, amount, sys_note, created)
									VALUES
									(?,?,?,?,?,?,?);
								"""
	insert_values = (t_name, t_type, category_id, account_id, amount, sys_note, created)
	if (not execute (conn, sql_insert_new_transcation, insert_values)):
		logging.error("Failed to insert transcation")
		return False
	
	i_amount = int(amount)
	if (int(t_type) != transcation_type['TRANSFER']):
		#increase or decrease balance amount depening on type
		if int(t_type) == transcation_type['DEBIT']:
			i_amount *= -1
		sql_update_account_balance = "UPDATE account SET balance = balance + " + str(i_amount) + " WHERE id = " + str(account_id)
		if (not execute (conn, sql_update_account_balance)):
			logging.error("Failed to update account")
			return False
	else:
		#transfer amount from account_id to sys_note vaue id account
		sql_update_account_balance = "UPDATE account SET balance = balance + " + str(i_amount) + " WHERE id = " + str(sys_note) + ";" + "UPDATE account SET balance = balance + " + str(i_amount * -1) + " WHERE id = " + str(account_id) + ";"
		if (not execute (conn, sql_update_account_balance, None, True)):
			logging.error("Failed to update with transfer of amount")
			return False

	return True

def create_new_category(c_name, c_logo_id, c_color_hex):
	sql_insert_new_category = """
									INSERT INTO category(name, logo_id, color_hex)
									VALUES
									(?,?,?);
								"""
	insert_values = (c_name, c_logo_id, c_color_hex)
	if (not execute (conn, sql_insert_new_category, insert_values)):
		logging.error("Failed to create new category "+c_name)
		return (False, None)
	
	sql_get_lastest_category_id = """
									SELECT MAX(id) FROM category
									"""
	if (not execute (conn, sql_get_lastest_category_id)):
		logging.error("could not get id for latest category")
		return (False, None)

	return (True, cur.fetchall())

def get_all_category():
	sql_get_all_category = """
							SELECT * FROM category 
							"""
	if (not execute(conn, sql_get_all_category)):
		logging.error ("Failed to get data from category table")
		return None
	
	rows = cur.fetchall()
	return(rows)

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
		
		'''
		2) transactions and category table
		'''
		sql_create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions (
											id INTEGER PRIMARY KEY AUTOINCREMENT,
											name TEXT,
											type INT,
											category_id INT,
											account_id INT,
											amount INT,
											sys_note TEXT,
											created INT,
											FOREIGN KEY (category_id) REFERENCES category (id)
											FOREIGN KEY (account_id) REFERENCES account (id)								
										); """
		sql_create_category_table = """ CREATE TABLE IF NOT EXISTS category (
											id INTEGER PRIMARY KEY AUTOINCREMENT,
											name TEXT,
											logo_id TEXT,
											color_hex TEXT
										); """
		if (not execute(conn, sql_create_category_table)):
			logging.error ("Failed to create table category. Exiting...")
			exit(0)

		if (not execute(conn, sql_create_transactions_table)):
			logging.error ("Failed to create table transactions. Exiting...")
			exit(0)

		create_new_category("Transfer", "c_food", "#000000")



