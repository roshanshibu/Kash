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
db.init()

#prepare cli menu
#keep this basic, the intent of this program is to develop and test individual apis to interact with the database


#auto-populate some values for testing
autopopulate = 1
if autopopulate != 0:
	db.create_new_account_type("Savings", "---")
	db.create_new_account_type("Checking", "---")
	db.create_new_account("federal", 1, 100000)
	db.create_new_account("south indian", 2, 1000)
	

feature_list = ["create an account", "view accounts", "register transcation"]
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
		db.create_new_category("Food & Drink", "c_food", "#000000")
		db.create_transcation("Groceries - quality", db.transcation_type['DEBIT'], 1, 1, 100, "")
		db.create_transcation("Monthly saving", db.transcation_type['TRANSFER'], 1, 1, 900, "2")
