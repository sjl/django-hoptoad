
django-hoptoad
==============

django-hoptoad is some simple Middleware for letting Django_-driven websites report their errors to Hoptoad_.  Now ponies_ can ride the toad too.

.. _Django: http://djangoproject.com/
.. _Hoptoad: http://hoptoadapp.com/
.. _ponies: http://djangopony.com/


Requirements
------------

django-hoptoad requires:

* Python_ 2.5+ (preferably 2.6+ as that's what I've tested it with)
* PyYAML_ (`pip install pyyaml` or `easy_install pyyaml`)
* Django_ 1.0+
* A Hoptoad_ account

.. _Python: http://python.org/
.. _PyYAML: http://pyyaml.org/


Installation
------------

Grab the the django-hoptoad code by cloning the Mercurial_ repository (or just `download the latest version <http://bitbucket.org/sjl/django-hoptoad/get/tip.zip>`_ and unzip it somewhere)::

    hg clone http://bitbucket.org/sjl/django-hoptoad/

There's a git mirror too if you *really* want it::

    git clone git://github.com/sjl/django-hoptoad.git

Once you download it, you can install it in the usual manner::

    cd django-hoptoad
    python setup.py install

If you'd prefer to be able to update at any time by pulling down changes with Mercurial or git, you can symlink the module into your ``site-packages`` directory instead of using ``python setup.py install``::

    ln -s /full/path/to/django-hoptoad/hoptoad /full/path/to/site-packages/

To make sure it works you can run::

    python -c 'import hoptoad'

.. _Mercurial: http://mercurial.selenic.com/


Usage
-----

To set up a Django project to notify Hoptoad of its errors, you need to do two things in its `settings.py` file.

First, add the ``HoptoadNotifierMiddleware`` as the last item in the ``MIDDLEWARE_CLASSES``` setting::

    MIDDLEWARE_CLASSES = (
        # ... other middleware classes ...
        'hoptoad.middleware.HoptoadNotifierMiddleware',
    )

Next, you'll need to add a ``HOPTOAD_API_KEY`` setting.  You can get the key from the Hoptoad project page::

    HOPTOAD_API_KEY = 'Your Hoptoad API key.'


Documentation
-------------

The documentation for django-hoptoad is at the `project page <http://sjl.bitbucket.org/django-hoptoad/>`_. There's a `Quick Start guide <http://sjl.bitbucket.org/django-hoptoad/quickstart/>`_, `Configuration guide <http://sjl.bitbucket.org/django-hoptoad/config/>`_, `Troubleshooting guide <http://sjl.bitbucket.org/django-hoptoad/troubleshooting/>`_, and a few other things there.

The documentation is stored in the ``docs/`` directory of the repository if you prefer to read it offline.


Suggestions
-----------

This Middleware is a work in progress.  If you have a suggestion or find a bug please `add an issue <http://bitbucket.org/sjl/django-hoptoad/issues/?status=new&status=open>`_ and let me know.
