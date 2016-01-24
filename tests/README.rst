Tests
=====

To run these tests, check out this code and enter this tests directory and run the following commands:

    $ cd tests/
    $ pip install hitch (or sudo pip install hitch)
    $ hitch init

Note that virtualenv and python 3 must both be installed.

After set up and the first test run is complete, you can run the following to run a test in development mode:

    $ hitch test somefile.test --settings tdd.settings --tags tag1,tag2

Or you can run the full suite of tests from end to end as follows:

    $ hitch test . --settings ci.settings

For more information on hitch, see the documentation at https://hitchtest.readthedocs.org/
