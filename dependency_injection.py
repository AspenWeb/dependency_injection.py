"""This Python library defines a helper for building a dependency injection
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
wants to have the ``bar`` and ``baz`` objects passed into it. What ``bar`` and
``baz`` resolve to depends on the dependency injection framework. This library
provides a helper, :py:func:`~resolve_dependencies`, for building your own
dependency injection framework. It doesn't provide such a framework itself,
because that would take away all the fun.

.. _Dependency injection: http://en.wikipedia.org/wiki/Dependency_injection


Library API
-----------

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from collections import namedtuple


__version__ = '1.0.0rc1'


if sys.version_info >= (3, 0, 0):
    _get_code = lambda f: f.__code__
    _get_defaults = lambda f: f.__defaults__
else:
    _get_code = lambda f: f.func_code
    _get_defaults = lambda f: f.func_defaults


def resolve_dependencies(function, available):
    """Given a function object and a mapping of available dependencies, return a
        :py:class:`namedtuple` that has arguments to suit the function's parameters.

    :param function: a function object (not just a function name)
    :param available: a :py:class:`dict` mapping arbitrary names to objects
    :returns: a :py:class:`namedtuple` representing the arguments to use in calling the function

    The return value of this function is a :py:class:`namedtuple` with these
    attributes:

    0. ``as_args`` - a :py:class:`tuple` of argument values
    1. ``as_kwargs`` - a :py:class:`dict` of keyword arguments
    2. ``signature`` - a :py:class:`namedtuple` as returned by :py:func:`get_signature`

    The ``as_args`` and ``as_kwargs`` arguments are functionally equivalent.
    You could call the function using either one and you'd get the same result,
    and which one you use depends on the needs of the dependency injection
    framework you're writing, and your personal preference.

    This is the main function you want to use from this library. The idea is
    that in your dependency injection framework, you call this function to
    resolve the dependencies for a function, and then call the function. So
    here's a function:

    >>> def foo(bar, baz):
    ...     return bar + baz

    And here's the basics of a dependency injection framework:

    >>> def inject_dependencies(func):
    ...     my_state = {'bar': 1, 'baz': 2, 'bloo': 'blee'}
    ...     dependencies = resolve_dependencies(func, my_state)
    ...     return func(*dependencies.as_args)
    ...

    And here's what it looks like to call it:

    >>> inject_dependencies(foo)
    3

    """
    as_args = tuple()
    as_kwargs = {}
    signature = get_signature(function)

    missing = object()
    for name in signature.parameters:
        value = missing  # don't use .get, to avoid bugs around None
        if name in available:
            value = available[name]
        elif name in signature.optional:
            value = signature.optional[name]
        if value is not missing:
            as_args += (value,)
            as_kwargs[name] = value

    return _Dependencies(as_args, as_kwargs, signature)


def get_signature(function):
    """Given a function object, return a :py:class:`namedtuple` representing the function
        signature.

    :param function: a function object (not just a function name)
    :returns: a :py:class:`namedtuple` representing the function signature

    This function returns a :py:class:`namedtuple` with these items:

    0. ``parameters`` - a :py:class:`tuple` of all parameters, in the order they were defined
    1. ``required`` - a :py:class:`tuple` of required parameters, in the order they were defined
    2. ``optional`` - a :py:class:`dict` of optional parameters mapped to their defaults

    For example, if you have this function:

    >>> def foo(bar, baz=1):
    ...     pass
    ...

    Then :py:func:`get_signature` will return:

    >>> get_signature(foo)
    Signature(parameters=('bar', 'baz'), required=('bar',), optional={'baz': 1})

    This function is a helper for :py:func:`resolve_dependencies`.

    """

    # parameters
    code = _get_code(function)
    parameters = code.co_varnames[:code.co_argcount]

    # optional
    nrequired = len(parameters)
    values = _get_defaults(function)
    optional = {}
    if values is not None:
        nrequired = -len(values)
        keys = parameters[nrequired:]
        optional = dict(zip(keys, values))

    # required
    required = parameters[:nrequired]

    return _Signature(parameters, required, optional)


# Named with leading underscore to suppress documentation.
_Dependencies = namedtuple('Dependencies', 'as_args as_kwargs signature')
_Signature = namedtuple('Signature', 'parameters required optional')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
