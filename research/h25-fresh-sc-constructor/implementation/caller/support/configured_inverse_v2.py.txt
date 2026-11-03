"""Finite literal-only configuration inverse; no import, exec, compile or loader.

An independently authenticated record binds BOTH the configured image and its
frozen template. Only complete RHS spans of named top-level single assignments
may differ, and every restored RHS is exactly None. No function/class/import or
other byte can change. This authenticates a transform, never its trust origin.
"""
import ast
import hashlib

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ASSIGNMENTS = 128


class ConfigurationInverseError(ValueError):
    pass


def _need(value, message):
    if not value:
        raise ConfigurationInverseError(message)


def _digest(value):
    _need(type(value) is str and len(value) == 64 and all(x in '0123456789abcdef' for x in value),
          'exact configuration digest required')


def _literal(value, budget, depth=0):
    budget[0] += 1
    _need(budget[0] <= 200000 and depth <= 32, 'finite configured literal tree bound')
    kind = type(value)
    if value is None or kind is bool:
        return
    if kind is int:
        _need(value.bit_length() <= 127, 'configuration integer bound')
        return
    if kind is str or kind is bytes:
        _need(len(value) <= 1048576, 'configuration atom bound')
        return
    _need(kind in (tuple, list, dict) and len(value) <= 8192, 'configuration exact literal type')
    if kind is dict:
        for key in value:
            _need(type(key) is str, 'configuration dictionary key type')
    for item in (value.values() if kind is dict else value):
        _literal(item, budget, depth + 1)


def _record(record):
    _need(type(record) is dict and all(type(k) is str for k in record) and
          set(record) == {'module', 'template_sha256', 'configured_sha256', 'assignments'}, 'configuration record schema')
    _need(type(record['module']) is str and record['module'].isidentifier(), 'configuration module name')
    _digest(record['template_sha256']); _digest(record['configured_sha256'])
    assignments = record['assignments']
    _need(type(assignments) is dict and len(assignments) <= MAX_ASSIGNMENTS, 'finite assignment inventory')
    values = {}
    for name, text in assignments.items():
        _need(type(name) is str and name.isidentifier() and type(text) is str and
              0 < len(text) <= MAX_SOURCE_BYTES and '\n' not in text and '\r' not in text and text.isascii(),
              'exact single-line literal replacement required')
        value = ast.literal_eval(text)
        _literal(value, [0])
        values[name] = value
    return values


def _spans(raw, names, template):
    _need(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES, 'configuration source byte bound')
    tree = ast.parse(raw)
    lines = raw.splitlines(keepends=True)
    starts, offset = [], 0
    for line in lines:
        starts.append(offset); offset += len(line)
    spans = {}
    for node in tree.body:
        if type(node) is ast.Assign and len(node.targets) == 1 and type(node.targets[0]) is ast.Name:
            name = node.targets[0].id
            if name in names:
                _need(name not in spans, 'duplicate configured top-level assignment')
                if template:
                    _need(type(node.value) is ast.Constant and node.value.value is None,
                          'only original top-level None declarations can be configured')
                else:
                    _literal(ast.literal_eval(node.value), [0])
                start = starts[node.value.lineno - 1] + node.value.col_offset
                end = starts[node.value.end_lineno - 1] + node.value.end_col_offset
                spans[name] = (start, end)
    _need(set(spans) == set(names), 'configured assignment absent or not a direct top-level name')
    return spans


def verify_configured_source(raw, record):
    """Verify exact configured bytes and whole inverse; return native literals."""
    values = _record(record)
    _need(hashlib.sha256(raw).hexdigest() == record['configured_sha256'], 'configured image differs')
    spans = _spans(raw, values, False)
    restored = raw
    for name, (start, end) in sorted(spans.items(), key=lambda item: item[1][0], reverse=True):
        _need(raw[start:end] == record['assignments'][name].encode('ascii'), 'configured literal bytes differ')
        restored = restored[:start] + b'None' + restored[end:]
    _need(hashlib.sha256(restored).hexdigest() == record['template_sha256'], 'complete configured-to-template byte inverse differs')
    _spans(restored, values, True)
    return values


def render_configured_source(template_raw, record):
    """Pure construction body for parent-owned future assembly; writes no files."""
    values = _record(record)
    _need(hashlib.sha256(template_raw).hexdigest() == record['template_sha256'], 'template image differs')
    spans = _spans(template_raw, values, True)
    raw = template_raw
    for name, (start, end) in sorted(spans.items(), key=lambda item: item[1][0], reverse=True):
        raw = raw[:start] + record['assignments'][name].encode('ascii') + raw[end:]
    verify_configured_source(raw, record)
    return raw
