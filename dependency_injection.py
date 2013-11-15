"""This Python library defines helpers for building a dependency injection
framework.


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


What is Dependency Injection?
-----------------------------

When you define a function you specify its *parameters*, and when you call the
function you pass in *arguments* for those parameters. `Dependency injection`_
means dynamically passing arguments to a function based on the parameters it
defines.  So if you define a function:

    >>> def foo(bar, baz):
    ...     pass


Then you are advertising to a dependency injection framework that your function
wants to have ``bar`` and ``baz`` objects passed into it. What ``bar`` and
``baz`` resolve to depends on the dependency injection framework. This library
provides two helpers for building your own dependency injection framework. It
doesn't provide such a framework itself.

.. _Dependency injection: http://en.wikipedia.org/wiki/Dependency_injection


Library API
-----------

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


def resolve_dependencies(function, available):
    """Given a function object and a :py:class:`dict` of available dependencies, return a
        :py:class:`namedtuple` that has arguments to suit the function's parameters.

    :param function: a function object (not just a function name)
    :param available: a :py:class:`dict` mapping arbitrary names to objects
    :returns: a :py:class:`namedtuple`, the arguments to use in calling the function

    The return value of this function is a :py:class:`namedtuple` with these
    attributes:

    0. ``a`` - a tuple of argument values
    1. ``kw`` - a dictionary of keyword arguments
    2. ``signature`` - a :py:class:`namedtuple` as returned by :py:func:`get_signature`

    The ``a`` and ``kw`` arguments are functionally equivalent. You could call
    the function using either one and you'd get the same result.

    """
    dependencies = namedtuple('Dependencies', 'a kw signature')
    dependencies.a = tuple()
    dependencies.kw = {}
    dependencies.signature = get_signature(function)

    missing = object()
    for name in dependencies.signature.parameters:
        value = missing  # don't use .get, to avoid bugs around None
        if name in available:
            value = available[name]
        elif name in dependencies.signature.optional:
            value = dependencies.signature.optional[name]
        if value is not missing:
            dependencies.a += (value,)
            dependencies.kw[name] = value
    return dependencies


def get_signature(function):
    """Given a function object, return a :py:class:`namedtuple` representing the function
        signature.

    :param function: a function object (not just a function name)
    :returns: a three-:py:class:`tuple`

    This function returns a :py:class:`namedtuple` with these items:

    0. ``parameters`` - a :py:class:`tuple` of all parameters, in the order they were defined
    1. ``required`` - a :py:class:`tuple` of required parameters, in the order they were defined
    2. ``optional`` - a :py:class:`dict` of optional parameters mapped to their defaults

    For example, if you have this function:

    >>> def foo(bar, baz=1):
    ...     pass
    ...

    Then :py:func:`~dependency_injection.get_signature` will return:

    >>> get_signature(foo)
    (('bar', 'baz'), ('bar',), {'baz': 1})

    """
    out = namedtuple('Signature', 'parameters required optional')

    # parameters
    code = _get_code(function)
    out.parameters = code.co_varnames[:code.co_argcount]

    # optional
    nrequired = len(out.parameters)
    values = _get_defaults(function)
    out.optional = {}
    if values is not None:
        nrequired = -len(values)
        keys = out.parameters[nrequired:]
        out.optional = dict(zip(keys, values))

    # required
    out.required = out.parameters[:nrequired]

    return out


if __name__ == '__main__':
    import doctest
    doctest.testmod()
