"""This is a dependency injection library for Python.

Installation
------------

:py:mod:`dependency_injection` is available on `GitHub`_ and on `PyPI`_::

    $ pip install dependency_injection

We `test <https://travis-ci.org/gittip/dependency_injection.py>`_ against
Python 2.6, 2.7, 3.2, and 3.3.

:py:mod:`dependency_injection` is in the `public domain`_.


.. _GitHub: https://github.com/gittip/dependency_injection.py
.. _PyPI: https://pypi.python.org/pypi/dependency_injection
.. _public domain: http://creativecommons.org/publicdomain/zero/1.0/


API
---

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from collections import namedtuple


__version__ = '0.0.0-dev'


if sys.version_info >= (3, 0, 0):
    _get_code = lambda f: f.__code__
    _get_defaults = lambda f: f.__defaults__
else:
    _get_code = lambda f: f.func_code
    _get_defaults = lambda f: f.func_defaults


def parse_signature(function):
    """Given a function, return a tuple of required args and dict of optional args.
    """
    code = _get_code(function)
    varnames = code.co_varnames[:code.co_argcount]

    nrequired = len(varnames)
    values = _get_defaults(function)
    optional = {}
    if values is not None:
        nrequired = -len(values)
        keys = varnames[nrequired:]
        optional = dict(zip(keys, values))

    required = varnames[:nrequired]

    return varnames, required, optional


def resolve_dependencies(function, available):
    """Given a function and a dict of available deps, return a deps object.

    The deps object is a namedtuple with these attributes:

        a - a tuple of argument values
        kw - a dictionary of keyword arguments
        names - a tuple of the names of all arguments (in order)
        required - a tuple of names of required arguments (in order)
        optional - a dictionary of names of optional arguments with their
                     default values

    """
    deps = namedtuple('deps', 'a kw names required optional')
    deps.a = tuple()
    deps.kw = {}
    deps.names, deps.required, deps.optional = parse_signature(function)

    missing = object()
    for name in deps.names:
        value = missing  # don't use .get, to avoid bugs around None
        if name in available:
            value = available[name]
        elif name in deps.optional:
            value = deps.optional[name]
        if value is not missing:
            deps.a += (value,)
            deps.kw[name] = value
    return deps
