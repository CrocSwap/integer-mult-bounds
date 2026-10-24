#!/usr/bin/env python3
"""Exact residual audit of an unchanged source-authenticated Tensor prefix.

Hiroki KUMAZAKI with substantial OpenAI Codex assistance. Apache-2.0.
The physical observation fixture is credited to JoyboyBrian, PR5056; numerical
owners and the source-produced finite catalogue remain Jose Manuel's sources.
"""
import argparse
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'research/tensor-internal-contraction'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def authenticate(path, record):
    need(path.is_file() and not path.is_symlink(), 'regular source: ' + str(path))
    for ancestor in path.parents:
        if ancestor == ROOT:
            break
        need(not ancestor.is_symlink(), 'regular source ancestor')
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == record['sha256'], 'source SHA256 mismatch: ' + str(path))
    blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
    need(sha1(blob).hexdigest() == record['git_blob'], 'source Git blob mismatch: ' + str(path))
    return raw


def sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    records = [r for r in manifest['files'] if r['usage'] == 'input']
    captured = {r['path']: authenticate(ROOT / r['path'], r) for r in records}
    need(len(records) == len(captured) and records, 'nonempty unique input closure')
    with TemporaryDirectory(prefix='expansion-source-control-') as directory:
        test = Path(directory) / 'changed.py'
        record = next(r for r in records if r['path'].endswith('/majorant.py'))
        test.write_bytes(captured[record['path']] + b'\n# changed source\n')
        try:
            authenticate(test, record)
        except ValueError as error:
            need('source SHA256 mismatch' in str(error), 'source control reason')
        else:
            raise ValueError('source mutation accepted')
    return captured


def module_from_bytes(name, path, raw):
    need(name not in sys.modules, 'cold module name: ' + name)
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def natural_axis_record(record, profiles):
    """Undo the source's [K_0,K_1,I_0,I_1] layout, checking all padding.

    This is the bounded two-axis, one-row fixture. The proof states the
    arbitrary-dimensional coordinate contract separately.
    """
    shape = tuple(record['output_shape'])
    need(len(profiles) == len(shape) == 2, 'declared two-axis layout')
    coarse = tuple(p['tiles'] for p in profiles)
    target = tuple(p['t'] for p in profiles)
    inner = tuple(t // k for t, k in zip(target, coarse))
    need(all(t == k * length for t, k, length in zip(target, coarse, inner)),
         'complete coarse and short fields')
    physical = record['physical']
    need(len(physical) == target[0] * target[1], 'full physical target box')
    natural = [None] * (shape[0] * shape[1])
    padding, offset = 0, 0
    for ks in product(*(range(k) for k in coarse)):
        for js in product(*(range(length) for length in inner)):
            i, j = (k * length + short for k, length, short in zip(ks, inner, js))
            value = physical[offset]
            offset += 1
            if i < shape[0] and j < shape[1]:
                position = i * shape[1] + j
                need(natural[position] is None, 'unique natural axis record')
                natural[position] = value
                need(value == record['reference'][position],
                     'full actual intermediate axis equals signed reference')
            else:
                need(value == (0, 0), 'complete untouched-axis zero padding')
                padding += 1
    need(all(value is not None for value in natural), 'complete actual natural axis')
    return natural, {'physical_records': len(physical), 'active_records': len(natural),
                     'zero_padding_records': padding,
                     'physical_sha256': sha256(canonical(physical).encode()).hexdigest(),
                     'natural_sha256': sha256(canonical(natural).encode()).hexdigest()}


def run():
    captured = sources()
    old_cache = sys.pycache_prefix
    old_path = sys.path[:]
    with TemporaryDirectory(prefix='expansion-accuracy-bytecode-') as directory:
        # -B alone does not prevent loading stale bytecode. Every transitive
        # source import in this run gets a new, initially empty namespace.
        sys.pycache_prefix = directory
        try:
            model = module_from_bytes('accuracy_model', HERE / 'accuracy_model.py',
                                      (HERE / 'accuracy_model.py').read_bytes())
            parent = module_from_bytes('retained_expansion_observer', PARENT / 'verify.py',
                                       captured['research/tensor-internal-contraction/verify.py'])
            old_block, old_axis, old_pairs = parent.block, parent.axis, parent.pairs
            summaries, observations = [], []
            pending = []

            def audited_block(data, page):
                retained = old_block(data, page)
                output, trace, summary = model.audit_block(data, page)
                need(output == retained[0], 'independent signed outputs match retained source observations')
                need(trace == retained[1], 'independent five-site trace matches retained source observations')
                summaries.append(summary)
                return retained

            def audited_axis(data, shape, position, profile):
                need(not pending, 'prior physical axis observation consumed')
                output, output_shape = old_axis(data, shape, position, profile)
                record = dict(data=data, shape=shape, position=position, profile=profile,
                              reference=output, output_shape=output_shape)
                observations.append(record)
                pending.append(record)
                return output, output_shape

            def observed_pairs(raw, width):
                values = old_pairs(raw, width)
                if pending:
                    record = pending.pop()
                    p = record['profile']['expansion_pages'][0][1][0]['p']
                    need(width == p + 2, 'actual axis record width')
                    record['physical'] = values
                return values

            # These two aliases are checker-only references. The original
            # Tensor, word/convolution owners, truncations and pages run intact.
            with patch.object(parent, 'block', audited_block), \
                    patch.object(parent, 'axis', audited_axis), \
                    patch.object(parent, 'pairs', observed_pairs):
                physical = parent.physical()
            retained_receipt = json.loads(captured['research/tensor-internal-contraction/RESULT.json'])
            need(canonical(physical) == canonical(retained_receipt['physical']),
                 'unchanged actual prefix and inherited physical controls')
            need(len(observations) == 2 and summaries and not pending,
                 'complete accuracy observations')
            axis_audit, axis_records = model.AxisAudit(), []
            profiles = [record['profile'] for record in observations]
            actual_previous = observations[0]['data']
            for record in observations:
                actual, layout = natural_axis_record(record, profiles)
                need(record['data'] == actual_previous, 'actual computed input of following axis')
                receipt = axis_audit.observe(actual_previous, record['shape'], record['position'],
                                             record['profile'], actual, record['output_shape'])
                receipt['actual_intermediate_layout'] = layout
                axis_records.append(receipt)
                actual_previous = actual
            need(axis_records[1]['omitted_prior_error_distinguished'],
                 'nonzero prior error transport is exercised')
            # A permutation preserves every norm used by the retained check,
            # but must fail our new full intermediate coordinate comparison.
            changed = dict(observations[0])
            changed['physical'] = list(changed['physical'])
            other = next(i for i, value in enumerate(changed['physical'])
                         if value != changed['physical'][0])
            changed['physical'][0], changed['physical'][other] = (
                changed['physical'][other], changed['physical'][0])
            try:
                natural_axis_record(changed, profiles)
            except ValueError as error:
                need('actual intermediate axis' in str(error) or 'zero padding' in str(error),
                     'intermediate permutation control reason')
            else:
                raise ValueError('norm-preserving intermediate permutation accepted')
            return {
                'schema_version': 1,
                'status': 'PASS',
                'sources': {'live_inputs': len(captured), 'source_mutation': 'rejected',
                            'bytecode': 'fresh private namespace before source imports'},
                'physical': physical,
                'accuracy': {
                    'checked_block_reference_calls': len(summaries),
                    'block_residual_records_sha256': sha256(canonical(summaries).encode()).hexdigest(),
                    'first_block': summaries[0],
                    'axis_telescope': axis_records,
                    'intermediate_layout_control': 'norm-preserving coordinate permutation rejected',
                    'controls': model.controls(),
                },
                'scope': 'stored-page exact residuals and conditional source proof; finite reduced halos do not validate production Gaussian accuracy',
            }
        finally:
            sys.pycache_prefix = old_cache
            sys.path[:] = old_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    evidence = run()
    raw = json.dumps(evidence, indent=2, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if args.write_result:
        target.write_text(raw)
    else:
        need(target.read_text() == raw, 'frozen RESULT.json differs')
    print(json.dumps({'status': 'PASS', 'blocks': evidence['physical']['actual_blocks'],
                      'truncations': evidence['physical']['actual_truncations'],
                      'axes': len(evidence['accuracy']['axis_telescope']),
                      'result_sha256': sha256(raw.encode()).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
