#!/bin/sh
python dependency_injection.py -v
py.test -v tests.py
