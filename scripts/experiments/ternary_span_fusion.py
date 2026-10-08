#!/usr/bin/env python3
"""Exact common-frame fusion of the certified direct ternary producer.

Default reproduction rebuilds the exact producer and frame audit, then computes
rational source/dual frame classes and F3 boundary ranks. An existing DAG may
be reused only with its matching, current producer certificate. No new kappa
or multiplication assembly witness is asserted by this experiment.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile

if __package__:
    from .ternary_target_certify import ROOT, certificate as producer_certificate, file_hash
else:
    from ternary_target_certify import ROOT, certificate as producer_certificate, file_hash

PROOF_FILES = (
    'scripts/experiments/ternary_span_fusion.py',
    'scripts/experiments/ternary_target_span_classes.cpp',
    'scripts/experiments/ternary_source_span_classes.cpp',
    'scripts/experiments/ternary_boundary_fusion.cpp',
    'scripts/experiments/ternary_reuse_plateaus.py',
    'docs/research/ternary-span-fusion.md',
    'tests/test_ternary_boundary_fusion.py',
)


def run(binary, *args):
    result = json.loads(subprocess.check_output([str(binary), *map(str, args)], text=True))
    result.pop('seconds', None)
    return result


def certificate(workdir=None, producer_path=None, dag_path=None):
    if workdir is None:
        with tempfile.TemporaryDirectory(prefix='ternary-span-fusion-') as temporary:
            return certificate(Path(temporary), producer_path, dag_path)
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    if (producer_path is None) != (dag_path is None):
        raise ValueError('A reused DAG requires its producer certificate')
    if producer_path is None:
        producer = producer_certificate(workdir)
        dag = workdir/'dag-28.bin'
    else:
        producer = json.loads(Path(producer_path).read_text())
        dag = Path(dag_path)
        if producer['dag_sha256'] != file_hash(dag):
            raise ValueError('DAG hash does not match the exact producer certificate')
        for name, digest in producer['proof_sha256'].items():
            if file_hash(ROOT/name) != digest:
                raise ValueError(f'Stale producer proof: {name}')
    if producer['support']['h'] != 28 or producer['global_roles']['current'] != 10365877:
        raise ValueError('This certificate fixes the direct h=28 producer')
    binaries = {}
    for name in ('target_dual', 'target_span_classes', 'source_span_classes', 'boundary_fusion'):
        binary = workdir/f'ternary-{name}'
        source = ROOT/f'scripts/experiments/ternary_{name}.cpp'
        subprocess.run(['c++', '-std=c++17', '-O3', str(source), '-o', str(binary)], check=True)
        binaries[name] = binary
    family_labels, targets = workdir/'family-labels.bin', workdir/'targets.bin'
    dual_labels, all_labels = workdir/'dual-span-labels.bin', workdir/'all-span-labels.bin'
    frames = run(binaries['target_dual'], dag, workdir/'reassigned.txt', family_labels, targets)
    if frames != producer['frames']:
        raise ValueError('Regenerated frame audit differs from the certified producer')
    family_count = run(binaries['boundary_fusion'], dag, family_labels)
    dual_classes = run(binaries['target_span_classes'], dag, targets, dual_labels)
    dual_count = run(binaries['boundary_fusion'], dag, dual_labels)
    source_classes = run(binaries['source_span_classes'], dag, targets, dual_labels, all_labels)
    fused = run(binaries['boundary_fusion'], dag, all_labels)
    if (family_count['saving'], dual_count['saving'], fused['saving']) != (0, 0, 9205):
        raise ValueError('The exact h=28 boundary counts changed')
    if fused['new_roles'] != 10356672:
        raise ValueError('Unexpected fused producer width')
    return dict(
        schema_version=1,
        status='EXACT COMMON-FRAME PRODUCER FUSION; NO NEW ASSEMBLY WITNESS',
        producer=producer,
        family_partition=family_count,
        dual_span_partition=dict(classes=dual_classes, boundary=dual_count),
        source_and_dual_partition=dict(classes=source_classes, boundary=fused),
        global_roles=dict(previous=10365877, current=10356672, saved=9205,
                          center_loss=9828, extra_frame_loss=0),
        exactness=dict(prime=(1 << 61)-1, minor_bound=5**14,
                       row_space_equality='Ranks of A, B and stacked original indicator rows are preserved.',
                       canonical_tuple_equality=True, boundary_field=3,
                       signature='Common intersection and union are intrinsic to each five-set row space.',
                       early_stop='The row rank reaches |union|-|core|, or one for a singleton family.'),
        compiler=dict(roles='v + sum(q_region - rank_F3(M_region))',
                      input_ports='Distinct incoming upstream values.',
                      output_ports='Distinct (value, successor region), plus each designated output use.',
                      quotient='Acyclic source and dual equality quotients joined by the ancestor-closed source-to-dual cut.',
                      frames='Previously certified frames; source and dual regions are kept separate.',
                      dirty_scratch='Invertible rank-maximal local completion and the existing transparent wrapper.'),
        artifact_sha256=dict(dag=file_hash(dag), targets=file_hash(targets),
                             family_labels=file_hash(family_labels), dual_labels=file_hash(dual_labels),
                             all_labels=file_hash(all_labels)),
        proof_sha256={name: file_hash(ROOT/name) for name in PROOF_FILES},
        scope='Exact full-size producer width under the common-frame compiler lemma. '
              'No source/dual frame is changed or mixed across the cut, and no extra descent '
              'is introduced. The multiplication assembly witness is not updated here.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workdir', type=Path)
    parser.add_argument('--producer-certificate', type=Path)
    parser.add_argument('--dag', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'certificates/ternary-span-fusion.json')
    args = parser.parse_args()
    result = certificate(args.workdir, args.producer_certificate, args.dag)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS exact source/dual span fusion:', result['global_roles']['current'],
          'roles;', result['global_roles']['saved'], 'saved; no new assembly witness')
