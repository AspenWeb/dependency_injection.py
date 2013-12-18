#!/bin/sh
python dependency_injection.py
py.test -v tests.py
