==============
MultiNoseTests
==============

.. image:: https://badge.fury.io/py/multinosetests.png
    :target: http://badge.fury.io/py/multinosetests

.. image:: https://travis-ci.org/dealertrack/multinosetests.png?branch=master
    :target: https://travis-ci.org/dealertrack/multinosetests

.. image:: https://coveralls.io/repos/dealertrack/multinosetests/badge.png?branch=master
    :target: https://coveralls.io/r/dealertrack/multinosetests?branch=master

Helper utility to run multiple nosetests suites.
Mostly used for making makefile scripts.

This utility runs multiple nosetest suites and merges their
xml reports using xunitmerge. The advantage of this utility
is that it guarantees that all nosetests suites are executed
even if any of them fails (exit status ``>0``). This is especially
useful if multiple nosetests need to be run in Makefile script
because normally, if any of them will fail, the rest of the
script wont get executed which will skew the nosetests xml
report as well as coverage data which are especially useful
for CI systems such as Jenkins.

Installing
----------

You can install ``multinosetests`` using pip::

    $ pip install multinosetests

Using
-----

You can use the utility via an executable ``multinosetests``::

    $ multinosetests --help
    $ multinosetests "nosetests tests/foo -sv --with-xunit --with-coverage" \
                     "nosetests tests/bar -sv --with-xunit --with-coverage"

Testing
-------

To run the tests you need to install testing requirements first::

    $ pip install -r requirements-dev.txt

Then to run tests, you can use ``nosetests``::

    $ nosetests -sv




History
-------

0.2.2 (2017-07-28)
~~~~~~~~~~~~~~~~~~

* Using wheels for distribution
* Excluding tests from being installed

0.2.1 (2014-08-28)
~~~~~~~~~~~~~~~~~~

* Modified project to use cookiecutter project template

0.2.0 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Added overall test suites test results to print out at the end

0.1.1 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Log output goes to stderr.
  This fixes an issue when ``multinosetests`` is run in CI
  which would result in printing log messages below all test suites.
* Added tests
* Switched to using Python ``setuptools`` entry-points instead of
  binary script

0.1.0 (2014-07-07)
~~~~~~~~~~~~~~~~~~

* Initial release


Credits
-------

This utility was created at `DealerTrack Technologies`_
(`DealerTrack GitHub`_) for our internal use so thank you
DealerTrack for allowing to contribute the utility
to the open-source community.

Development Lead
~~~~~~~~~~~~~~~~

* Miroslav Shubernetskiy - https://github.com/miki725

Contributors
~~~~~~~~~~~~

None yet. Why not be the first?


.. _DealerTrack GitHub: https://github.com/Dealertrack
.. _DealerTrack Technologies: https://www.dealertrack.com


License
-------

The MIT License (MIT)

Copyright (c) 2014 Dealertrack Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


