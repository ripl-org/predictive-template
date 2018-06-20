from RIIPL_connection import *
import sys

def query_and_export(sql_path, csv_path):
	with open(sql_path, 'r') as sql_f:
		sql_str = ''
		for line in sql_f:
			sql_str += line.rstrip() + ' '

	queries = sql_str.split(';')

	with RIIPL_connection() as cxn:
		cursor = None
		for query in queries:
			if not query.strip():
				continue
			cursor = cxn.execute(query, verbose=True)

		cxn.spool_to_csv(cursor, csv_path)

def main():
	if len(sys.argv) != 3:
		print("Usage: python csv_to_sql.py SQL_FILEPATH CSV_FILEPATH")
		exit(1)

	query_and_export(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
	main()