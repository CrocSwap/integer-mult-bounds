#!/usr/bin/env python3
"""Stronger rank screens and exhaustive balanced-Fano diagnostic."""
from hashlib import sha256
from pathlib import Path
import json

from audit_joint_frames import eye, matrix, add
from certify import require, verify_sources
from finite_bit_contract import xor_gate
from prepare_layers import serializable
from rank_obstructions import check_fractional_paths, scalar_lift, check_telescope
from experiments.fano_completion import FANO_EDGES
from experiments.balanced_fano import balanced_fano, existence


ROOT = Path(__file__).resolve().parents[1]
FANO_DEMANDS = [('a', 'ta'), ('b', 'tb'), ('c', 'tc')]
FANO_FLOWS = [
    [dict(weight='1/2', edges=[0, 6, 9, 13, 17]), dict(weight='1/2', edges=[1, 15, 12, 10, 11])],
    [dict(weight='1/2', edges=[3, 7, 10, 12, 14, 18, 19]), dict(weight='1/2', edges=[3, 7, 11, 17, 16, 18, 19])],
    [dict(weight='1/2', edges=[5, 9, 6, 0, 1]), dict(weight='1/2', edges=[5, 13, 16, 14, 15])],
]


def lift_control():
    gates = [xor_gate(1, 0), xor_gate(0, 1), xor_gate(1, 0)]
    local = [[[1, 1], [0, 1]], [[1, -1], [0, 1]], [[1, 1], [0, 1]]]
    lifted = scalar_lift(2, gates, local)
    sources = [matrix([[1, 2], [3, 4]]), matrix([[-1, 0], [2, 1]])]
    sinks = [add(sources[1], eye(2)), add(sources[0], eye(2))]
    frames = [matrix([[0, 0], [0, 0]]), matrix([[2, 1], [0, -1]]), matrix([[0, 2], [1, 1]])]
    check = check_telescope(2, gates, local, sources, frames, sinks)
    return dict(gates=gates, local_rational_matrices=local, rho=lifted['rho'],
                transfer=lifted['transfer'], source_frames=sources, gate_frames=frames,
                sink_frames=sinks, check=check)


def certificate():
    flow = check_fractional_paths(FANO_EDGES, FANO_DEMANDS, FANO_FLOWS)
    require(flow['rates'] == [1, 1, 1] and flow['backward_traversals'] > 0, 'Wrong fractional witness')
    model = balanced_fano()
    search = existence(model['W'], model['pairs'], model['prescribed'])
    require(not search['exists'] and search['exhaustive_negative'], 'Unexpected balanced completion')
    require(search['prefix_assignments'] == search['suffix_assignments'] == 279936,
            'Incomplete half enumeration')
    sources = ('scripts/audit_stronger_screens.py', 'scripts/rank_obstructions.py',
               'scripts/experiments/balanced_fano.py', 'scripts/experiments/fano_completion.py',
               'scripts/finite_bit_contract.py', 'docs/research/stronger-rank-screens.md')
    return dict(status='STRONGER NECESSARY SCREENS; BALANCED FANO MODEL EXHAUSTED; NO NEW KAPPA',
                upstream_commit=verify_sources(),
                clean_Fano_undirected_unit_flow=dict(edges=FANO_EDGES, demands=FANO_DEMANDS,
                    flows=FANO_FLOWS, check=flow,
                    scope='Only three clean demands. This does not reject all completions with additional auxiliary demands.'),
                balanced_model=model, exact_scalar_search=search,
                characteristic_zero_control=lift_control(),
                solver_required_for_replay=False,
                completion_paper=dict(url='https://arxiv.org/abs/2610.09367',
                    submission_date='2026-10-07',
                    title='Network Coding Can Beat Routing in Undirected Multiple-Unicast Networks',
                    reviewed='Abstract and section III-B/III-C/III-D, not the complete proof or Lean build',
                    relevance='Integer-valid signed permutation circuits are excluded as-is by the characteristic-zero rank obstruction. Completion discipline may still be useful for characteristic-dependent seeds.'),
                scope='The rejection theorem is general; finite controls test its algebra. The exhaustive scalar exclusion covers the specified 14 two-port gates only, not other Fano topologies or larger local gates.',
                source_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/stronger-rank-screens.json').write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    print('PASS exact undirected half-path flow, characteristic-zero telescoping, and all balanced-Fano local assignments; no new kappa.')
