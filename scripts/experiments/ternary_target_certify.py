#!/usr/bin/env python3
"""Deterministic direct-producer support and rational-frame certificate.

The default h=28 run needs a C++17 compiler, several GB of memory and roughly
one minute. No fingerprints are accepted as support or span certificates.
Assembly and any claimed multiplication exponent are checked separately.
"""
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_target_fingerprint import export
import intersection_circuit

ROLES = 10365877
PREDECESSOR_ROLES = 11840940
PROOF_FILES = (
    'scripts/experiments/ternary_target_certify.py',
    'scripts/experiments/ternary_target_fingerprint.py',
    'scripts/experiments/ternary_target_fingerprint.cpp',
    'scripts/experiments/ternary_target_exact.cpp',
    'scripts/experiments/ternary_target_dual.cpp',
    'scripts/experiments/intersection_circuit.py',
    'scripts/exclusion_circuit.py',
    'docs/research/ternary-targets.md',
)


def file_hash(path):
    digest = sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def build_checkers(workdir):
    workdir = Path(workdir)
    binaries = {}
    for name in ('exact', 'dual'):
        binary = workdir/f'ternary-target-{name}'
        source = ROOT/f'scripts/experiments/ternary_target_{name}.cpp'
        subprocess.run(['c++', '-std=c++17', '-O3', str(source), '-o', str(binary)], check=True)
        binaries[name] = binary
    return binaries


def exact_run(h, workdir, binaries=None):
    """Run all target-size algebra checks; keep reproducible counts only."""
    if not 8 <= h <= 28:
        raise ValueError('Certified checker supports 8 <= h <= 28')
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    binaries = binaries or build_checkers(workdir)
    # The imported exploratory template permits environment-selected splits.
    # This certificate fixes the half split explicitly, including cached calls.
    intersection_circuit.MODE = 'half'
    intersection_circuit.build.cache_clear()
    plan, dag = workdir/f'plan-{h}.bin', workdir/f'dag-{h}.bin'
    unresolved = workdir/f'dual-reassigned-{h}.txt'
    plan_summary = export(h, plan)
    support = json.loads(subprocess.check_output([str(binaries['exact']), str(plan), str(dag)], text=True))
    frames = json.loads(subprocess.check_output([str(binaries['dual']), str(dag), str(unresolved)], text=True))
    for result in (support, frames):
        result.pop('seconds', None)
    if not support['every_output_family_independently_checked']:
        raise ValueError('Missing independent exact output-family check')
    if not frames['every_final_frame_nondegenerate'] or frames['unresolved_source_nodes']:
        raise ValueError('Final source/dual cut has an unresolved frame')
    if not frames['source_region_ancestor_closed'] or not frames['all_centers_in_source_region']:
        raise ValueError('Frame cut does not preserve the nested-edge proof')
    if support['inputs'] != comb(h, 5) or support['outputs'] != comb(h, 5)+comb(h, 2):
        raise ValueError('Wrong producer dimensions')
    if support['roles'] != support['retained_additions']+support['outputs']:
        raise ValueError('Role accounting mismatch')
    if (frames['positive_source_nodes']+frames['dual_nodes'] !=
            support['inputs']+support['retained_additions']):
        raise ValueError('Frame audit does not cover every active node')
    if h == 28 and (support['roles'] != ROLES or frames['delayed_source_nodes'] != 64):
        raise ValueError('Target-size producer or frame repair changed')
    return dict(plan=plan_summary, support=support, frames=frames,
                plan_sha256=file_hash(plan), dag_sha256=file_hash(dag))


def certificate(workdir=None, h=28):
    """Return a deterministic certificate after rerunning all exact checks."""
    if workdir is None:
        with tempfile.TemporaryDirectory(prefix='ternary-target-') as temporary:
            return certificate(Path(temporary), h)
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    result = exact_run(h, workdir)
    center_loss = comb(h, 2)*(h-2)
    result.update(
        schema_version=1,
        status='CONDITIONAL DIRECT PRODUCER; ASSEMBLY CERTIFIED SEPARATELY',
        predecessor=dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/7',
                         head='6725c6a17b17871a35353fd29157f4ed851bc114',
                         author='Zhihao Chen (jacklightChen)'),
        global_roles=dict(current=result['support']['roles'], center_loss=center_loss,
                          extra_frame_loss=0, retained_totals=comb(h, 2)),
        frame_proof=dict(
            form='I-(2/25)J over Q',
            rational_basis='primitive integer elimination on original five-set indicators',
            nondegeneracy_primes=[1000000007, 1000000009],
            modular_full_rank_is_exact_rational_certificate=True,
            source_rule='Common source core has at least two points, or delayed-cut ancestor.',
            dual_rule='Orthogonal complement of the span of every reachable side target.',
            unresolved_dual_policy='Reassign to exact source span and close source region under ancestors.',
            final_unresolved_frames=0,
            dag_inclusions='Source-source and dual-dual monotonicity; source-dual by exact support orthogonality.',
            endpoint_inclusions='Input lines, target complements, and positive retained pair-total spans.',
            invocation_downward_rank=center_loss),
        proof_sha256={name: file_hash(ROOT/name) for name in PROOF_FILES},
        scope='Exact finite producer coefficients, cancellation-free supports, role count and '
              'nondegenerate rational frames with a proved monotone cut. The physical wrapper, '
              'three tensor stages, retained center losses and assembly use the stated upstream '
              'interfaces; this is not formal verification or an independent assembly witness.')
    if h == 28:
        result['global_roles'].update(previous=PREDECESSOR_ROLES, saved=PREDECESSOR_ROLES-ROLES)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=28)
    parser.add_argument('--workdir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = certificate(args.workdir, args.h)
    output = args.output or ROOT/f'certificates/ternary-target-network{ "" if args.h == 28 else "-h"+str(args.h)}.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS exact direct producer:', result['support']['roles'], 'roles;',
          result['frames']['delayed_source_nodes'], 'delayed source frames;',
          result['frame_proof']['invocation_downward_rank'], 'lost rank per invocation')
