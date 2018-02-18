from pytest import raises
from dependency_injection import get_signature, resolve_dependencies, CantUseThis


# get_signature
# ===============

def test_get_signature_infers_defaults():
    def func(foo='bar'): pass
    signature = get_signature(func)
    assert signature.parameters == ('foo',)
    assert signature.required == tuple()
    assert signature.optional == {'foo': 'bar'}


def test_get_signature_returns_empty_dict_for_no_defaults():
    def func(foo, bar, baz): pass
    signature = get_signature(func)
    assert signature.parameters == ('foo', 'bar', 'baz')
    assert signature.required == ('foo', 'bar', 'baz')
    assert signature.optional == {}


def test_get_signature_works_with_mixed_arg_kwarg():
    def func(foo, bar, baz='buz'): pass
    signature = get_signature(func)
    assert signature.parameters == ('foo', 'bar', 'baz')
    assert signature.required == ('foo', 'bar')
    assert signature.optional == {'baz': 'buz'}


def test_get_signature_doesnt_conflate_objects_defined_inside():
    def func(foo, bar, baz=2):
        blah = foo * 42
        return blah
    signature = get_signature(func)
    assert signature.parameters == ('foo', 'bar', 'baz')
    assert signature.required == ('foo', 'bar')
    assert signature.optional == {'baz': 2}


# resolve_dependencies
# ====================

def test_resolve_dependencies_resolves_dependencies():
    def func(foo): pass
    deps = resolve_dependencies(func, {'foo': 1})
    assert deps.signature.parameters == ('foo',)
    assert deps.signature.required == ('foo',)
    assert deps.signature.optional == {}
    assert deps.as_args == (1,)
    assert deps.as_kwargs == {'foo': 1}


def test_resolve_dependencies_resolves_two_dependencies():
    def func(foo, bar): pass
    deps = resolve_dependencies(func, {'foo': 1, 'bar': True})
    assert deps.as_args == (1, True)
    assert deps.as_kwargs == {'foo': 1, 'bar': True}


def test_resolve_dependencies_resolves_kwarg():
    def func(foo, bar=False): pass
    deps = resolve_dependencies(func, {'foo': 1, 'bar': True})
    assert deps.as_args == (1, True)
    assert deps.as_kwargs == {'foo': 1, 'bar': True}


def test_resolve_dependencies_honors_kwarg_default():
    def func(foo, bar=False): pass
    deps = resolve_dependencies(func, {'foo': 1})
    assert deps.as_args == (1, False)
    assert deps.as_kwargs == {'foo': 1, 'bar': False}


def test_resolve_dependencies_honors_kwarg_default_of_None():
    def func(foo, bar=None): pass
    deps = resolve_dependencies(func, {'foo': 1})
    assert deps.as_args == (1, None)
    assert deps.as_kwargs == {'foo': 1, 'bar': None}


def test_resolve_dependencies_doesnt_get_hung_up_on_None_though():
    def func(foo, bar=None): pass
    deps = resolve_dependencies(func, {'foo': 1, 'bar': True})
    assert deps.as_args == (1, True)
    assert deps.as_kwargs == {'foo': 1, 'bar': True}


# Non-Function Callables
# ======================
# https://github.com/gittip/dependency_injection.py/issues/2

def check_callable(cllbl):
    deps = resolve_dependencies(cllbl, {'foo': 1, 'bar': True})
    assert deps.as_args == (1, True)
    assert deps.as_kwargs == {'foo': 1, 'bar': True}


def test_resolve_dependencies_can_work_with_oldstyle___new__():
    class Foo():
        def __new__(cls, foo, bar=None):
            pass
    check_callable(Foo)


def test_resolve_dependencies_can_work_with_newstyle___new__():
    class Foo(object):
        def __new__(cls, foo, bar=None):
            pass
    check_callable(Foo)


def test_resolve_dependencies_can_work_with_oldstyle___init__():
    class Foo():
        def __init__(self, foo, bar=None):
            pass
    check_callable(Foo)


def test_resolve_dependencies_can_work_with_newstyle___init__():
    class Foo(object):
        def __init__(self, foo, bar=None):
            pass
    check_callable(Foo)


def test_resolve_dependencies_can_work_with_oldstyle_class_without___new___or___init__():
    class Foo():
        pass
    deps = resolve_dependencies(Foo, {})
    assert deps.as_args == ()
    assert deps.as_kwargs == {}


def test_resolve_dependencies_can_work_with_newstyle_class_without___new___or___init__():
    class Foo(object):
        pass
    deps = resolve_dependencies(Foo, {})
    assert deps.as_args == ()
    assert deps.as_kwargs == {}


def test_resolve_dependencies_can_work_with_an_unbound_method():
    class Foo(object):
        def method(self, foo, bar=None):
            pass
    check_callable(Foo.method)


def test_resolve_dependencies_can_work_with_a_bound_method():
    class Foo(object):
        def method(self, foo, bar=None):
            pass
    check_callable(Foo().method)


def test_resolve_dependencies_can_work_with___call__():
    class Foo(object):
        def __call__(self, foo, bar=None):
            pass
    check_callable(Foo())


def test_resolve_dependencies_raises_CantUseThis():
    Foo = object()
    value = raises(CantUseThis, resolve_dependencies, Foo, {}).value
    class_str = str(Foo)  # Varies slightly between Python 2 and 3
    assert str(value) == "Sorry, we can't get a signature for {0}.".format(class_str)
