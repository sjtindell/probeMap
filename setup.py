try:
	from setuptools import setup
except ImportError:
	from disutils.core import setup

config = {
	'description': 'My Project',
	'author': 'sam tindell',
	'url': 'URL to get it at',
	'download_url': 'Where to download it.',
	'author_email': 'sjtindell@gmail',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['src'],
	'scripts': [],
	'name': 'projectname'
}

setup(**config)
