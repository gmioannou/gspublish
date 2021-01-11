import sys
import psycopg2
from os import path, system

class PostGIS:
	def __init__(self, host, port, user, password, dbname):
		self.dbname = dbname
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.conn = None
		self.conn_string = (
			"dbname=%s host=%s port=%s user=%s password=%s" % (self.dbname, self.host, self.port, self.user, self.password)
		)

	def info(self):
		print('\nPostGIS Info:')
		print(' Database Name: %s' % self.dbname)
		print(' Host: %s' % self.host)
		print(' Port: %s' % self.port)
		print(' User: %s' % self.user)
		print(' Password: %s' % self.password)

	def connect(self):
		try:
			self.conn = psycopg2.connect(self.conn_string)
			print('\nConnect to database ...')
		except psycopg2.Error as err:
			print(str(err))
			print('\nUnable to connect to database %s ...' % self.dbname)
			sys.exit(1)

	def disconnect(self):
		if self.conn:
			self.conn.commit()
			self.conn.close()

		print("\nDisconnect from database ...")

	def get_schemas(self):
		sql_string = "\
			SELECT schema_name \
			  FROM information_schema.schemata \
	     WHERE schema_name <> 'information_schema' \
	       AND schema_name NOT LIKE 'pg_%' \
			 ORDER BY schema_name;"

		cur = self.conn.cursor()
		cur.execute(sql_string)
		rows = cur.fetchall()
		cur.close()

		schemas = [row[0] for row in rows]

		return schemas

	def get_layers(self, schema):
		"""Return layers list"""
		cur = self.conn.cursor()

		sql_string = "\
		     SELECT f_table_schema, \
			 		f_table_name, \
			 		f_geometry_column, \
			        srid, \
					type \
		       FROM geometry_columns \
		      WHERE f_table_schema = '{0}' \
		   ORDER BY f_table_schema, f_table_name;".format(schema)

		cur.execute(sql_string)
		layers = cur.fetchall()
		cur.close()

		return layers

	def get_lookup_tables(self, schema, layer):
		"""Return layer's lookup_tables list"""

		cur = self.conn.cursor()
		sql_string = "\
			SELECT * \
			  FROM foreign_key_constraints_vw \
			 WHERE table_schema='{0}' AND table_name='{1}'".format(schema, layer)

		cur.execute(sql_string)
		lookup_tables = cur.fetchall()
		cur.close()

		return lookup_tables

	def get_records(self, schema, table):
		"""Return table records"""
		cur = self.conn.cursor()

		sql_string = '\
		    SELECT * \
			  FROM "{0}"."{1}"'.format(schema, table)

		cur.execute(sql_string)
		records = cur.fetchall()
		cur.close()

		return records
