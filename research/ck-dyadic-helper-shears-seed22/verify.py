#!/usr/bin/env python3
"""Exact fixed-forest CK helper matching; no new kappa.

steph4n-gh with substantial OpenAI Codex assistance. Apache-2.0.
Reuses the pinned PR917 lowering/replay and PR622 native checker with credit.
"""
import argparse
import copy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
ALPHABET = ((-2, 1), (-1, 1), (-1, 2), (1, 2), (1, 1), (2, 1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if Path(path).suffix == '.gz' else raw)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sources():
    pins = read(HERE / 'SOURCES.json')
    for item in pins['files']:
        raw = (ROOT / item['path']).read_bytes()
        payload = gzip.decompress(raw) if item.get('encoding') == 'gzip' else raw
        require(hashlib.sha256(payload).hexdigest() == item['sha256'], 'source pin: ' + item['path'])
    return pins


@lru_cache(None)
def price8(value, modern=False):
    """Retained binary Horner cost of value/8; zero means no operation."""
    if value == 0:
        return 0
    a, d = abs(value), 3
    while d and a % 2 == 0:
        a //= 2
        d -= 1
    old = 3 + a.bit_length() - 1 + a.bit_count() + d
    return old - (2 if abs(value) == 8 else 1) if modern else old


def census(D, modern=False):
    cols = list(zip(*D))
    costs = [sum(price8(2*x,modern) for x in col) for col in cols]
    edges = {}
    checksum = hashlib.sha256()
    profitable = {str(Q(n, d)): 0 for n, d in ALPHABET}
    for a, left in enumerate(cols):
        for b, right in enumerate(cols):
            if a == b:
                continue
            for n, d in ALPHABET:
                q2 = 2*n//d
                gain = costs[b] - sum(price8(2*v-q2*u,modern) for u, v in zip(left, right)) - 2*price8(4*q2,modern)
                edges[a, b, n, d] = gain
                checksum.update(f'{a},{b},{n},{d},{gain}\n'.encode())
                profitable[str(Q(n,d))] += gain > 0
    return edges, {'cases': len(edges), 'sha256': checksum.hexdigest(), 'profitable': profitable}


def dual_check(cert, edges, units=False):
    """Weak duality for non-perfect weighted matching, in doubled integers."""
    dv = cert['vertex_dual_twice']
    require(len(dv) == 254 and all(type(v) is int and v >= 0 for v in dv), 'vertex dual')
    odd = []
    for item in cert['odd_sets']:
        vs, z = item['vertices'], item['dual']
        require(type(z) is int and z >= 0, 'odd-set dual')
        require(len(vs) >= 3 and len(vs) % 2 == 1 and len(set(vs)) == len(vs), 'odd-set cardinality')
        require(all(type(v) is int and 0 <= v < 254 for v in vs), 'odd-set vertex')
        odd.append((set(vs), z))
    used = set()
    total = 0
    for x in cert['matching']:
        key = x['a'], x['b'], x['numerator'], x['denominator']
        require(all(type(v) is int for v in (*key, x['gain'])), 'matching integer fields')
        require(key in edges and (not units or abs(key[2]) == key[3]), 'matching alphabet')
        a, b = key[:2]
        require(a not in used and b not in used, 'matching overlap')
        used.update((a, b))
        require(x['gain'] == edges[key] and x['gain'] > 0, 'matching gain')
        total += x['gain']
    covered = 0
    for (a, b, n, d), gain in edges.items():
        if units and abs(n) != d:
            continue
        # Nonpositive edges can be omitted from a maximum-weight matching.
        if gain > 0:
            lhs = dv[a] + dv[b] + 2*sum(z for vs, z in odd if a in vs and b in vs)
            require(lhs >= 2*gain, 'dual edge uncovered')
            covered += 1
    bound2 = sum(dv) + sum((len(vs)-1)*z for vs, z in odd)
    require(bound2 == 2*total, 'primal dual gap')
    require(cert['gain'] == total and cert['matching_pairs'] == len(cert['matching']), 'matching receipt')
    return {'gain': total, 'dual_bound_twice': bound2, 'pairs': len(cert['matching']),
            'positive_directed_edges_covered': covered, 'positive_odd_sets': len(odd)}


def panel(e, targets, helpers, C, forest, matching):
    D = [row[:] for row in C]
    for child, parent, sign, _ in forest:
        D[child] = [a-sign*b for a,b in zip(C[child], C[parent])]
    E = [[Q(x,4) for x in row] for row in D]
    prepT = [e.addition(targets[c], targets[p], -s) for c,p,s,_ in forest]
    prepH = []
    used = set()
    for x in matching:
        a,b,q = x['a'],x['b'],Q(x['numerator'], x['denominator'])
        require(a != b and a not in used and b not in used, 'overlapping helper pair')
        used.update((a,b))
        prepH.append(e.addition(helpers[a], helpers[b], q))
        for row in E:
            row[b] -= q*row[a]
    residual = [e.addition(t, helpers[j], x) for t,row in zip(targets,E) for j,x in enumerate(row) if x]
    inverse = lambda es: [e.addition(x[1], x[2], -Q(x[3],x[4])) for x in reversed(es)]
    result = prepT + prepH + residual + inverse(prepH) + inverse(prepT)
    return result, {'target_preparation':len(prepT), 'helper_preparation':len(prepH),
                    'residual':len(residual), 'restoration':len(prepT)+len(prepH),
                    'total':len(result), 'sha256':digest(result)}


def integer_summary(result):
    p = result['positive_prefix']
    return {'real_primitives':2*result['primitive_count'],
            'prefix_l1':str(Q(p['numerator'], 2**p['denominator_power'])),
            'prefix_bits':p['strict_power_of_two_bits'],
            'maximum_denominator_power':result['maximum_denominator_power']}


def modern_primitives(events, lower):
    """Adapt the pinned PR696 vocabulary to the existing integer interpreter."""
    for event in events:
        if event[0] != 'scalar':
            continue
        for instruction in lower(event[1]):
            if instruction[0] in ('add','subtract'):
                yield ('add',instruction[1],instruction[2],1 if instruction[0]=='add' else -1)
            else:
                yield instruction


def native(e, w, programs):
    with tempfile.TemporaryDirectory(prefix='ck-dyadic22-') as directory:
        out = Path(directory)
        (out/'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(canonical(w),mtime=0))
        for filename in ('hpe_emit_local.py', 'hpe_audit_local.py'):
            path=ROOT/'research/complex-571-cold14-k492c/code'/filename
            run=subprocess.run([sys.executable,'-I','-B',str(path),str(out)],capture_output=True,text=True)
            require(run.returncode == 0, 'native '+filename+' failed:\n'+run.stdout+run.stderr)
        require(read(out/'LOCAL-PROGRAMS.json.gz') == programs, 'native emission disagreement')
        checks=read(out/'LOCAL-CHECKS.json')
        audit=read(out/'INDEPENDENT-LOCAL-REPLAY.json')
        require(len(audit['negative_controls_rejected']) == 25, 'native controls missing')
        return {'checks':checks,'local':audit['local'],'paid_profiles':audit['paid_profiles'],
                'negative_controls_rejected':audit['negative_controls_rejected']}


def controls(e, integer, w, candidate_panel, forest, matching, edges, certificates):
    rejected=[]
    def must_fail(label, fn):
        try: fn()
        except ValueError: rejected.append(label)
        else: raise ValueError('control accepted: '+label)
    for label, mutate in (
        ('underpriced_nonunit', lambda c: next(x for x in c['matching'] if x['denominator']==2).__setitem__('gain', 6)),
        ('overlapping_matching', lambda c: c['matching'].append(copy.deepcopy(c['matching'][0]))),
        ('negative_vertex_dual', lambda c: c['vertex_dual_twice'].__setitem__(0,-1)),
        ('uncovered_dual', lambda c: c.__setitem__('vertex_dual_twice',[0]*254)),
        ('even_odd_set', lambda c: c['odd_sets'][0]['vertices'].pop()),
        ('duplicate_odd_vertex', lambda c: c['odd_sets'][0]['vertices'].__setitem__(0,c['odd_sets'][0]['vertices'][1])),
    ):
        bad=copy.deepcopy(certificates['extended']);mutate(bad)
        must_fail(label,lambda:dual_check(bad,edges))
    nt=len(forest); nh=len(matching)
    nonunit=next(i for i,x in enumerate(matching) if x['denominator']==2)
    reference=integer.replay(e.primitives([e.scalar(x,False) for x in w['compensation']]))['endpoint']
    for name, index, alteration in (
        ('missing_target_preparation',0,'delete'),
        ('missing_helper_preparation',nt+nonunit,'delete'),
        ('missing_helper_restoration',len(candidate_panel)-nt-1-nonunit,'delete'),
        ('missing_target_restoration',len(candidate_panel)-1,'delete'),
        ('wrong_nonunit_sign',nt+nonunit,'sign'),
        ('half_swapped_with_double',nt+nonunit,'reciprocal'),
    ):
        bad=copy.deepcopy(candidate_panel)
        if alteration=='delete': del bad[index]
        elif alteration=='sign': bad[index][3]*=-1
        else: bad[index][3],bad[index][4]=-2,1
        got=integer.replay(e.primitives([e.scalar(x,False) for x in bad]))['endpoint']
        require(got!=reference,'operator control accepted: '+name)
        rejected.append(name)
    # Cost-symmetric endpoint-preserving omission cannot detect private dirt without its own input column.
    q=Q(-1,2); primitives=e.lower(['add',['L',1],['L',0],q.numerator,q.denominator])
    good=integer.replay(primitives,n=2,centers=0)['endpoint']
    for label,ops in [('dirty_work_without_initial_clear',primitives[1:]),('uncleared_final_work',primitives[:-1])]:
        require(integer.replay(ops,n=2,centers=0)['endpoint']!=good,'work control accepted')
        rejected.append(label)
    return rejected


def verify(record=False):
    pins=sources()
    e=module('ck917_experiment',ROOT/'research/complex-ck-two-sided/experiment.py')
    integer=module('ck917_integer',ROOT/'research/complex-ck-two-sided/independent.py')
    independent=module('ck22_independent',HERE/'independent.py')
    w,original,checks=e.load()
    targets,helpers,C=e.matrix(w)
    prior=read(ROOT/'research/complex-ck-two-sided/RECIPE.json')
    forest=prior['target_forest']
    D=[row[:] for row in C]
    for c,p,s,_ in forest: D[c]=[a-s*b for a,b in zip(C[c],C[p])]
    edges,census_receipt=census(D)
    certificate=read(HERE/'CERTIFICATE.json')
    require(certificate['format']=='ck-helper-matching-dual-v1' and certificate['seed']==22 and
            certificate['alphabet']==[list(q) for q in ALPHABET], 'certificate domain')
    certificates=certificate['matchings']
    proof={name:dual_check(certificates[name],edges,name=='unit') for name in ('unit','extended')}
    other=independent.run()
    require(other['census_sha256']==census_receipt['sha256'] and other['census_cases']==census_receipt['cases'], 'independent census disagreement')
    oldmatching=[dict(a=a,b=b,numerator=s,denominator=1,gain=g) for a,b,s,g in prior['helper_pairs']]
    require(sum(edges[x['a'],x['b'],x['numerator'],x['denominator']] for x in oldmatching)==prior['helper_search']['gain'], 'predecessor price mismatch')
    programs={'baseline':original}; panels={}; panel_counts={}
    for name,matching in [('predecessor',oldmatching)]+[(n,certificates[n]['matching']) for n in ('unit','extended')]:
        panels[name],panel_counts[name]=panel(e,targets,helpers,C,forest,matching)
        programs[name]=e.replace_programs(w,original,panels[name])
        literal_price=sum(len(e.lower(e.scalar(x,False)[1])) for x in panels[name])
        gain=prior['helper_search']['gain'] if name=='predecessor' else certificates[name]['gain']
        require(literal_price==prior['forest_search']['price']-gain,'emitted panel/certified old price')
        panel_counts[name]['component_primitive_price']=literal_price
    result={'status':'FINITE_FIXED_FOREST_DYADIC_HELPER_MATCHING_NO_NEW_KAPPA','base_commit':BASE,'seed':22,
            'source_pins_sha256':digest(pins),'certificate_sha256':digest(certificate),
            'census':census_receipt,'matching_proofs':proof,'independent':other,
            'panels':panel_counts,'programs':{}}
    for orientation in ('forward','backward'):
        results={}
        for name in ('baseline','predecessor','unit','extended'):
            events=programs[name][orientation]
            counted=2*sum(len(e.lower(x[1])) for x in events if x[0]=='scalar')
            if name in ('baseline','unit','extended'):
                replay=integer.replay(e.primitives(events))
                integer.check_endpoint(replay,orientation)
                summary=integer_summary(replay)
                require(summary['real_primitives']==counted,'literal primitive count')
                require(summary['prefix_bits']<=192,'192-bit local allowance')
                if name in ('baseline','extended'):
                    state,second=e.fraction_replay(events)
                    e.endpoint(state,orientation=='backward')
                    require(second==summary,'Fraction/integer disagreement')
            else:
                summary={'real_primitives':counted}
            summary.update(program_sha256=digest(events), scalar_macros=sum(x[0]=='scalar' for x in events),
                           primitive_word_sha256=digest(list(e.primitives(events))))
            results[name]=summary
        require(results['baseline']['real_primitives']==checks[orientation]['real_component_primitive_bound'],'historical bill')
        require(results['predecessor']['real_primitives']-results['extended']['real_primitives']==8,'predecessor delta')
        require(results['unit']['real_primitives']-results['extended']['real_primitives']==6,'alphabet delta')
        result['programs'][orientation]=results
    nw=copy.deepcopy(w);nw['compensation']=panels['extended']
    result['native']=native(e,nw,programs['extended'])
    for orientation in ('forward','backward'):
        actual=result['native']['checks'][orientation]
        require(actual['paid_profile']==checks[orientation]['paid_profile'],'changed child profile')
        require(actual['real_component_primitive_bound']==result['programs'][orientation]['extended']['real_primitives'],'native count')
        require(result['native']['local'][orientation]['prefix_l1_upper']==result['programs'][orientation]['extended']['prefix_l1'],'native prefix')
    # Reprice/reoptimize under the stronger accepted copy/unit lowering.
    modern=module('pr696_lower',ROOT/'research/complex-dyadic-lowering/lower.py')
    modern_edges,modern_census=census(D,modern=True)
    modern_certs=certificate['pr696_matchings']
    modern_proof={name:dual_check(modern_certs[name],modern_edges,name=='unit') for name in ('unit','extended')}
    require(other['pr696']['census_sha256']==modern_census['sha256'] and
            other['pr696']['census_cases']==modern_census['cases'],'independent modern census')
    modern_programs={}
    modern_native={}
    for name in ('unit','extended'):
        key='pr696_'+name
        replacement,panel_counts[key]=panel(e,targets,helpers,C,forest,modern_certs[name]['matching'])
        literal_price=sum(len(modern.lower(e.scalar(x,False)[1])) for x in replacement)
        require(literal_price==other['pr696']['target_forest_panel_price']-modern_certs[name]['gain'],'emitted panel/certified modern price')
        panel_counts[key]['component_primitive_price']=literal_price
        modern_programs[name]=e.replace_programs(w,original,replacement)
        native_word=copy.deepcopy(w);native_word['compensation']=replacement
        modern_native[name]=native(e,native_word,modern_programs[name])
    modern_results={}
    for orientation in ('forward','backward'):
        modern_results[orientation]={}
        variants=[('baseline',original[orientation]),('predecessor',programs['predecessor'][orientation]),
                  ('old_unit_witness',programs['unit'][orientation]),('old_extended_witness',programs['extended'][orientation])]
        variants += [(name,modern_programs[name][orientation]) for name in ('unit','extended')]
        for name,events in variants:
            literal=list(modern_primitives(events,modern.lower))
            replay=integer.replay(literal)
            integer.check_endpoint(replay,orientation)
            summary=integer_summary(replay)
            require(summary['prefix_bits']<=192,'modern local precision allowance')
            summary.update(program_sha256=digest(events),primitive_word_sha256=digest(literal),
                           scalar_macros=sum(x[0]=='scalar' for x in events))
            modern_results[orientation][name]=summary
            if name in ('unit','extended'):
                nc=modern_native[name]['checks'][orientation]
                require(nc['paid_profile']==checks[orientation]['paid_profile'],'modern native child profile')
                require(nc['real_component_primitive_bound']==2*sum(len(e.lower(x[1])) for x in events if x[0]=='scalar'),'modern macros/native old lowering')
                require(Q(summary['prefix_l1'])<=Q(modern_native[name]['local'][orientation]['prefix_l1_upper']),'modern prefix exceeds native old lowering')
        require(modern_results[orientation]['unit']['real_primitives']==modern_results[orientation]['extended']['real_primitives'],'modern alphabet tie')
    result['pr696']={'census':modern_census,'matching_proofs':modern_proof,
                      'programs':modern_results,'native':modern_native}
    # This historical local allowance depends on macro count as well as scalar work.
    # The matching duals optimize scalar work, not this separate reserve objective.
    require(w['R']==492 and w['v']==112 and len(w['centers'])==8,'local invoice dimensions')
    require(checks['forward']['paid_profile']==checks['backward']['paid_profile'] and
            sum(checks['forward']['paid_profile'].values())==3698,'local invoice children')
    def invoice(rows):
        M=max(rows[o]['scalar_macros'] for o in ('forward','backward'))
        P=max(rows[o]['real_primitives'] for o in ('forward','backward'))
        adapters=16*(M+3698+716+8)+64*73
        return {'maximum_scalar_macros':M,'maximum_real_primitives':P,
                'adapter_reserve':adapters,'compiler_factor':64*74**3,
                'local_bound':P+adapters*(64*74**3)}
    result['historical_local_invoice']={
        'binary_horner':{name:invoice({o:result['programs'][o][name] for o in ('forward','backward')})
                         for name in ('baseline','predecessor','unit','extended')},
        'pr696':{name:invoice({o:modern_results[o][name] for o in ('forward','backward')})
                 for name in ('baseline','predecessor','old_unit_witness','old_extended_witness','unit','extended')}}
    result['controls']=controls(e,integer,w,panels['extended'],forest,certificates['extended']['matching'],edges,certificates)
    if record:
        (HERE/'EXPECTED.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        require(read(HERE/'EXPECTED.json')==result,'EXPECTED.json mismatch')
    print('PASS_CK_DYADIC_HELPERS cases=385572x2 old_optima=4400/4403 pr696_optima=3778/3778 columns=725 controls='+str(len(result['controls']))+'+25 no_new_kappa')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true',help='regenerate only this package receipt after checks')
    args=parser.parse_args()
    verify(args.record)
