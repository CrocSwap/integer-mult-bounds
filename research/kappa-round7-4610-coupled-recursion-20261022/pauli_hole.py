"""Actual transported inner-hole gate for global Pauli pair adapters.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def lifted_polynomial(entries, f):
    linear, polar = [0]*(73*f), [0]*(73*f)
    for axis, coefficient in entries:
        support = [i for i in range(73*f) if axis >> i & 1]
        for i in support:
            linear[i] = (linear[i]+coefficient) % 4
            if coefficient % 2:
                for j in support:
                    if j > i:
                        polar[i] ^= 1 << j
    return linear, polar


def tensor_frame(frame, f):
    return [(axis << (73*j), c) for j in range(f) for axis, c in frame]


def coefficient(polar, i, j):
    return (polar[min(i,j)] >> max(i,j)) & 1


def evaluate(poly, frequency):
    linear, polar = poly
    indices = [i for i in range(len(linear)) if frequency >> i & 1]
    value = sum(linear[i] for i in indices)
    value += 2*sum((polar[i] >> j) & 1 for i in indices for j in indices if j > i)
    return value % 4


def pair_norm():
    zero = (Q(0),Q(0))
    add = lambda x,y:(x[0]+y[0],x[1]+y[1])
    mul = lambda x,y:(x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    one, ii = (Q(1),Q(0)), (Q(0),Q(1))
    rows = [[one,zero],[zero,one]]
    maximum = 1
    operations = [('add',0,1),('scale',1,-2),('add',1,0),('phase',1,1),
                  ('add',0,1),('scale',1,-2),('add',1,0),('scale',0,Q(1,2)),('scale',1,Q(1,2))]
    for kind,dst,src in operations:
        if kind=='add': rows[dst] = [add(x,y) for x,y in zip(rows[dst],rows[src])]
        else:
            factor = ii if kind=='phase' else (Q(src),Q(0))
            rows[dst] = [mul(factor,x) for x in rows[dst]]
        maximum = max(maximum,max(sum(abs(a)+abs(b) for a,b in row) for row in rows))
    need(maximum==4,'Exact emitted pair prefix bound')
    need(max(sum(abs(a)+abs(b) for a,b in row) for row in rows)==2,'Complete pair component norm')
    return dict(complex_ADD=4, signed_power_two_SCALE=4, exact_i_phase=1,
                exact_component_l1_prefix_bound=str(maximum), complete_component_l1_bound='2',
                added_fractional_bits=1, owned_productive_credit=0,
                strided_cost='O(V*((e*log(p))^tau+1)) per field adapter; two compact fanouts and one actual-bit kernel',
                fixed_120_field_bank_uses=120,
                charge_scope='Fixed physical overhead category, including dirty compact fields, repair, erasure and return. No O(V) claim or child credit.')


def run():
    manifest = read(HERE/'SOURCES.json')
    for row in manifest['files']:
        need(sha256((HERE/row['copy']).read_bytes()).hexdigest()==row['sha256'],'Source pin '+row['path'])
    n = load(HERE/'sources'/PREFIX/'native_common.py','hole_native_source')
    F = load(HERE/'sources/research/kappa-rebuild/controller/frame_exchange.py','hole_phase_source')
    _, phases = n.load_sources()
    old = read(HERE/'sources/research/kappa-round5-coupled-main-20261022/CALLER-PROBES.json.gz')
    auxiliary = old['converted_auxiliary_owner_recipes']
    owners = list(range(112))+auxiliary
    recipes = phases['recipes']+[phases['recipes'][i] for i in auxiliary]
    need([recipes[i]['q'] for i in (0,1)]==[11,19],'Actual discriminating normals')
    records, positive_contacts, power_cases = [], 0, 0
    for interval in ((0,1,2),(2,3,4),(0,1,2,3,4)):
        def target(recipe):
            fresh = [(a,1) for s in interval if s for a in n.AXES[9+8*(s-1):9+8*s]]
            head = [(a,1) for a in n.AXES[:9]] if 0 in interval else [(recipe['q'],1)]
            return n.frame(head+fresh)
        for stage in interval:
            common = n.move_frame(target(recipes[0]),n.source_route(phases,stage,owners[0]))
            holes = []
            for recipe,owner in zip(recipes,owners):
                g = n.source_route(phases,stage,owner)
                view = F.between(n,target(recipe),g,common)
                actual = n.move_frame(n.frame(list(target(recipe))+[(recipe['q'],-1)]),g,view['physical_shift'])
                wanted = n.frame(list(common)+[(recipe['q'],-1)])
                need(n.polynomial(actual)==n.polynomial(wanted),'Actual transported hole including affine phase')
                holes.append(actual)
                positive_contacts += 1
            # One column is a positive control: S(P)=Q, so it cancels Q^-1.
            need(all(n.polynomial(n.frame(list(hole)+[(recipe['q'],1)]))==n.polynomial(common)
                     for hole,recipe in zip(holes,recipes)),'One-column positive control')
            for f in (2,3,4,8):
                for k0 in range(4):
                    for k1 in range(4):
                        polys = []
                        for port,k in ((0,k0),(1,k1)):
                            q = recipes[port]['q']
                            diagonal = sum(q << (73*j) for j in range(f))
                            polys.append(lifted_polynomial(tensor_frame(holes[port],f)+[(diagonal,k)],f))
                        within = coefficient(polys[0][1],0,3)^coefficient(polys[1][1],0,3)
                        cross = coefficient(polys[0][1],3,73+3)^coefficient(polys[1][1],3,73+3)
                        need(within==(k0+1)%2 and cross==k0%2,'Universal block-polar formula')
                        need(within or cross,'Pauli powers cannot produce a common quadratic frame')
                        pair = (0,3) if within else (3,76)
                        # Translation/global scalar phases vanish in this second difference.
                        a,b = (1<<j for j in pair)
                        second = [(evaluate(p,a^b)-evaluate(p,a)-evaluate(p,b)+evaluate(p,0))%4 for p in polys]
                        need((second[0]-second[1])%4==2,'Exact Fourier-character polar witness')
                        records.append(dict(interval=interval,stage=stage,f=f,powers=[k0,k1],
                                            within_column_difference=within,cross_column_difference=cross,
                                            witness_axes=pair,second_differences_Z4=second))
                        power_cases += 1
    need(positive_contacts==1320 and power_cases==704,'Complete specified coverage')
    return dict(status='PASS_ACTUAL_GLOBAL_PAULI_INNER_HOLE_OBSTRUCTION',new_kappa=False,
                native_provider='unclosed',actual_normals=[11,19],
                positive_transport_contacts=positive_contacts,one_column_positive_controls=positive_contacts,
                tested_column_counts=[2,3,4,8],all_power_pairs_per_contact=16,power_cases=power_cases,
                records=records,all_f_statement='For every f>=2, the first two columns retain the same incompatible polar blocks. Translations and scalar phases cannot alter them.',
                stronger_sector_obstruction='For any a+bP with eigenvalues A=a+b and B=a-b, Q^-1(a+bP) on the two port0-only bit coordinates has Fourier values (A,-iB,-iB,-A). No translation character makes these constant if A!=0. Port1 is independent of these coordinates.',
                frozen_lift_deficit=dict(unconverted=0,converted=32),
                inherited_direct_head_ledgers={key:{field:old[key][field] for field in ['conditional_first_moment_surplus_before_terminal_normalization','direct_individual_Q_heads_H1','conditional_surplus_after_direct_heads']} for key in ['p1','p2_a0','p2_a1']},
                adapter_norm_and_cost=pair_norm(),
                exclusions='Only diagonal functions of each actual global Pauli at the retained owner routes and inner-hole common-contact boundary. Does not exclude non-diagonal coupled adapters, changed producer/owner words, another recursive job alphabet, or a new paid query compiler.',
                source_manifest_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    result = run()
    raw = json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    (HERE/'PAULI-HOLE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(result['status'],'contacts',result['positive_transport_contacts'],'power_cases',result['power_cases'])
