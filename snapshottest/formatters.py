import six


class BaseFormatter(object):
    def can_format(self, value):
        raise NotImplementedError()

    def format(self, value, indent, formatter):
        raise NotImplementedError()

    def get_imports(self):
        return ()


class TypeFormatter(BaseFormatter):
    def __init__(self, types, format_func):
        self.types = types
        self.format_func = format_func

    def can_format(self, value):
        return isinstance(value, self.types)

    def format(self, value, indent, formatter):
        return self.format_func(value, indent, formatter)


def format_none(value, indent, formatter):
    return 'None'


def format_str(value, indent, formatter):
    # Snapshots are saved with `from __future__ import unicode_literals`,
    # so the `u'...'` repr is unnecessary, even on Python 2. Avoid multiline
    # representation in tests because `\r\n` is normalized on Python read.
    return repr(value).lstrip('u')


def format_std_type(value, indent, formatter):
    return repr(value)


def format_dict(value, indent, formatter):
    items = [
        formatter.lfchar + formatter.htchar * (indent + 1) + formatter.format(key, indent) + ': ' +
        formatter.format(value[key], indent + 1)
        for key in sorted(value.keys())
    ]
    return '{%s}' % (','.join(items) + formatter.lfchar + formatter.htchar * indent)


def format_list(value, indent, formatter):
    items = [
        formatter.lfchar + formatter.htchar * (indent + 1) + formatter.format(item, indent + 1)
        for item in value
    ]
    return '[%s]' % (','.join(items) + formatter.lfchar + formatter.htchar * indent)


def format_tuple(value, indent, formatter):
    items = [
        formatter.lfchar + formatter.htchar * (indent + 1) + formatter.format(item, indent + 1)
        for item in value
    ]
    return '(%s)' % (','.join(items) + formatter.lfchar + formatter.htchar * indent)


class GenericFormatter(BaseFormatter):
    def can_format(self, value):
        return True

    def format(self, value, indent, formatter):
        # Remove the hex id from `repr`, if found.
        return repr(value).replace(hex(id(value)), "0x100000000")


def default_formatters():
    return [
        TypeFormatter(type(None), format_none),
        TypeFormatter(dict, format_dict),
        TypeFormatter(tuple, format_tuple),
        TypeFormatter(list, format_list),
        TypeFormatter(six.string_types, format_str),
        TypeFormatter((int, float, complex, bool, bytes, set, frozenset), format_std_type),
        GenericFormatter()
    ]
