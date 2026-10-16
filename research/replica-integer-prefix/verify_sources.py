#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the exact package, external inputs and executable source derivation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root, exclude=()):
    result = {}
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(), 'symlink in authenticated tree')
        if p.is_file():
            name = p.relative_to(root).as_posix()
            if name not in exclude:
                result[name] = sha(p)
    return result


def check():
    expected = read(HERE/'MANIFEST.json')
    need(tree(HERE, ('MANIFEST.json',)) == expected, 'exact package inventory')
    sources = read(HERE/'SOURCES.json')
    live = [r for r in sources['files'] if r['usage'] == 'input']
    for row in live:
        path = ROOT/row['path']
        need(path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink(), 'external input path')
        need(sha(path) == row['sha256'], 'external input SHA256: '+row['path'])
    derivation = read(HERE/'DERIVATION.json')
    need(derivation['source_head'] == 'f1826afe1f487333f2c1e5bf862bae2211ce8dd9', 'derivation predecessor')
    need(sha(HERE/'build_adapter.py') == derivation['builder_sha256'], 'exact adapter generator')
    for record in derivation['changes']:
        source, target = ROOT/record['source'], HERE/record['target']
        need(sha(source) == record['source_sha256'], 'derivation source pin')
        body = source.read_text(encoding='utf8')
        for before, after in record['replacements']:
            need(body.count(before) == 1, 'unique exact patch preimage')
            body = body.replace(before, after)
        need(target.read_bytes() == body.encode('utf8') and sha(target) == record['target_sha256'], 'exact executable derivation')
    independent = HERE/'independent'
    audit = read(independent/'DERIVATION.json')
    originals = {}
    for row in audit['source_copies']:
        source, target = ROOT/row['source'], independent/row['target']
        need(sha(source) == sha(target) == row['sha256'], 'independent copied source pin')
        if row['target'].startswith('source/independent_candidate_'):
            name = 'owners.py' if '_owners_' in row['target'] else 'moment.py'
            originals[name] = target.read_text(encoding='utf8')
    need(set(originals) == set(audit['targets']), 'complete independent derivation')
    for row in audit['changes']:
        body = originals[row['target']]
        need(body.count(row['before']) == 1, 'unique independent patch preimage')
        originals[row['target']] = body.replace(row['before'], row['after'])
    for name, digest in audit['targets'].items():
        need((independent/name).read_bytes() == originals[name].encode('utf8') and
             sha(independent/name) == digest, 'exact independent algorithm derivation')
    construction = read(HERE/'construction/DERIVATION.json')
    body = (HERE/'construction/original_build_p33.py').read_text(encoding='utf8')
    for name, digest in construction['construction_artifacts_sha256'].items():
        need(sha(HERE/'construction'/name) == digest, 'exact allocation support artifact')
    for before, after in construction['changes']:
        need(body.count(before) == 1, 'unique allocation generator preimage')
        body = body.replace(before, after)
    need((HERE/'build_allocation.py').read_bytes() == body.encode('utf8') and
         sha(HERE/'build_allocation.py') == construction['adapted_builder_sha256'], 'exact allocation generator derivation')
    declared = {row['path']:row['sha256'] for row in live}
    need(all(declared.get(row['path']) == row['sha256'] for row in construction['external_inputs']),
         'all allocation generator inputs declared')
    need(sha(HERE/'inputs/PR2833-OUTER-CLAIM.json') == '6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70', 'exact full latest comparison')
    return dict(status='PASS_SOURCE_AND_DERIVATION_BINDINGS',package_files=len(expected),
                external_inputs=len(live),manifest_sha256=sha(HERE/'MANIFEST.json'))


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
