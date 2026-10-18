"""Exact native paired-plane identity block and per-array occurrence invoice.

Jeremy Diviney, with OpenAI Codex assistance. Apache-2.0.
Uses the credited retained Clifford compiler and separate Gaussian interpreter.
No improved supplier, kappa, or general plane-decoder lower bound is claimed.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
NATIVE = ROOT / 'research/p104-native-channel/vendor'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sources():
    data = json.loads((PACKAGE/'SOURCES.json').read_text())
    for row in data['files']:
        if row['usage']=='input':
            path=ROOT/row['path']
            need(path.is_file(),'missing source: '+row['path'])
            need(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],
                 'changed source: '+row['path'])
    return data

def basis(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for higher in pivots:
            if higher > bit and pivots[higher] >> bit & 1:
                pivots[higher] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))

def inputs():
    archive=ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    with tarfile.open(archive) as tf:
        f = tf.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json')
        raw=f.read();data = json.loads(raw)
    need(data['m']==73 and data['ports']==112,'selected parent width and port count')
    need(sorted(x['port'] for x in data['recipes'])==list(range(112)),'selected recipe indices')
    labels = [x['q'] for x in sorted(data['recipes'], key=lambda r:r['port'])]
    cert = json.loads((ROOT / 'research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json').read_text())
    need(cert['selected_archive_sha256']==hashlib.sha256(archive.read_bytes()).hexdigest(), 'matching archive binding')
    need(cert['selected_payload_sha256']==hashlib.sha256(raw).hexdigest(), 'matching payload binding')
    return labels, cert['matching']

def recipes(q, r):
    need((q & r).bit_count() % 2 == 0 and q.bit_count() % 2 == r.bit_count() % 2 == 1,
         'orthonormal paired plane')
    plane = basis((q, r))
    cap = basis(v for v in range(512) if not (q & v).bit_count() % 2 and not (r & v).bit_count() % 2)
    need(len(plane) == 2 and len(cap) == 7, 'frame dimensions')
    E, V = CE.canonical_frame(9, plane), CE.canonical_frame(9, cap)
    F = CE.fourier(9)
    intrinsic = CE.cgate(9, q, 1).then(CE.cgate(9, r, 1))
    actuals = {
        'source_entry': intrinsic.adjoint().then(E),
        'source_advance': E.adjoint().then(F),
        'private_drop': E.adjoint(),
        'target_advance': V,
        'target_exit': V.adjoint().then(intrinsic.adjoint()).then(F),
    }
    e, v, f = NV.frame(plane, 9), NV.frame(cap, 9), NV.fourier(9)
    c = (('C', q, 1), ('C', r, 1))
    expected = {
        'source_entry': NV.adjoint(c) + e,
        'source_advance': NV.adjoint(e) + f,
        'private_drop': NV.adjoint(e),
        'target_advance': v,
        'target_exit': NV.adjoint(v) + NV.adjoint(c) + f,
    }
    ranks = {'source_entry':0, 'source_advance':7, 'private_drop':2,
             'target_advance':7, 'target_exit':0}
    out = {}
    for tag, op in actuals.items():
        record, _ = CE.lower_child(op)
        need(record['rank'] == ranks[tag], tag + ' native rank')
        NV.equal(NV.recipe(record), expected[tag], tag + ' exact operator')
        out[tag] = record
    return out, expected

def scalar_word(ports=2):
    program = []
    for p in range(ports):
        program.extend([['zero', 'C'], ['copy', 'C', 'X'+str(p)],
                        ['transport', 'X'+str(p), 'E', 'FULL', 7],
                        ['transport', 'C', 'E', 'ZERO', 2],
                        ['add', 'Y'+str(p), 'C', 1], ['erase', 'C'],
                        ['transport', 'Y'+str(p), 'ZERO', 'Eperp', 7]])
    return program

def execute(program, transfer=((1,0),(0,1)), private_lifetimes=2):
    names=['X0','X1','Y0','Y1']
    rows={name:[int(i==j) for j in range(4)] for i,name in enumerate(names)}
    frames={name:('E' if name.startswith('X') else 'ZERO') for name in names}
    ranks=Counter(); allocations=0
    for event in program:
        tag=event[0]
        if tag=='zero':
            _,reg=event
            need(reg=='C' and reg not in rows,'private lifetime must be fresh')
            rows[reg]=[0]*4;frames[reg]='E';allocations+=1
        elif tag=='copy':
            _,dst,src=event
            need(dst=='C' and rows[dst]==[0]*4 and frames[dst]==frames[src],
                 'COPY needs owned zero and common chart')
            rows[dst]=rows[src][:]
        elif tag=='transport':
            _,reg,old,new,rank=event
            need(frames[reg]==old,'transport starts at actual chart')
            need((old,new,rank) in [('E','FULL',7),('E','ZERO',2),('ZERO','Eperp',7)],
                 'transport must use checked native recipe')
            frames[reg]=new;ranks[rank]+=1
        elif tag=='add':
            _,dst,src,coeff=event
            need(frames[dst]==frames[src],'ADD requires common chart')
            rows[dst]=[a+coeff*b for a,b in zip(rows[dst],rows[src])]
        elif tag=='erase':
            _,reg=event
            need(reg=='C' and frames[reg]=='ZERO','owned private disposal at chart zero')
            del rows[reg];del frames[reg]
        else:raise ValueError('unknown event')
    target=[[1,0,0,0],[0,1,0,0],list(transfer[0])+[1,0],list(transfer[1])+[0,1]]
    need([rows[name] for name in names]==target,'all source and arbitrary dirty target columns')
    need('C' not in rows and frames=={'X0':'FULL','X1':'FULL','Y0':'Eperp','Y1':'Eperp'},
         'all public endpoints and private disposal')
    need(allocations==private_lifetimes,'private payload lifetime count')
    return ranks,target

def rejects(fn):
    try:fn()
    except ValueError:return True
    return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path)
    ap.add_argument('--write-expected',action='store_true')
    args=ap.parse_args()
    sources()
    global CE,NV
    CE = load('plane_clifford', NATIVE / 'clifford_exact.py')
    NV = load('plane_native_check', NATIVE / 'native_verify.py')
    labels, pairs = inputs()
    need(len(labels)==112 and len(pairs)==56 and sorted(i for p in pairs for i in p)==list(range(112)),
         'matching partitions all selected ports')
    records = []
    line_adapter_checks=0
    for i,(a,b) in enumerate(pairs):
        rec, exp = recipes(labels[a], labels[b])
        if i == 0:
            for column in range(512):
                need(NV.state(NV.recipe(rec['private_drop']),column)==NV.state(exp['private_drop'],column),
                     'private-drop complete Gaussian basis')
            bad=copy.deepcopy(rec['private_drop'])
            bad['left']['phase']=(bad['left']['phase']+1)%4
            need(rejects(lambda:NV.equal(NV.recipe(bad),exp['private_drop'],'phase control')),
                 'wrong global phase rejected')
            bad_rank=copy.deepcopy(rec['private_drop']);bad_rank['rank']=1
            need(rejects(lambda:NV.equal(NV.recipe(bad_rank),exp['private_drop'],'rank control')),
                 'one-direction drop cannot implement the plane drop')
        E=CE.canonical_frame(9,basis((labels[a],labels[b])))
        for port in (a,b):
            adapter,_=CE.lower_child(CE.cgate(9,labels[port],1).adjoint().then(E))
            need(adapter['rank']==1,'a line entrance is not a free plane entrance')
            line_adapter_checks+=1
        records.append({'ports':[a,b], 'labels':[labels[a],labels[b]], 'recipes':rec})
    program=scalar_word()
    event_profile,matrix=execute(program)
    need(event_profile=={7:4,2:2},'one complete pair profile')
    broadcast=[['zero','C'],['copy','C','X0'],['add','C','X1',1],
               ['transport','X0','E','FULL',7],['transport','X1','E','FULL',7],
               ['transport','C','E','ZERO',2],['add','Y0','C',1],['add','Y1','C',1],
               ['erase','C'],['transport','Y0','ZERO','Eperp',7],
               ['transport','Y1','ZERO','Eperp',7]]
    broadcast_profile,broadcast_matrix=execute(broadcast,((1,1),(1,1)),1)
    need(broadcast_profile=={7:4,2:1},'one-payload positive native control')
    profile = Counter()
    for record in records:
        for tag in ['source_advance','private_drop','target_advance']:
            # Both independent port arrays execute the recipe once.
            profile[record['recipes'][tag]['rank']] += 2
    need(profile=={7:224,2:112}, 'occurrence invoice')
    need(profile=={r:56*n for r,n in event_profile.items()},'native recipes and event occurrences agree')
    bad=copy.deepcopy(program)
    for e in bad:
        if e[:3]==['copy','C','X1']:e[2]='X0'
    # After X0 advances, this reuse fails the chart boundary even before its
    # wrong scalar endpoint; the direct transfer mutation tests payload rank.
    need(rejects(lambda:execute(bad)),'stale or reused first payload rejected')
    bad=copy.deepcopy(program)
    for e in bad:
        if e[:3]==['add','Y1','C']:e[3]=0
    need(rejects(lambda:execute(bad)),'missing second payload rejected')
    bad=copy.deepcopy(program)
    bad.insert(0,['erase','Y0'])
    need(rejects(lambda:execute(bad)),'public dirty input cannot be disposed')
    bad=[e for e in program if not(e[0]=='transport' and e[1]=='C')]
    need(rejects(lambda:execute(bad)),'unpaid cross-chart ADD rejected')
    need(rejects(lambda:execute(broadcast)),
         'legal one-payload broadcast cannot substitute for the identity')
    need(rejects(lambda:need({7:224,2:56}==profile,'half-counted invoice')),
         'per-recipe count is not per-payload occurrence count')
    recipe_digest=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    receipt = {
        'planes':56,'native_recipes':280,'native_ranks_checked':True,
        'local_profile':{str(k):v for k,v in profile.items()},'local_rank_mass':sum(k*v for k,v in profile.items()),
        'copy_mass':224, 'per_call_deficit':str(Fraction(2*896,9)-224),
        'private_lifetimes':112,'peak_owned_private_arrays':1,
        'block_program':program,'block_scalar_matrix':matrix,
        'broadcast_positive_profile':{str(k):v for k,v in broadcast_profile.items()},
        'broadcast_positive_matrix':broadcast_matrix,
        'native_recipe_sha256':recipe_digest,
        'all_column_private_drop_checks':512,'symbolic_columns_per_block':4,
        'covered_public_input_columns':224,
        'line_to_plane_entry_rank1_checks':line_adapter_checks,
        'moment_at_zero':str(Fraction(71*896+9*224,73*896)),
        'controls':8,
        'scope':'Explicit direct per-port plane word, native recipes and local occurrence invoice; not a global supplier or universal plane lower bound.'
    }
    expected=PACKAGE/'EXPECTED.json'
    if args.write_expected:
        need(not expected.exists(),'expected receipt already exists')
        expected.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(expected.read_text())==receipt,'complete recomputed receipt')
    if args.output:
        with args.output.open('x') as f:f.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS_PAIRED_PLANE_NATIVE_PAYLOAD',dict(profile),'mass',receipt['local_rank_mass'],'copy',receipt['copy_mass'],
          'moment_at_zero',receipt['moment_at_zero'],'no_new_kappa',flush=True)

if __name__=='__main__':main()
