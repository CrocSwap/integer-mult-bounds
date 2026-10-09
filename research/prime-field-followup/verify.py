"""Exact, reproducible refinement of the attributed PR #7 ternary producer.

Finite checks and conditional arithmetic do not formally verify the retained
prime-field, tape, Gaussian, precision, or multiplication arguments.
"""
from collections import Counter
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import struct
import subprocess
import sys
from types import SimpleNamespace

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[1]
sys.path[:0] = [str(FOLDER), str(FOLDER / 'vendor'), str(ROOT / 'scripts')]
from star_duality import alternative_greedy, check, templates
from prime_field_circuit import export_local, optimize
from prime_field_checks import SmallProducer, scalar_control, frame_control
from certify import Parameters, constraints, margins, verify_sources
from compact_control_layer import layer_exponents
from prepare_layers import serializable
from search_network import log_integer_bounds
from exclusion_circuit import ExclusionCircuit


def provenance():
    result = json.loads((FOLDER / 'provenance.json').read_text())
    for name, entry in result['files'].items():
        assert sha256((FOLDER / 'vendor' / name).read_bytes()).hexdigest() == entry['sha256'], name
    reference = json.loads((FOLDER / 'vendor/prime-field28.json').read_text())
    for name, entry in result['files'].items():
        old = reference.get('proof_sha256', {}).get(entry['upstream_path'])
        if old is not None:
            assert old == entry['sha256'], name
    return result, reference


def reversible_control(targets, gates):
    """Check every F3 basis direction, including dirty scratch, simultaneously."""
    n = max(targets).bit_length()
    support = [0]+[1 << i for i in range(n)]
    args = [None]*len(support)
    ids = {mask: i for i, mask in enumerate(support) if mask}
    for a, b in gates:
        ids[a | b] = len(support)
        support.append(a | b)
        args.append((ids[a], ids[b]))
    outputs = {j: ids[mask] for j, mask in enumerate(targets)}
    graph = SimpleNamespace(inputs=[(i,) for i in range(n)], support=support,
                            args=args, active=set(range(1, len(support))),
                            outputs=outputs, additions=len(gates))
    code = ExclusionCircuit.compile(graph)
    forward = [0]*code['roles']
    for (i,), slot in code['sources'].items():
        forward[slot] = 1 << i
    for node, ins, outs in code['gates']:
        for slot in set(ins+outs):
            assert not forward[slot] & ~support[node]
            forward[slot] = support[node]
    for j, slot in code['outputs'].items():
        assert forward[slot] == targets[j]
    reverse = [0]*code['roles']
    for j, slot in code['outputs'].items():
        reverse[slot] = targets[j]
    for node, ins, outs in reversed(code['gates']):
        for slot in set(ins+outs):
            assert not reverse[slot] or not support[node] & ~reverse[slot]
            reverse[slot] = support[node]
    for (i,), slot in code['sources'].items():
        assert reverse[slot] == 1 << i
    q, roles = len(targets), code['roles']
    width = n+q+roles
    full = (1 << width)-1
    def plus(a, b):
        a0, b0 = full ^ (a[0] | a[1]), full ^ (b[0] | b[1])
        return ((a[0]&b0)|(a0&b[0])|(a[1]&b[1]),
                (a[1]&b0)|(a0&b[1])|(a[0]&b[0]))
    def signed(value, sign):
        return value if sign > 0 else value[::-1]
    for inverse in (False, True):
        z = [(1 << (n+q+i), 0) for i in range(roles)]
        original = list(z)
        y = [(1 << (n+i), 0) for i in range(q)]
        operations = [('L',1),('J',-1),('L',-1),('V',1),
                      ('L',1),('J',1),('L',-1),('V',-1)]
        if inverse:
            operations = [(name,-sign) for name,sign in reversed(operations)]
        for name, sign in operations:
            if name == 'V':
                for (i,), slot in code['sources'].items():
                    z[slot] = plus(z[slot], signed((1 << i, 0), sign))
            elif name == 'J':
                for j, slot in code['outputs'].items():
                    y[j] = plus(y[j], signed(z[slot], sign))
            else:
                for _, ins, outs in (code['gates'] if sign > 0 else reversed(code['gates'])):
                    updates = [(slot, ins[0]) for slot in outs[1:]]
                    additions = [(ins[0], slot) for slot in ins[1:]]
                    steps = additions+updates if sign > 0 else list(reversed(updates))+list(reversed(additions))
                    for destination, source in steps:
                        z[destination] = plus(z[destination], signed(z[source], sign))
        assert z == original
        for j, mask in enumerate(targets):
            expected = (1 << (n+j), mask) if inverse else ((1 << (n+j)) | mask, 0)
            assert y[j] == expected
    return dict(roles=roles, basis_directions_per_orientation=width,
                dirty_scratch_restored=True, both_orientations_exact=True,
                forward_and_reverse_role_supports_nested=True)


def synthesize(demands, destination):
    counts = templates(demands)
    selected = {}
    records = []
    old = new = 0
    for targets, multiplicity in sorted(counts.items()):
        masks = list(targets)
        choices = {'published_greedy': optimize(masks),
                   'large_first': alternative_greedy(masks, large=True),
                   'large_first_reverse': alternative_greedy(masks, large=True, reverse=True)}
        winner = min(choices, key=lambda name: (len(choices[name]), name))
        gates = choices[winner]
        check(masks, gates)
        selected[targets] = gates
        lengths = {name: len(g) for name, g in choices.items()}
        old += multiplicity * lengths['published_greedy']
        new += multiplicity * len(gates)
        encoded = json.dumps([targets, gates], separators=(',', ':')).encode()
        records.append(dict(multiplicity=multiplicity, outputs=len(targets),
                            additions=lengths, winner=winner,
                            reversible_control=reversible_control(targets, gates),
                            circuit_sha256=sha256(encoded).hexdigest()))
    with destination.open('wb') as stream:
        def words(*xs):
            stream.write(struct.pack('<' + 'I'*len(xs), *xs))
        words(28, len(selected))
        for targets, gates in sorted(selected.items()):
            words(len(targets), len(gates), *targets)
            for a, b in gates:
                words(a, b)
    return dict(stars=sum(counts.values()), templates=len(selected),
                published_star_additions=old, selected_star_additions=new,
                saved_additions=old-new,
                winners=dict(Counter(row['winner'] for row in records)),
                template_binary_sha256=sha256(destination.read_bytes()).hexdigest(),
                template_records=records)


def guard(cn, beta, zeta):
    m, s, W = cn['m'], cn['s'], cn['W']
    E = 64*(W+m+1)**3
    B = s+E
    assert m >= 3 and 2 <= s < m**5
    assert s*(8+E) <= 9*B*B
    raw = max(Q(128*m*B*B), 18*m*B*B*(1+1/zeta))
    C0 = -(-raw.numerator//raw.denominator)
    assert 9*m*B*B*(1+1/zeta)+18 <= C0
    assert 36*W**3+4*s+4*W+4 < E
    return dict(E=E, B=B, C0=C0, C1=5-4*beta+zeta, beta=beta, zeta=zeta)


def witness(roles, reference):
    h = int(reference['witness']['bit']['h'])
    v, m = comb(h, 5), h**3
    N = v**3
    W = 2*v*v*(v+roles)
    L = 3*v*v*comb(h, 2)*(h-2)
    D = N-2*L
    assert D > 0
    bn = dict(h=h, v=v, m=m, N=N, W=W, L=L, D=D, s=W*m-D,
              roles=roles, eta=Q(D, W*m))
    # The complex network is the unchanged, conditional PR #7 dependency.
    cn = {key: int(value) for key, value in reference['witness']['complex'].items()
          if key != 'eta'}
    cn['eta'] = Q(reference['witness']['complex']['eta'])
    assert cn['W']*cn['m']-cn['s'] == cn['D']
    ab, ac = Q(761, 10**11), Q(39, 10**9)
    assert bn['eta'] > ab*log_integer_bounds(m)[1]
    assert cn['eta'] > ac*log_integer_bounds(cn['m'])[1]
    p = Parameters(tau=1-ab, sigma=1-ac, epsilon=Q(4999, 10000),
                   c=Q(9999, 10000), lam=1-Q(7609, 10**12),
                   lamp=1-Q(7608, 10**12), kappa=Q(38, 10**10),
                   beta=Q(19, 25), delta=Q(1, 10**6), C1=Q(19601, 10000))
    g = guard(cn, p.beta, Q(1, 10000))
    assert p.C1 == g['C1']
    ex = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    cs = constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    # Exactly the faster-Gaussian interface supplied in eumemic's PR #5.
    for key in ('gaussian_cost', 'dimension_upper_bound', 'alpha_below_sqrt_p', 'gamma_sublinear'):
        del cs[key]
    cs['gaussian_cost'] = 1-p.delta-2*p.epsilon
    cs['alpha_squared_theta_growth'] = 1-2*p.epsilon
    cs['packed_overhead'] = p.lam-ex['internal']
    cs['reserved_axes'] = p.lamp-ex['preprocessing']
    gs = margins(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    gs['g5'] = 1-p.delta-2*p.epsilon
    assert all(value > 0 for value in cs.values())
    assert min(gs.values()) > p.kappa > Q(373, 10**11)
    return dict(parameters=asdict(p), bit=bn, retained_complex=cn, guard=g,
                bit_saving=ab, complex_saving=ac, recurrence=ex, constraints=cs,
                margins=gs, minimum_margin=min(gs.values()),
                absorption_gap=min(gs.values())-p.kappa,
                headline_ratio_to_pr7=p.kappa/Q(373, 10**11))


def certificate():
    pinned, reference = provenance()
    build = ROOT / 'build/prime-field-followup'
    build.mkdir(parents=True, exist_ok=True)
    local = build / 'local.bin'
    demands = build / 'demands.txt'
    regenerated = build / 'rechecked-demands.txt'
    binary = build / 'check'
    selected = build / 'templates.bin'
    local_check = export_local(local)
    subprocess.run(['c++', '-std=c++17', '-O3', str(FOLDER/'vendor/prime_field_supports.cpp'),
                    '-o', str(binary)], check=True)
    first = subprocess.run([str(binary), str(local), '-', str(demands)],
                           check=True, capture_output=True, text=True)
    original = json.loads(first.stdout)
    original.pop('seconds', None)
    search = synthesize(demands, selected)
    second = subprocess.run([str(binary), str(local), '-', str(regenerated), str(selected)],
                            check=True, capture_output=True, text=True)
    repeated, checked = map(json.loads, second.stdout.splitlines())
    repeated.pop('seconds', None)
    assert repeated == original
    assert demands.read_bytes() == regenerated.read_bytes()
    assert checked['new_star_additions'] == search['selected_star_additions']
    old_width = reference['witness']['bit']['roles']
    assert checked['role_upper_bound'] == old_width-search['saved_additions']
    assert search['published_star_additions'] == reference['producer']['replacements']['new_additions']
    small = SmallProducer(8)
    small_controls = dict(map=small.verify_map(), scalar=scalar_control(small),
                          rational_frames=frame_control(small))
    result = dict(status='CONDITIONAL PR #7 REFINEMENT; NOT INDEPENDENT MATHEMATICAL REVIEW OR FORMAL VERIFICATION',
                  provenance=pinned, upstream_commit=verify_sources(),
                  local=local_check, global_before_replacement=original,
                  selected_templates=search, independent_cpp_check=checked,
                  retained_small_controls=small_controls,
                  witness=witness(checked['role_upper_bound'], reference),
                  scope='New checked monotone star templates and exact conditional assembly. '
                        'The small controls recheck the inherited scalar/rational schedule; '
                        'they do not enumerate the full modified h28 network. '
                        'The PR #7 prime-field transfer and complex network, PR #5 Gaussian '
                        'argument, compact-control interfaces, and upstream multiplication '
                        'theorem remain mathematical assumptions. No integrated manuscript patch.')
    names = ['star_duality.py', 'verify.py', 'provenance.json']
    result['source_sha256'] = {name: sha256((FOLDER/name).read_bytes()).hexdigest() for name in names}
    dependencies = ['scripts/certify.py', 'scripts/search_network.py', 'scripts/prepare_layers.py',
                    'scripts/compact_control_layer.py', 'scripts/exclusion_circuit.py',
                    'scripts/paired_exclusion_circuit.py']
    result['retained_source_sha256'] = {name: sha256((ROOT/name).read_bytes()).hexdigest() for name in dependencies}
    return serializable(result)


if __name__ == '__main__':
    result = certificate()
    (FOLDER/'certificate.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS complete h28 producer and all replacement template boundaries')
    print('Saved additions:', result['selected_templates']['saved_additions'])
    print('Conditional kappa:', result['witness']['parameters']['kappa'])
    print('Strict absorption gap:', result['witness']['absorption_gap'])
