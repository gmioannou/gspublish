
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'gspublish'
VERSION = __import__(PACKAGE).__version__

config = {
    'description': 'Publish PostGIS layers to geoserver',
    'author': 'George Ioannou',
    'url': 'http://github.com/cartologic/gspublish',
    'download_url': 'http://github.com/cartologic/gspublish',
    'author_email': 'gmioannou@cartologic.com',
    'version': VERSION,
    'install_requires': [
		'ConfigParser>=3.5.0',
		'gsconfig>=1.0.8',
        'psycopg2>=2.6.2',
        'pyyaml>=3.12'
	],
    'packages': ['gspublish'],
    'scripts': [],
    'name': 'gspublish',
	'entry_points': {
	    'console_scripts': [
			'gspublish = gspublish.gspublish:main'
		]
	},
}

setup(**config)
