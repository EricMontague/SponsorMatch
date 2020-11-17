"""This module contains helper functions for manipulating
strings.
"""

import functools

# Source - https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
def getattr_nested(obj, attributes):
    """Wrapper around Python's getattr built-in
    that allows for getting arbitrarily nested
    attributes from objects.
    """
    def _getattr(obj, attribute):
        return getattr(obj, attribute)
    return functools.reduce(
        _getattr, [obj] + attributes.split(".")
    )


def setattr_nested(obj, attributes, value):
    """Wrapper around Python's setattr built-in
    that allows for setting arbitrarily nested
    attributes on objects.
    """
    pre, _, post = attributes.rpartition(".")
    setattr(getattr_nested(obj, pre) if pre else obj, post, value)