#!/usr/bin/env python3
"""Compose exact native input roles with authenticated LF/CRLF log comparison.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
Reuses AAAmirinu's PR2344 and Adam Gall's PR2101 predicates unchanged.
"""
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate_vendors():
    rows = json.loads((HERE / 'PREDECESSORS.json').read_bytes())['files']
    require(len(rows) == 11 and len({r['path'] for r in rows}) == 11,
            'predecessor inventory changed')
    for row in rows:
        raw = (HERE / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                'predecessor source changed: ' + row['path'])


def load(name, relative):
    authenticate_vendors()
    spec = importlib.util.spec_from_file_location(name, HERE / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


roles = load('pinned_windows_roles', 'vendor/pr2344/compare_roles.py')
closed = roles.predecessor


def encoded(value):
    """Serialize strict trees exactly, preserving Decimal/integer/Boolean types."""
    kind = type(value)
    if kind is dict:
        require(all(type(k) is str for k in value), 'non-string JSON key')
        text = '{' + ','.join(json.dumps(k) + ':' + encoded(value[k]).decode('ascii')
                              for k in sorted(value)) + '}'
    elif kind is list:
        text = '[' + ','.join(encoded(v).decode('ascii') for v in value) + ']'
    elif kind is Decimal:
        require(value.is_finite(), 'nonfinite decimal')
        text = str(value)
        if '.' not in text and 'e' not in text.lower():
            text += '.0'
    else:
        require(value is None or kind in (str, bool, int), 'unsupported JSON value')
        text = json.dumps(value, ensure_ascii=True, allow_nan=False)
    return text.encode('ascii')


def canonical_log(raw):
    """Permit only CRLF-to-LF conversion, with every other byte retained."""
    require(type(raw) is bytes, 'log must be bytes')
    result = raw.replace(b'\r\n', b'\n')
    require(b'\r' not in result, 'bare carriage return in log')
    return result


def prepare(files, context, outer):
    # Authenticate all original raw links before changing any log or digest.
    adapted, portable_context = roles.adapt(files, context)
    closed.prepare(adapted, portable_context)
    outer_result = closed.outer_log(canonical_log(outer), adapted)
    stages = closed.strict.read_json(adapted['STAGES.json'])
    replay = closed.strict.read_json(adapted['REPLAY.json'])
    updated = dict(adapted)
    for index, name in enumerate(closed.STAGES):
        log_name = name + '.log'
        normalized = canonical_log(files[log_name])
        updated[log_name] = normalized
        digest = closed.digest(normalized)
        stages[index]['log_sha256'] = digest
        replay['stages'][index]['log_sha256'] = digest
    updated['STAGES.json'] = encoded(stages)
    updated['REPLAY.json'] = encoded(replay)
    return updated, portable_context, outer_result


def compare(reference, candidate, reference_context, candidate_context,
            reference_outer, candidate_outer):
    left, left_context, left_outer = prepare(reference, reference_context, reference_outer)
    right, right_context, right_outer = prepare(candidate, candidate_context, candidate_outer)
    require(left_outer == right_outer, 'outer log result differs')
    result = closed.compare(left, right, left_context, right_context)
    result['log_policy'] = 'CRLF to LF only; bare CR rejects; original raw links authenticated first'
    result['normalized_inner_logs_per_side'] = len(closed.STAGES)
    return result
