from calendar import month
import sqlite3 as sql
import logging
from os.path import isfile, getsize
import time
import datetime

database_file = "kash.db"
conn = None
cur = None #global cursor, can be used in case of select statements

s_transcations_by_ID = "ID" #for given id
s_transcations_by_MONTH = "MONTH" #for given month if unix timestamp is provided, otherwise the current month
s_transcations_by_CATEGORYNAME = "CATEGORYNAME" #for given category name
s_transcations_by_CATEGORYID = "CATEGORY" #for given category id
s_transcations_sort_LATEST = "SORT BY LATEST" #sort by date of tran desc
s_transcations_sort_VALUE = "SORT BY VALUE" #sort by amount desc



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

def get_account_balance(account_id = None):
	sql_get_account_balance = """
								SELECT SUM(balance) FROM account
								"""
	if account_id is not None:
		sql_get_account_balance += " WHERE id="+str(account_id)
	
	if (not execute(conn, sql_get_account_balance)):
		logging.error ("Failed to get acount balance")
		return None
	
	rows = cur.fetchall()
	return(rows[0][0])

def update_account_balance(account_id, new_balance):
	cur_balance = get_account_balance(account_id)
	diff = new_balance - cur_balance
	if diff > 0:
		t_type = transcation_type['CREDIT']
	else:
		t_type = transcation_type['DEBIT']
	if (not create_transcation("Balance adjustment", t_type, 2, account_id, abs(diff), '')):
		logging.error("Failed to update balance")
		return False
	return True


def create_transcation(t_name, t_type, category_id, account_id, amount, sys_note, created = None, ghost = None):
	if ghost is None:
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
	else:
		logging.info("Ghost transcation with params [%s, %s, %s, %s, %s, %s, %s, %s]", str(t_name), str(t_type), str(category_id), str(account_id), str(amount), str(sys_note), str(created), str(ghost))
	
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

def month_start_end(unixtime):
	#for the given timestamp, get the month
	#then return the timestamp of the month start and end
	dt = datetime.datetime.fromtimestamp(unixtime)
	f_month = dt.month
	f_year = dt.year
	first_second_f_month = datetime.datetime(f_year, f_month, 1)
	first_second_f_plus_1_month = datetime.datetime(f_year, f_month+1, 1)
	last_second_f_month = first_second_f_plus_1_month - datetime.timedelta(seconds=1)
	
	month_start = int(time.mktime(first_second_f_month.timetuple()))
	month_end = int(time.mktime(last_second_f_month.timetuple()))
	
	return (month_start, month_end)

def get_transcations(options = None, param = None):
	sql_get_transcations = """
							SELECT * FROM transactions t 
								INNER JOIN  category c ON t.category_id = c.id
							"""
	#set WHERE
	sql_get_transcations_where = ""
	sql_get_transcations_order_by = ""
	if (options is not None):
		i = 0
		for op in options:
			if (op == s_transcations_by_ID):
				if (len(sql_get_transcations_where) > 0):
					sql_get_transcations_where += " AND "
				sql_get_transcations_where += " t.id = "+str(param[i])
				continue
			
			if (op == s_transcations_by_MONTH):
				if (len(sql_get_transcations_where) > 0):
					sql_get_transcations_where += " AND "
				if (param[i] is None):
					unixtime = int(time.time())
				else:
					unixtime = int(param[i])
				month_interval = month_start_end(unixtime)
				sql_get_transcations_where += " t.created BETWEEN " + str(month_interval[0]) + " AND " + str(month_interval[1])
				continue

			if (op == s_transcations_by_CATEGORYNAME):
				if (len(sql_get_transcations_where) > 0):
					sql_get_transcations_where += " AND "
				sql_get_transcations_where += " c.name = " + str(param[i])
				continue		
			
			if (op == s_transcations_by_CATEGORYID):
				if (len(sql_get_transcations_where) > 0):
					sql_get_transcations_where += " AND "
				sql_get_transcations_where += " c.id = " + str(param[i])
				continue

			if (op == s_transcations_sort_LATEST):
				if (len(sql_get_transcations_order_by) > 0):
					sql_get_transcations_order_by += ", "
				sql_get_transcations_order_by += " t.created DESC "
				continue
			
			if (op == s_transcations_sort_VALUE):
				if (len(sql_get_transcations_order_by) > 0):
					sql_get_transcations_order_by += ", "
				sql_get_transcations_order_by += " t.amount DESC "
				continue
			
			i+=1

	if (len(sql_get_transcations_where) > 0):
		sql_get_transcations += " WHERE "+ sql_get_transcations_where
	if (len(sql_get_transcations_order_by) > 0):
		sql_get_transcations += " ORDER BY "+ sql_get_transcations_order_by
		
	if (not execute(conn, sql_get_transcations)):
		logging.error ("Failed to get data from transctaion table")
		return None
	
	rows = cur.fetchall()
	return(rows)

def del_transcation(del_tran_id):
	#get transcation details
	detail = get_transcations([s_transcations_by_ID], [del_tran_id]) [0]
	print ("will delete...")
	print (detail)
	del_t_type = int(detail[2])
	del_t_account = detail[4]
	del_t_amount = detail[5]

	if del_t_type != transcation_type['TRANSFER']:
		#revert the transcation amount
		#do a ghost transcation, so we do nor create entries in the transcation table, but the amount table gets updated 
		if (del_t_type == transcation_type['CREDIT']):
			del_t_amount *= -1
		
		if ( not create_transcation(None, transcation_type['CREDIT'], None, del_t_account, del_t_amount, None, None, True)):
			logging.error("Failed to do a ghost transcation to revert del_tran ["+del_tran_id+"]")
			return False
	else:
		#do ghost transcation for both accounts
		del_t_from = int(del_t_account)
		del_t_to = int(detail[6])
		if ( not create_transcation(None, transcation_type['CREDIT'], None, del_t_from, del_t_amount, None, None, True)):
			logging.error("Failed to do a ghost transcation to revert transfer op ["+del_tran_id+"] : credit to original sender failed")
			return False
		if ( not create_transcation(None, transcation_type['DEBIT'], None, del_t_to, del_t_amount, None, None, True)):
			logging.error("Failed to do a ghost transcation to revert transfer op ["+del_tran_id+"] : debit from original receiver failed")
			return False
		
	
	sql_delete_transcation_entry = "DELETE FROM transactions where id =" + del_tran_id
	if (not execute (conn, sql_delete_transcation_entry)):
		logging.error("Failed to delete transcation id ["+del_tran_id+"] row from transcations table")
		return False

	return True

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

		create_new_category("Transfer", "c_transfer", "#000000")
		create_new_category("Balance Adjustment", "c_bal_adj", "#000000")
		
	
	return should_init


