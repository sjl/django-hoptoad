#!/usr/bin/env bash

markdoc build
rsync --delete -az .html/ ~/src/sjl.bitbucket.org/django-hoptoad
hg -R ~/src/sjl.bitbucket.org commit -Am 'django-hoptoad: Update documentation.'
hg -R ~/src/sjl.bitbucket.org push
