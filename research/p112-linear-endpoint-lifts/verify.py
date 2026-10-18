#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify source-bound premises and exact accounting for the endpoint theorems."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from fractions import Fraction as Q

from accounting import GLOBAL, check_global, check_local
from arithmetic import moment
from controls import run as controls
from geometry import model, require, verify_graph_certificate

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/'
MEMBERS = {
    'word': PREFIX + 'base/providers/gauge44/CANONICAL-WORD.json.gz',
    'programs': PREFIX + 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
    'phases': PREFIX + 'base/work/complex-nine-native/DATA-PHASES.json',
    'template': PREFIX + 'hosted/GLOBAL-TEMPLATE.json.gz',
    'idle_frames': PREFIX + 'hosted/IDLE-REMAINDER-FRAMES.json.gz',
}


def source_bytes(name, sources):
    row = next(x for x in sources['files'] if x['path'] == name)
    data = subprocess.check_output(['git', 'show', sources['base_commit'] + ':' + name], cwd=ROOT)
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: ' + name)
    return data


def load_inputs(sources, certificate):
    raw = source_bytes(ARCHIVE, sources)
    inputs = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        for key, name in MEMBERS.items():
            data = archive.extractfile(name).read()
            require(hashlib.sha256(data).hexdigest() == certificate['archive_members'][name],
                    'archive member SHA256: ' + name)
            inputs[key] = json.loads(gzip.decompress(data) if name.endswith('.gz') else data)
    return inputs


def enclosure(low, high):
    scale = 10 ** 55
    return [str(Q((low * scale).numerator // (low * scale).denominator, scale)),
            str(Q(-((-high * scale).numerator // (-high * scale).denominator), scale))]


def verify():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    certificate = json.loads((PACKAGE / 'CERTIFICATE.json').read_text())
    inputs = load_inputs(sources, certificate)
    word, programs = inputs['word'], inputs['programs']
    labels, form, edges = model(word['ports'])
    graph = verify_graph_certificate(certificate, labels, form, edges)
    local = check_local(word, programs)
    global_bill = check_global(**inputs)
    selected = json.loads(source_bytes('research/community-frontier1094-audit/ASSEMBLY.json', sources))
    require({int(k): v for k, v in selected['complex_profile'].items()} == GLOBAL,
            'selected assembly profile')
    selected_manifest = json.loads(source_bytes(
        'research/community-frontier1094-audit/SELECTED-SOURCE.json', sources))
    bindings = {}
    for name in ('research/gauge44-slots-t16/code/audit_allcold.py',
                 'research/gauge44-slots/code/invoice_allcold.py',
                 'research/gauge44-slots/independent/audit_local.py'):
        digest = hashlib.sha256(source_bytes(name, sources)).hexdigest()
        require(selected_manifest['files'][name] == digest, 'selected code binding')
        bindings[name] = digest
    frame_note = hashlib.sha256(source_bytes('notes/general-clifford-frames.tex', sources)).hexdigest()
    require(frame_note == selected_manifest['files'][
        'research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/'
        'vendor/multicold/vendor/pr559/notes/general-clifford-frames.tex'], 'selected frame lemma binding')
    b_low = Q(selected['complex_lower'])
    b_high = b_low + Q(1, 10 ** 24)
    at_low, at_high = moment(GLOBAL, 73, 14336, b_low), moment(GLOBAL, 73, 14336, b_high)
    require(at_low[1] < 1 < at_high[0], 'exact complex root bracket')
    next_kappa = Q(selected['kappa']) + Q(1, 10 ** 18)
    ideal_cap = b_high / (1 + b_high)
    require(ideal_cap < next_kappa, 'next outer kappa grid point excluded')
    report = {
        'status': 'PASS_P112_ENDPOINT_DIMENSION_AND_LINEAR_LIFT_OBSTRUCTION',
        'base_commit': sources['base_commit'], 'graph': graph,
        'local_minimum_ranks': local, 'global_accounting': global_bill,
        'selected_source_code_sha256': bindings, 'frame_distance_lemma_sha256': frame_note,
        'moment': {'b_low': str(b_low), 'b_high': str(b_high),
                   'at_low_minus_one': enclosure(at_low[0] - 1, at_low[1] - 1),
                   'at_high_minus_one': enclosure(at_high[0] - 1, at_high[1] - 1)},
        'outer': {'selected_kappa': selected['kappa'], 'excluded_next_grid': str(next_kappa),
                  'optimistic_complex_cap': str(ideal_cap),
                  'retained_raw_bit_lower': selected['bit_lower'],
                  'scope': 'The complex necessary condition alone excludes the next selected grid point. The bit and finite-invoice conditions can only restrict it further.'},
        'controls': controls(certificate, word, programs),
        'proof_scope': 'All-size handwritten proofs use the checked finite graph premises and frame-distance lemma. No proof-assistant formalization or fresh cold replay is claimed.',
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write the checked report to this path.')
    args = parser.parse_args()
    report = verify()
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads((PACKAGE / 'RESULT.json').read_text())
        require(json.loads(json.dumps(report)) == expected, 'stored report mismatch')
    print(report['status'])
    print('tensor_rank=80; arbitrary_two_plane_dimension=18; local_edges=3494 per orientation; idle_edges=7526')
    print('exact_complex_bracket=PASS; next_kappa_grid=EXCLUDED; controls=PASS')


if __name__ == '__main__':
    main()
