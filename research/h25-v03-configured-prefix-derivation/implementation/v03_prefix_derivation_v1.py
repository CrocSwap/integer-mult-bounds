"""Verify only eight literal replacements in the exact reviewed V03 prefix.

Source proposal, Apache-2.0. Preserve original authors and derivation notices.
Pinned gate-value DATA does not confer source/native/funding/runtime admission.
"""
import ast
from v03_integrated_constructor_v2 import GATES, build_control_driver


def _plain(value):
    budget = [0, 0]

    def walk(item, depth):
        budget[0] += 1
        if depth > 24 or budget[0] > 65536:
            raise ValueError('gate tree bound')
        kind = type(item)
        if item is None or kind is bool:
            return
        if kind is int:
            if not -(1 << 64) <= item < (1 << 64):
                raise ValueError('gate integer bound')
            return
        if kind is str:
            budget[1] += len(item)
            if len(item) > 8192 or budget[1] > 524288:
                raise ValueError('gate text bound')
            return
        if kind not in (list, dict) or len(item) > 1024:
            raise ValueError('gate exact JSON domain')
        if kind is dict:
            for key in item:
                if type(key) is not str:
                    raise ValueError('gate exact string key required')
                walk(key, depth + 1)
                walk(item[key], depth + 1)
        else:
            for child in item:
                walk(child, depth + 1)

    walk(value, 0)


def _same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return (set(left) == set(right) and
                all(_same(left[k], right[k]) for k in left))
    if type(left) is list:
        return (len(left) == len(right) and
                all(_same(a, b) for a, b in zip(left, right)))
    return left == right


def verify_configured_prefix(original_bytes, driver_bytes, frozen_gate_values):
    expected = build_control_driver(original_bytes)
    if type(driver_bytes) is not bytes or not 0 < len(driver_bytes) <= 262144:
        raise ValueError('selected driver byte bound')
    _plain(frozen_gate_values)
    if type(frozen_gate_values) is not dict or set(frozen_gate_values) != set(GATES):
        raise ValueError('exact eight frozen gates required')

    tree = ast.parse(driver_bytes, feature_version=(3, 12))
    offsets, position = [], 0
    for line in driver_bytes.splitlines(keepends=True):
        offsets.append(position)
        position += len(line)

    actual, spans = {}, []
    for node in tree.body:
        if (type(node) is ast.Assign and len(node.targets) == 1 and
                type(node.targets[0]) is ast.Name and
                node.targets[0].id in GATES):
            name, value = node.targets[0].id, node.value
            if name in actual:
                raise ValueError('duplicate configured gate')
            pending, count = [(value, 0)], 0
            while pending:
                child, depth = pending.pop()
                count += 1
                if depth > 26 or count > 65536:
                    raise ValueError('literal AST bound')
                pending.extend((part, depth + 1)
                               for part in ast.iter_child_nodes(child))
            actual[name] = ast.literal_eval(value)
            spans.append((
                offsets[value.lineno - 1] + value.col_offset,
                offsets[value.end_lineno - 1] + value.end_col_offset,
            ))

    _plain(actual)
    if set(actual) != set(GATES) or not _same(actual, frozen_gate_values):
        raise ValueError('configured values differ from independently pinned data')
    normalized = driver_bytes
    for start, end in sorted(spans, reverse=True):
        normalized = normalized[:start] + b'None' + normalized[end:]
    if normalized != expected:
        raise ValueError('selected source differs outside eight literal values')
