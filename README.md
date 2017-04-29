## Documentation

Please refer to the [documentation web page](https://dependency-injection-py.readthedocs.org/).

## Running the tests
 
`tox` has to be installed in order to run the tests:

    pip install tox
    
To run the tests:

    tox

If you don't have all the needed Python interpreters installed on your system
but a Docker client available, here you go:

    ./run-tests-with-docker

You can also pass arguments to `tox`, e.g.:
 
    ./run-tests-with-docker -e py26
