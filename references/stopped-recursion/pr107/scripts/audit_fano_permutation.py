#!/usr/bin/env python3
"""Free-output Fano completions: exact scalar, rigidity, and routing checks."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

from certify import require, verify_sources
from finite_bit_contract import scalar_permutation, physical_graph, check_routing_paths
from routing_smt import paths_from_port_choices
from experiments.fano_completion import clean_prefix, program_hash
from experiments.fano_permuted_completion import LAYOUTS, rows_after, refinement, cases


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'scripts/experiments/fano_permuted_routing_witnesses.json'


def replay(entry, record):
    p = entry['program']
    W, gates = p['W'], p['gates']
    require(record['program_sha256'] == program_hash(p), 'Routing witness program mismatch')
    switches = record['switches']
    require(len(switches) == len(gates) and set(switches) <= {'0', '1'}, 'Malformed switch witness')
    choices = [g['roles'] if b == '0' else list(reversed(g['roles']))
               for g, b in zip(gates, switches)]
    paths = paths_from_port_choices(W, gates, choices)
    return dict(switches=switches, check=check_routing_paths(W, gates, paths))


def partial_bypass(entry):
    """Explicit three-path witness, independent of the full routing fixture.

    Cross only at the forced source/target elimination gates; go straight at
    every other gate. The other roles are not claimed to meet their endpoints.
    """
    require(entry['keep_terminals'], 'Terminal-preserving completion required')
    p = entry['program']
    W, gates = p['W'], p['gates']
    offset = entry['prefix_xors']
    crossings = []
    for c, pivot in enumerate(entry['pivots'][:3]):
        require(pivot['column'] == c and pivot['row'] == 3+c, 'Changed terminal pivots')
        require(c in pivot['targets'], 'Missing forced direct elimination')
        crossing = offset+pivot['targets'].index(c)
        require(gates[crossing]['xors'] == [[c, 3+c]], 'Wrong bypass gate')
        crossings.append(crossing)
        offset += len(pivot['targets'])
    tokens = list(range(W))
    paths = [[] for _ in range(W)]
    edge = 0
    for i, gate in enumerate(gates):
        ports = gate['roles']
        for r in ports:
            paths[tokens[r]].append(edge)
            edge += 1
        if i in crossings:
            x, y = ports
            tokens[x], tokens[y] = tokens[y], tokens[x]
    for r in range(W):
        paths[tokens[r]].append(edge)
        edge += 1
    edges = physical_graph(W, gates)
    used = set()
    for source in range(3):
        at = source
        for e in paths[source]:
            u, v, _ = edges[e]
            require(u == at and e not in used, 'Invalid partial routing')
            used.add(e)
            at = v
        require(at == W+len(gates)+3+source, 'Wrong partial destination')
    return dict(crossing_gates=crossings, paths=paths[:3],
                all_prefix_gates_straight=True, original_three_demands_routable=True)


def certificate():
    rigidity = []
    for name, compact, edge in LAYOUTS:
        p = clean_prefix(compact, edge)
        rows = rows_after(p['W'], p['gates'])
        proof = refinement(rows)
        require(proof['singleton_colors'], 'Compute-map rigidity not established')
        rigidity.append(dict(layout=name, W=p['W'], binary_rows=rows,
                             program_sha256=program_hash(p), refinement=proof,
                             only_permutation_conjugate_is_identity=True))
    fixture = json.loads(FIXTURE.read_text())
    programs = list(cases())
    require(set(fixture) == {name for name, e in programs}, 'Missing or extra routing fixture')
    records = []
    counts = Counter()
    for name, entry in programs:
        p = entry['program']
        rho = scalar_permutation(p['W'], p['gates'])
        moved = [i for i in range(6, p['W']) if rho[i] != i]
        mixed = [i for i in range(6, p['W']) if rho[i] < 6]
        if entry['keep_terminals']:
            require(rho[:3] == (3, 4, 5), 'Original Fano terminal assignments changed')
        routing = replay(entry, fixture[name])
        record = dict(name=name, W=p['W'], rho=list(rho),
                      prefix_xors=entry['prefix_xors'], suffix_xors=entry['suffix_xors'],
                      auxiliary_inputs_moved=moved, auxiliary_inputs_in_data_outputs=mixed,
                      original_terminal_assignments_required=entry['keep_terminals'],
                      program_sha256=program_hash(p), routing=routing,
                      all_rational_frames_excluded=True)
        if entry['keep_terminals']:
            record['bypass'] = partial_bypass(entry)
        records.append(record)
        counts['cases'] += 1
        counts['with_moved_auxiliaries'] += bool(moved)
        counts['with_auxiliary_data_mixing'] += bool(mixed)
        counts['with_prescribed_Fano_terminals'] += entry['keep_terminals']
        counts['routable'] += 1
    sources = ('scripts/audit_fano_permutation.py',
               'scripts/experiments/fano_permuted_completion.py',
               'scripts/experiments/fano_permuted_routing_witnesses.json',
               'scripts/experiments/fano_completion.py', 'scripts/finite_bit_contract.py',
               'scripts/routing_smt.py', 'docs/research/fano-permutation-audit.md')
    return dict(status='144 SPECIFIED FREE-OUTPUT COMPLETIONS ROUTABLE; NO NEW KAPPA',
                upstream_commit=verify_sources(), rigidity=rigidity,
                counts=dict(counts), completed_cases=records,
                solver_required_for_replay=False, improved_frame_certificate_supplied=False,
                source_sha256={s: sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},
                scope='All encoded-register permutations in three fixed compute/permutation/inverse-compute templates; 144 specified Gaussian completions, not all completions or all pivot choices.',
                decision='Do not extend generic decoding searches on these prefixes. Build a balanced all-role topology and its scalar permutation together, preserving a routing obstruction before frame optimization.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/fano-permutation-audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS three rigid compute maps; 144 scalar permutations and full routings; 72 direct bypasses; no new kappa.')
