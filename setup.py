# Copyright the django_alfajor authors and contributors.
# All rights reserved.  See AUTHORS.
# This file is part of 'django_alfajor' and is distributed under the BSD license.
# See LICENSE for more details.
"""\
django_alfajor
-------

Provides access to Alfajor within Django's manage.py test framework.
"""

from setuptools import setup, find_packages


setup(name="django_alfajor",
      version="0.1",
      packages=find_packages(),

      author='Jeff Schwaber',
      author_email='freyley@gmail.com', 

      description='Alfajor functional testing for django',
      keywords='testing test functional integration browser ajax selenium django',
      long_description=__doc__,
      license='BSD',
      url='http://github.com/freyley/django_alfajor/',

      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Browsers',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Quality Assurance',
          ],

      install_requires=[
        'alfajor >= 0.1',
	'nose == 0.11.3',
        ],
      )
