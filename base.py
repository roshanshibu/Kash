import sqlite3 as sql


#create and connect to the db "kash" if not already present
database = "kash.db"
try:
	conn = sql.connect(database)
	print ("Succesfully connected to database [",database,"]")
except sql.Error as e:
	print ("Exception while creating/connecting to database file [",database,"]:\n{",e,"}")

#develop funstions for each functionality
'''
1) create an account and store its details
'''
