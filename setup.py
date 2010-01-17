import os
from setuptools import setup, find_packages

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst')

setup(
    name='django-hoptoad',
    version='0.3',
    description='django-hoptoad is some simple Middleware for letting '
                'Django-driven websites report their errors to Hoptoad.',
    long_description=open(README_PATH).read(),
    author='Steve Losh',
    author_email='steve@stevelosh.com',
    url='http://sjl.bitbucket.org/django-hoptoad/',
    packages=find_packages(),
    install_requires=['pyyaml'],
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
