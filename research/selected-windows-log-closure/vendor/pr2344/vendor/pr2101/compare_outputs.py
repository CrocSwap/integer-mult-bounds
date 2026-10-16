#!/usr/bin/env python3
"""Closed PR1094 final-output caller for the pinned PR2040/PR2059 predicates.

All 105 output files are compared. Only two authenticated invoice links, six
exact input-path roles, and 22 stage-time fields receive normalization.
Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_vendor(name):
    records = json.loads((HERE / 'SOURCES.json').read_bytes())['vendored_sources']
    record = next(row for row in records if row['path'] == 'vendor/' + name + '.py')
    path = HERE / record['path']
    require(digest(path.read_bytes()) == record['sha256'], 'vendored source drift: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


strict = load_vendor('strict_compare')
invoice = load_vendor('invoice_compare')
POLICY = json.loads((HERE / 'POLICY.json').read_bytes())
NAMES = frozenset(POLICY['files'])
STAGES = POLICY['stages']


def read_files(directory):
    return {name: path.read_bytes() for name, path in strict.inventory(directory).items()}


def prepare(files, context):
    """Validate per-side raw edges before any equality or representation quotient.

    context contains logical work/local roots and exactly three actual external
    input byte strings. No filesystem path from a receipt is followed.
    Other digest fields remain literal, not inferred graph edges.
    """
    require(set(files) == NAMES, 'complete 105-file inventory differs')
    require(set(context) == {'work', 'local', 'external'}, 'invalid comparison context')
    strict.Roots([('work', context['work']), ('local', context['local'])])
    external = context['external']
    require(set(external) == {'local-word', 'local-replay', 'owners'}, 'external role set differs')
    stages = strict.read_json(files['STAGES.json'])
    replay = strict.read_json(files['REPLAY.json'])
    require(type(stages) is list and len(stages) == len(STAGES), 'stage inventory differs')
    require(type(replay) is dict and 'stages' in replay, 'missing replay stage binding')
    require(strict.tree(stages) == strict.tree(replay['stages']), 'stage receipts disagree')
    for name, paths in POLICY['timings'].items():
        strict.validate_timings(stages if name == 'STAGES.json' else replay, paths)
    for expected, stage in zip(STAGES, stages):
        require(type(stage) is dict and stage.get('name') == expected, 'stage order differs')
        require(type(stage.get('exit_code')) is int and stage['exit_code'] == 0, 'stage did not pass')
        require(type(stage.get('log_sha256')) is str and
                stage['log_sha256'] == digest(files[expected + '.log']), 'stale stage log: ' + expected)
    independent = strict.read_json(files['INDEPENDENT-T16.json'])
    require(type(independent) is dict and type(independent.get('input_sha256')) is dict,
            'missing independent input roles')
    expected_inputs, rebound = {}, {}
    for role in POLICY['input_roles']:
        path = context[role['root']] + '/' + role['suffix']
        raw = files[role['target']] if 'target' in role else external[role['external']]
        expected_inputs[path] = digest(raw)
        rebound[role['root'] + ':' + role['suffix']] = digest(raw)
    require(len(expected_inputs) == 6 and
            strict.tree(independent['input_sha256']) == strict.tree(expected_inputs),
            'stale, missing, or misbound independent input role')
    independent['input_sha256'] = rebound
    # Reuse the three-node predecessor unchanged; it authenticates both links
    # before rebinding and retains the complete invoice and consumer payloads.
    replacements = invoice.normalized({name: files[name] for name in invoice.FILES})
    # This receipt's pinned schema is integer/string/Boolean JSON, like the
    # invoice domain. Reparse through that domain before its serialization.
    independent = invoice.parse(json.dumps(independent).encode('utf-8'))
    replacements['INDEPENDENT-T16.json'] = invoice.canonical(independent)
    return replacements


def compare(reference, candidate, reference_context, candidate_context):
    left = prepare(reference, reference_context)
    right = prepare(candidate, candidate_context)
    result = {}
    for name in sorted(NAMES):
        result[name] = strict.classify(name, left.get(name, reference[name]),
                                       right.get(name, candidate[name]),
                                       timing_paths=POLICY['timings'].get(name, ()))
    return {'equivalent': all(strict.accepted(row) for row in result.values()),
            'files': result, 'checked_files': len(result),
            'authenticated_raw_edges_per_side': 30,
            'normalized_invoice_edges_per_side': 2,
            'relocated_input_roles_per_side': 6,
            'permitted_stage_timing_fields_per_side': 22}


def outer_log(raw, files):
    """Check all 13 lines and bind all printed times to the same-side receipt."""
    lines = raw.decode('utf-8').splitlines()
    require(raw.endswith(b'\n') and len(lines) == 13, 'outer log inventory differs')
    stages = strict.read_json(files['STAGES.json'])
    for index, name in enumerate(STAGES):
        fields = lines[index].split(' ')
        require(len(fields) == 3 and fields[:2] == ['PASS', name], 'outer log stage differs')
        seconds = Decimal(fields[2])
        require(seconds.is_finite() and seconds >= 0 and seconds == stages[index]['seconds'],
                'outer log timing differs from its receipt')
    expected = ['PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY 0.001672660197076918',
                'PASS_T16_RARE_PATTERN_EXCHANGES 0.001672660197076918']
    require(lines[11:] == expected, 'outer log final result differs')
    return [*('PASS ' + name for name in STAGES), *expected]
