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