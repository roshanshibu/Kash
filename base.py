import logging
import db


#logging options
log_to_file = 0
min_log = logging.DEBUG

log_format = '%(asctime)s | %(levelname)s | %(funcName)s() :: %(message)s'

if (log_to_file != 0):
	logging.basicConfig(filename='kash.log', encoding='utf-8', level=min_log, format=log_format, datefmt='%m/%d/%Y %I:%M:%S %p')
else:
	logging.basicConfig(format=log_format, level=min_log, datefmt='%m/%d/%Y %I:%M:%S %p')
#----------------

#initialize db connection
db.init()
