import os
from setuptools import setup, find_packages

setup(
    name='django-hoptoad',
    description='django-hoptoad is some simple Middleware for letting Django-driven websites report their errors to Hoptoad.',
    long_description=open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README')).read(),
    author='Steve Losh',
    author_email='steve@stevelosh.com',
    url='http://stevelosh.com/projects/django-hoptoad/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
    ],
)