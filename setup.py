try:
	from setuptools import setup
except ImportError:
	from disutils.core import setup

config = {
	'description': 'Sniff probe requests, google map router names.',
	'author': 'sam tindell',
	'download_url': 'https://github.com/sjtindell/probeMap',
	'author_email': 'sjtindell@gmail.com',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['src', 'tests'],
	'scripts': [],
	'name': 'probeMap'
}

setup(**config)
