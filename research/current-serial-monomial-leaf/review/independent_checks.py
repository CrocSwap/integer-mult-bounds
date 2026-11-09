"""Complementary review checks; not a second physical provider replay.

The integer geometry and signed-pair oracles are independent of the package
checkers. Only emitted finite table inspection imports the implementation.
Prepared by the compiler-owned review agent, with OpenAI assistance.
"""
from pathlib import Path
import ast
import hashlib
import importlib.util
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import column_view as cv


def require(ok, message):
    if not ok:
        raise AssertionError(message)


SCHEMA = ('outer', 'rows', 'stock', 'row_bits', 'within_bits', 'record_bits',
          'p', 'd', 'K', 'G', 'H', 'q0', 'qF', 'qB', 'D', 'f', 'rho',
          'active_start', 'back_start', 'selected_axes', 'entry_start',
          'remainder', 'cutoff')
USED = {'outer', 'rows', 'row_bits', 'within_bits', 'record_bits', 'd', 'K',
        'G', 'H', 'f', 'rho', 'active_start', 'back_start', 'selected_axes',
        'remainder'}
require(tuple(cv.ROLES) == SCHEMA, 'exact 23 field order')
require(len(set(cv.ROLES.values())) == 23, 'separate decoded field ports')
require(len(cv.PRIVATE) == 45 and cv.PARENT not in cv.PRIVATE,
        'all 45 private roles include current child view')
require(not set(cv.ROLES.values()) & {cv.FBOUND, cv.OLD_K, cv.COLUMN,
                                    cv.ACC, cv.SUM, cv.M},
        'iteration temporaries cannot clobber retained fields')
tree = ast.parse((ROOT/'vendor/monomial/phase_adapter.py').read_text())
consumer_fields = {n.slice.value for n in ast.walk(tree)
    if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
    and n.value.id == 'header' and isinstance(n.slice, ast.Constant)
    and isinstance(n.slice.value, str)}
# Eight positive checks use a fixed name tuple, so add those semantic reads.
consumer_fields |= {'outer', 'rows', 'row_bits', 'record_bits', 'f', 'K', 'G', 'H'}
require(consumer_fields == USED, 'reviewed exact consumer field set')


def inspect_table(table):
    for row in table:
        op = row[0]
        require(op in {'read','write','move','goto','done','result','reject','quarantine'},
                'closed local instruction set')
        if op in {'read','write','move'}:
            require(type(row[1]) is int and 0 <= row[1] < 46, 'fixed port domain')
        targets = list(row[2].values()) if op == 'read' else [row[1]] if op == 'goto' else []
        require(all(type(t) is int and 0 <= t < len(table) for t in targets),
                'all jump targets within immutable table')
        if op == 'read':
            require(set(row[2]) == {'0','1','_','|'}, 'complete local symbol cases')
        if op == 'write':
            require(row[1] != cv.PARENT and row[2] in {'0','1','_'},
                    'parent and every origin marker immutable')
        if op == 'move':
            require(row[2] in {-1,1}, 'only unit movement')
        if op == 'result':
            require(row[1] in {'ready','finished'}, 'finite external branch alphabet')
    return len(table)


table_sizes = []
for rank in range(1,74):
    table_sizes.append(inspect_table(cv.compile_prepare(rank)))
next_size, release_size = inspect_table(cv.NEXT), inspect_table(cv.RELEASE)
controls = []
for label, table in [('parent-write', [('write',cv.PARENT,'1'),('done',)]),
                     ('outside-jump', [('goto',2),('done',)])]:
    try:
        inspect_table(table)
    except AssertionError:
        controls.append(label)
    else:
        raise AssertionError('static failure detector did not reject '+label)


def enc_len(values):
    return sum(2*max(1, values[name].bit_length())+1 for name in SCHEMA)


geometries = views = selected_positions = 0
max_child_parent_ratio = 0
for m,f,K,G,slack in itertools.product((1,2,9,73),(1,2,3,7),(1,2,5),(1,3),(0,2)):
    for rho in sorted({0,K-1}):
        for e in sorted({0,m-1}):
            H = max(1,(f-1)*G)+slack
            u = 2*H + e*K + slack
            z = u + m*f*K + slack
            a = z + H + slack
            h, r, C = 5, 3, 6
            b = 6*r*(h+1)
            parent = dict(outer=2, rows=3, stock=7, row_bits=b<<a,
                within_bits=a, record_bits=b, p=max(m*f+e,2), d=m*f+e,
                K=K, G=G, H=H, q0=5, qF=6, qB=7, D=m*f+e,
                f=f, rho=rho, active_start=u, back_start=z,
                selected_axes=m*f+e, entry_start=u-e*K, remainder=e,
                cutoff=3*m*f)
            all_parent = {u+(i*f+j)*K+rho for i in range(m) for j in range(f)}
            seen = set()
            for j in range(f):
                child = dict(parent, f=1,K=f*K,rho=j*K+rho,selected_axes=m+e)
                require(all(child[k] == parent[k] for k in SCHEMA
                            if k not in {'f','K','rho','selected_axes'}), '19 unchanged fields')
                require(0 <= child['rho'] < child['K'] and child['f'] == 1,
                        'one-column residue admission')
                require(child['selected_axes'] == m*child['f']+e <= child['d']
                        and 0 <= e < m, 'rank/remainder admission')
                compact = (child['f']-1)*G
                before = u-2*H
                after = z-u-m*child['f']*child['K']
                suffix = a-z-compact
                widths = [compact,H-compact,compact,H-compact,before] + [child['f']*child['K']]*m + [after,compact]
                require(all(v >= 0 for v in widths) and a-z >= H and suffix >= 0,
                        'all encoded subtractions and suffix admission')
                require(sum(widths) == z, 'complete one-column enumerated address extent')
                require((C<<sum(widths))*(2*h*r<<suffix) == (C*2*h*r<<a),
                        'complete field volume unchanged after suffix folding')
                position = {u+i*child['K']+child['rho'] for i in range(m)}
                expected = {u+(i*f+j)*K+rho for i in range(m)}
                require(position == expected and not seen & position,
                        'exact disjoint tensor factors, preserving all spectator bits')
                seen |= position
                require(enc_len(child) <= 2*enc_len(parent)+10, 'finite encoded size sanity')
                max_child_parent_ratio=max(max_child_parent_ratio,enc_len(child)/enc_len(parent))
                views += 1
                selected_positions += len(position)
            require(seen == all_parent, 'all parent selected factors covered once')
            require((f-1)*G <= H and 2*H <= u and u+m*f*K <= z and z+H <= a,
                    'test domain is admitted parent geometry')
            geometries += 1

# This is an interface discriminator, not an error: an unused producer identity
# need not hold in the private consumer view.
e,K,f,u = 1,2,3,9
entry = u-e*K
require(entry+e*(f*K) != u, 'private header must not be advertised as generic producer descriptor')
u,i,f,j,K,rho = 9,2,3,1,2,1
require(u+(i*f+j)*K+rho != u+i*K+j*K+rho,
        'unscaled stride negative control')
controls.append('unscaled-private-stride')


def rotate(z, phase):
    x,y=z
    return ((x,y),(-y,x),(-x,-y),(y,-x))[phase%4]


signed_pairs = strict_pairs = 0
for h in range(2,9):
    low, high = -(1<<(h-1)), (1<<(h-1))-1
    for x in range(low,high+1):
        for y in range(low,high+1):
            for p in range(4):
                a,b=rotate((x,y),p)
                admissible = low <= a <= high and low <= b <= high
                formula = (p == 0 or p == 1 and y != low
                           or p == 2 and x != low and y != low
                           or p == 3 and x != low)
                require(admissible == formula, 'exact signed phase iff')
                if x != low and y != low:
                    require(admissible and a != low and b != low,
                            'strict symmetric signed domain invariant')
                signed_pairs += 1
            strict_pairs += x != low and y != low
for h in range(2,21):
    low,high=-(1<<(h-1)),(1<<(h-1))-1
    z=(low,0)
    require(rotate(z,2*2)==z and rotate(z,2)[0]>high,
            'constant-2 two-column batched/serial domain counterexample')
    first=rotate(z,1)
    second=rotate(first,1)
    require(all(low<=a<=high for a in first) and second[0]>high and rotate(z,4)==z,
            'actual constant-1 four-column late failure, batched endpoint fits')
controls += ['batched-admission-does-not-imply-intermediate-admission',
             'late-quarter-turn-overflow', 'missing-tensor-constant']
require((2*2)%4 != 2%4, 'tensor phase control separates per-column and one-time constant')

report = dict(status='PASS_INDEPENDENT_SMALL_CHECKS',
    methods={'geometry':'direct integer identities; no package oracle import',
             'signed':'direct complex signed-pair permutation; no phase implementation import',
             'finite_tables':'read-only import of emitted implementation; separate structural validator',
             'physical':'no long numeric fixtures rerun'},
    descriptor_fields=23, consumer_semantic_fields=sorted(USED),
    canonical_preserved_only_fields=sorted(set(SCHEMA)-USED),
    valid_parent_geometries=geometries,private_views=views,
    disjoint_selected_positions=selected_positions,
    maximum_observed_child_parent_header_ratio=max_child_parent_ratio,
    fixed_rank_compilations=73,prepare_table_rows_range=[min(table_sizes),max(table_sizes)],
    next_table_rows=next_size,release_table_rows=release_size,
    private_ports=45,signed_phase_cases=signed_pairs,strict_signed_pairs=strict_pairs,
    signed_widths=[2,8],counterexample_widths=[2,20],controls=controls,
    is_universal_proof=False,
    proof_support='Universal claims separately reviewed by algebra/source reasoning; these are bounded failure detectors.')
(OUT/'independent-check-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,sort_keys=True))
