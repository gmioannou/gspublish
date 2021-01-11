import sys, os
import glob
import copy
from .style_generator import Style

def publish_layers(pgdb, gscat, gsws, pginfo, gsinfo, sldinfo):
	'''iterate database schemas, create datastores in geoserver and publish layers'''

	# get schemas list from the database
	schemas = pgdb.get_schemas()

	for schema in schemas:
		# set datastore name to schema if no default provided
		if gsinfo.datastore:
			datastore = gsinfo.datastore
		else:
			datastore = schema

		# get layers from the databae
		layers = pgdb.get_layers(schema)

		# create datastore in geoserver only if schema has layers
		if len(layers) > 0:
			gsds = create_datastore(gscat, gsws, datastore, schema, pginfo)

		# publish layers
		for layer in layers:
			layer_schema = layer[0]
			layer_name = layer[1]
			layer_srs = 'EPSG:{0}'.format(layer[3])
			layer_geomtype = layer[4]

			if layer_srs != 'EPSG:0':
				publish_layer(gscat, gsws, gsds, layer_name, layer_srs, layer_geomtype)
				create_default_style(gscat, gsws, gsds, layer_name, layer_geomtype, sldinfo)
				create_alternate_styles(gscat, gsws, pgdb, layer_schema, layer_name, layer_geomtype, sldinfo)

def publish_layer(gscat, gsws, gsds, layer_name, layer_srs, layer_geomtype):
	'''Publish layers as feature_types in geoserver's workspace.datastore'''

	layer_resource = gscat.get_resource(layer_name, gsds, gsws)
	if layer_resource == None:
		layer = gscat.publish_featuretype(layer_name, gsds, layer_srs)
		layer.abstract = '{0}  {1}  {2}'.format(layer_name, layer_geomtype, layer_srs)
		gscat.save(layer)
		print('\n  {0}.{1}.{2}'.format(gsws.name, gsds.name, layer_name))
	else:
		print('\n  {0}.{1}.{2} (layer already published)'.format(gsws.name, gsds.name, layer_name))

def create_default_style(gscat, gsws, gsds, layer_name, layer_geomtype, sldinfo):
	'''Generate and publish layer's default style'''
	style_name = layer_name

	# check if the default style exists in the workspace
	gsstyle = gscat.get_style(style_name, gsws)

	# generate and publish default style if it does not exist
	if gsstyle == None:
		print('    {0}'.format(style_name))
		def_style = Style(style_name,
						layer_geomtype,
						sld_folder=sldinfo.folder,
						overwrite=sldinfo.overwrite)

		def_style.generate()
		def_style.publish(gscat, gsws)
	else:
		print('    {0} (style already published)'.format(style_name))

	# get default style
	gsstyle = gscat.get_style(style_name, gsws)

	gslayer = gscat.get_layer('{0}:{1}'.format(gsws.name, layer_name))
	if gslayer != None:
		gslayer.default_style = gsstyle
		gscat.save(gslayer)
	else:
		print('    layer {0} is not published...' % layer_name)

def create_alternate_styles(gscat, gsws, pgdb, layer_schema, layer_name, layer_geomtype, sldinfo):
	'''Generate and publish layer's alternate styles based on lookup table's records'''
	# need to create a list first and then assign it to gslayer.styles
	alt_styles = []
	luts = pgdb.get_lookup_tables(layer_schema, layer_name)
	for lut in luts:
		gsstyle = create_lut_style(gscat, gsws, pgdb, lut, layer_geomtype, sldinfo)
		alt_styles.append(gsstyle)

	# get layer and update alternate styles
	gslayer = gscat.get_layer('{0}:{1}'.format(gsws.name, layer_name))
	gslayer.styles = alt_styles

	gscat.save(gslayer)

def create_lut_style(gscat, gsws, pgdb, lut, layer_geomtype, sldinfo):
	'''Create layer's alternate style based on lookup table'''
	layer_schema = lut[0]
	layer_name = lut[1]
	layer_field = lut[2]
	lut_schema = lut[3]
	lut_name = lut[4]
	lut_field = lut[5]

	recs = pgdb.get_records(lut_schema, lut_name)

	recs_dict = {}
	for rec in recs:
		rec_key = rec[1]
		rec_value = str(rec[2]).replace("&", "and")
		recs_dict.update({rec_key: rec_value})

	# print('\n    {0} {1} {2} {3}'.format(layer_name, layer_field, lut_name, lut_field))
	style_name = '{0}_{1}'.format(layer_name, layer_field.title())

	# check if the style exists
	gsstyle = gscat.get_style(style_name, gsws)

	if gsstyle == None:
		# Generate the style and publish to geoserver
		print('    {0}'.format(style_name))
		lut_style = Style(style_name,
		              layer_geomtype,
					  sld_folder=sldinfo.folder,
					  overwrite=sldinfo.overwrite,
					  property_name=layer_field,
					  values_dictionary=recs_dict,
					  stroke_width=0.1)
		lut_style.generate()
		lut_style.publish(gscat, gsws)
	else:
		print('    {0} (alt style already published)'.format(style_name))

	# get style
	gsstyle = gscat.get_style(style_name, gsws)

	return gsstyle

def create_datastore(gscat, gsws, datastore, schema, pginfo):
	'''Create datastore in geoserver catalog/workspace'''

	# update geoserver datastore connection info to postgis
	gsds_info = pginfo.copy()
	gsds_info['database'] = gsds_info.pop('dbname')
	gsds_info['passwd'] = gsds_info.pop('password')
	gsds_info.update({'dbtype': 'postgis', 'schema': schema})

	# create the Datastore if it does not exist
	gsds = gscat.get_store(datastore, gsws)
	if gsds == None:
		gsds = gscat.create_datastore(datastore, gsws)
		gsds.connection_parameters.update(**gsds_info)
		gscat.save(gsds)
		print('\n{0}.{1}'.format(gsws.name, datastore))
	else:
		print('\n{0}.{1} (already published)'.format(gsws.name, schema))

	return gsds
