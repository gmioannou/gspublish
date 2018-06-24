import sys
from configparser import  ConfigParser
from geoserver.catalog import Catalog
from postgis import PostGIS
from gslayers import *

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def get_usage():
	print '\nUsage: gspublish <configfile>'
	sys.exit(1)

def main():

	# validate args
	if len(sys.argv) != 2:
		get_usage()
	else:
		configfile = sys.argv[1]

	# read the config file
	config = ConfigParser()
	config.read(configfile)
	if config.sections() != ['PostGIS', 'Geoserver', 'Styles']:
		print 'Invalid config file...'
		sys.exit(1)

	# connect to postgis
	pginfo = dict(config.items('PostGIS'))
	pgdb = PostGIS(**pginfo)
	pgdb.info()
	pgdb.connect()

	# connect to geoserver
	gsinfo = Struct(**dict(config.items('Geoserver')))
	gscat = Catalog(gsinfo.url, gsinfo.user, gsinfo.password)

	print '\nGeoserver info:'
	print ' Url:', gsinfo.url
	print ' User:', gsinfo.user
	print ' password:', gsinfo.password

	gsws = gscat.get_workspace(gsinfo.workspace)
	print '\nConnect to Geoserver...'

	if gsws == None:
		wsuri = '{0}/{1}'.format(gsinfo.url, gsinfo.workspace)
		gsws = gscat.create_workspace(gsinfo.workspace, wsuri)
		print 'Workspace created...'

	# sldfile info
	sldinfo = Struct(**dict(config.items('Styles')))
	sldinfo.folder = config.get('Styles', 'folder')
	sldinfo.overwrite = config.getboolean('Styles', 'overwrite')

	print '\nStyles info:'
	print ' Folder: ', sldinfo.folder
	print ' Overwrite: ', sldinfo.overwrite

	# publish layers from postgis to geoserver
	publish_layers(pgdb, gscat, gsws, pginfo, gsinfo, sldinfo)

	# close postgis connection
	pgdb.conn.close()

	print("\nCompleted!")
