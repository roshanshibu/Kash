import logging
import db


#logging options
log_to_file = 1
min_log = logging.DEBUG

log_format = '%(asctime)s | %(levelname)s | %(funcName)s() :: %(message)s'

if (log_to_file != 0):
	logging.basicConfig(filename='kash.log', level=min_log, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
else:
	logging.basicConfig(format=log_format, level=min_log, datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info ("!!!!----------Session Start----------!!!!")
#----------------

#initialize db connection
should_init = db.init()

#prepare cli menu
#keep this basic, the intent of this program is to develop and test individual apis to interact with the database


#auto-populate some values for testing, if init was done
if should_init:
	db.create_new_account_type("Savings", "---")
	db.create_new_account_type("Checking", "---")
	db.create_new_account("federal", 1, 100000)
	db.create_new_account("south indian", 2, 1000)
	

feature_list = ["create an account", "view accounts", "register transcation", "adjust balance", "delete a transcation", "view all transcations", "view transcations in this month"]

'''
to-do features:
- view transcations in this month for a specific category (with same sorting)
- view transcations in this month for all categories (give percentage of spending in each category)
- get account balances (individual and total)
- delete an account
'''

while True:
	i=0
	print ("Kash - Choose an option")
	for feature in feature_list:
		i += 1
		print ("(",i,")", feature)

	option = input("\nEnter option number: ")
	if (option == "1"):
		print ("\n")
		print (feature_list[0])
		#get account name, balance
		print ("--------------Enter account details--------------")
		account_name = input("Account Name: ")
		account_balance = input("Starting balance: ")
		account_types = db.get_account_types()
		print ("Account types:")
		for ac_type in account_types:
			print (" (",ac_type[0],")", ac_type[1])
		account_type_id = input ("Select account type. Press x to create a new account type: ")
		if (account_type_id == "x"):
			print ("-------Create new account Type-------")
			account_type_name = input("Enter new account type name: ")
			ret = db.create_new_account_type(account_type_name, "---")
			if (not ret[0]):
				print ("Failed to create type")
			else:
				account_type_id = ret[1][0][0]
				
		print ("account type id is : ", account_type_id)

		if(not db.create_new_account(account_name, account_type_id, account_balance)):
			print ("Failed to create account")
		
		print ("\nCreated new account " + account_name + "!\n\n")

	if (option == "2"):
		print ("\n")
		print (feature_list[1])
		#print all account details
		all_accounts = db.get_all_accounts()
		for account in all_accounts:
			print (account)
		
		print ("\n\n")
	
	if (option == "3"):
		print ("\n")
		print (feature_list[2])
		print ("--------------Enter transcation details--------------")
		t_name =  input("Transcation name: ")
		print ("-------Select transcation Type-------")
		x = 0
		for key in db.transcation_type:
			x += 1
			print ("(",x,")", key)
		t_type = input("Transcation type: ")
		if(int(t_type) != db.transcation_type['TRANSFER']):
			category_types = db.get_all_category()
			for category in category_types:
				print (category)
			category_id = input("Select category type. Press x to create a new category: ")
			if (category_id == "x"):
				print ("-------Create new account Typecategory-------")
				category_name = input("Enter new category name: ")
				ret = db.create_new_category(category_name, "---", "#000000")
				if (not ret[0]):
					print ("Failed to create category")
				else:
					category_id = ret[1][0][0]
					print ("Category id is :",category_id)
		else:
			category_id = 1 #a category called 'Transfer' is created in init for this 
		
		all_accounts = db.get_all_accounts()
		for account in all_accounts:
			print (account)
		account_id = input("Select account id: ")
		amount = input ("enter amount: ")
		sys_note = input("if this is a transfer op, enter the recipient account id: ")
		print (t_name, t_type, category_id, account_id, amount, sys_note)
		db.create_transcation(t_name, t_type, category_id, account_id, amount, sys_note)

	if (option == "4"):
		print ("\n")
		print (feature_list[3])
		#get the new balance and compute diff
		all_accounts = db.get_all_accounts()
		for account in all_accounts:
			print (account)
		account_id = input("Select account id to edit balance: ")
		new_account_balance =  int(input("Enter new balance: "))
		db.update_account_balance(account_id, new_account_balance)

		print ("\n\n")


	if (option == "5"):
		print ("\n")
		print (feature_list[4])
		#get id of transction to be deleted
		all_transcations = db.get_transcations()
		for tran in all_transcations:
			print (tran)
		tran_id = input("Select id of transcation to be deleted: ")
		if (db.del_transcation(tran_id)):
			print ("deleted transcation succesfully")
		else:
			print ("failed to delete transcation")
		print ("\n\n")


	
	if (option == "6"):
		print ("\n")
		print (feature_list[5])
		#print all transcation details
		all_transcations = db.get_transcations()
		for tran in all_transcations:
			print (tran)
		print ("\n\n")
	
	if (option == "7"):
		print ("\n")
		print (feature_list[5])
		#print transcation in this month
		print ("(1)", db.s_transcations_sort_LATEST)
		print ("(2)", db.s_transcations_sort_VALUE)
		sort_option = input("Select sort option: ")
		if sort_option == "1":
			month_transcations = db.get_transcations([db.s_transcations_by_MONTH, db.s_transcations_sort_LATEST], [None])
		else:
			month_transcations = db.get_transcations([db.s_transcations_by_MONTH, db.s_transcations_sort_VALUE], [None])
		for tran in month_transcations:
			print (tran)
		print ("\n\n")
	