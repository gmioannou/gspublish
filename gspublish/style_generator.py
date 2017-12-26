import os
import random

class Style:

	def __init__(self, name, geom_type, sld_folder='styles', overwrite=False, property_name=None, values_dictionary={}, stroke_width=0.1):
		self.name = name
		self.geom_type = geom_type
		self.overwrite = overwrite
		self.property_name = property_name
		self.values_dictionary = values_dictionary
		self.stroke_width = stroke_width
		self.sld_folder = sld_folder
		self.file_name = os.path.join(os.getcwd(), *[sld_folder, '{0}.sld'.format(self.name)])
		self.file_unit = None

	def info(self):
		print self.name
		print self.file_name

	def generate(self):
		if os.path.exists(self.file_name):
			if not self.overwrite:
				print '      sld file already exists...'
				return
			else:
				print '      sld file already exists overwriting...'

		self.init_folder()
		self.open_file()
		self.write_Header()
		self.write_Rules()
		self.write_Footer()
		self.close_file()

	def write_Rules(self):
		if len(self.values_dictionary) == 0:
			self.write_RuleHeader(self.name)
			self.write_Symbolizer()
		else:
			for key, value in self.values_dictionary.iteritems():
				self.write_RuleHeader(value)
				self.write_Filter(key)
				self.write_Symbolizer()

	def write_Symbolizer(self):
		if (self.geom_type in {'Point', 'POINT'}):
			symbol = 'circle'
			symbol_size = 8
			stroke_color = self.get_color()
			fill_color = self.get_color()
			self.write_PointSymbolizer(symbol, symbol_size, fill_color, stroke_color)

		elif (self.geom_type in {'Line', 'LINE', 'MULTILINESTRING'}):
			stroke_color = '#454545'
			self.write_LineSymbolizer(stroke_color, self.stroke_width * 20)

			stroke_color = self.get_color()
			self.write_LineSymbolizer(stroke_color, self.stroke_width * 15)

		elif (self.geom_type in {'Polygon', 'POLYGON', 'MULTIPOLYGON'}):
			stroke_color = '#454545'
			fill_color = self.get_color()
			self.write_PolygonSymbolizer(fill_color, stroke_color)

		else:
			print('Unknown geometry type ...')

		self.write_RuleFooter()

	def write_Header(self):
		self.write_it('<?xml version="1.0" encoding="UTF-8"?>')
		self.write_it('<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">')
		self.write_it('  <sld:NamedLayer>')
		self.write_it('    <sld:Name>{0}</sld:Name>'.format(self.name))
		self.write_it('    <sld:UserStyle>')
		self.write_it('      <sld:Name>{0}</sld:Name>'.format(self.name))
		self.write_it('      <sld:Title>{0}</sld:Title>'.format(self.name))
		self.write_it('      <sld:FeatureTypeStyle>')
		self.write_it('        <sld:Name>{0}</sld:Name>'.format(self.name))

	def write_RuleHeader(self, value):
		self.write_it('        <sld:Rule>')
		self.write_it('          <sld:Title>{0}</sld:Title>'.format(value))

	def write_RuleFooter(self):
		self.write_it('        </sld:Rule>')

	def write_Filter(self, key):
		self.write_it('          <ogc:Filter>')
		self.write_it('            <ogc:PropertyIsEqualTo>')
		self.write_it('              <ogc:PropertyName>{0}</ogc:PropertyName>'.format(self.property_name))
		self.write_it('              <ogc:Literal>{0}</ogc:Literal>'.format(key))
		self.write_it('            </ogc:PropertyIsEqualTo>')
		self.write_it('          </ogc:Filter>')

	def write_PolygonSymbolizer(self, fill_color, stroke_color):
		self.write_it('          <sld:PolygonSymbolizer>')
		self.write_it('            <sld:Fill>')
		self.write_it('              <sld:CssParameter name="fill">{0}</sld:CssParameter>'.format(fill_color))
		self.write_it('            </sld:Fill>')
		self.write_it('            <sld:Stroke>')
		self.write_it('              <sld:CssParameter name="stroke">{0}</sld:CssParameter>'.format(stroke_color))
		self.write_it('              <sld:CssParameter name="stroke-width">{0}</sld:CssParameter>'.format(self.stroke_width))
		self.write_it('            </sld:Stroke>')
		self.write_it('          </sld:PolygonSymbolizer>')

	def write_PointSymbolizer(self, symbol, symbol_size, fill_color, stroke_color):
		self.write_it('          <sld:PointSymbolizer>')
		self.write_it('            <sld:Graphic>')
		self.write_it('              <sld:Mark>')
		self.write_it('                <sld:WellKnownName>{0}</sld:WellKnownName>'.format(symbol))
		self.write_it('                <sld:Fill>')
		self.write_it('                  <sld:CssParameter name="fill">{0}</sld:CssParameter>'.format(fill_color))
		self.write_it('                </sld:Fill>')
		self.write_it('                <sld:Stroke>')
		self.write_it('                  <sld:CssParameter name="stroke">{0}</sld:CssParameter>'.format(stroke_color))
		self.write_it('                  <sld:CssParameter name="stroke-width">{0}</sld:CssParameter>'.format(self.stroke_width))
		self.write_it('                </sld:Stroke>')
		self.write_it('              </sld:Mark>')
		self.write_it('              <sld:Size>{0}</sld:Size>'.format(symbol_size))
		self.write_it('            </sld:Graphic>')
		self.write_it('          </sld:PointSymbolizer>')

	def write_LineSymbolizer(self, stroke_color, stroke_width):
		self.write_it('          <sld:LineSymbolizer>')
		self.write_it('            <sld:Stroke>')
		self.write_it('              <sld:CssParameter name="stroke">{0}</sld:CssParameter>'.format(stroke_color))
		self.write_it('              <sld:CssParameter name="stroke-width">{0}</sld:CssParameter>'.format(stroke_width))
		self.write_it('            </sld:Stroke>')
		self.write_it('          </sld:LineSymbolizer>')

	def write_Footer(self):
		self.write_it('      </sld:FeatureTypeStyle>')
		self.write_it('    </sld:UserStyle>')
		self.write_it('  </sld:NamedLayer>')
		self.write_it('</sld:StyledLayerDescriptor>')

	def get_color(self):
		r = lambda: (random.randint(0,255) + 255) / 2
		if ('Water' in self.name or 'Lakes' in self.name or 'Sea' in self.name or 'Gulf' in self.name):
			color = '#%02X%02X%02X' % (0,0,r())
		else:
			color = '#%02X%02X%02X' % (r(),r(),r())

		return(color)

	def write_it(self, string):
		self.file_unit.write(string + '\n')

	def open_file(self):
		self.file_unit = open(self.file_name, "w")

	def close_file(self):
		self.file_unit.close()

	def init_folder(self):
		if not os.path.exists(self.sld_folder):
			os.makedirs(self.sld_folder)

	def validate(self):

		print '==>', self.overwrite

		status = True
		if os.path.exists(self.file_name):
			print '      (sld file already exists,',
			if self.overwrite:
				print 'overwriting ...)'
				status = True
			else:
				print 'not overwriting ...)'
				status = False

		return status

	def publish(self, gscat, gsws):
		with open(self.file_name) as f:
			gscat.create_style(self.name, f.read(), overwrite=True, workspace=gsws.name)
