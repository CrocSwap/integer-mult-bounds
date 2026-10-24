#!/usr/bin/env python3
"""Complete finite helper residual/normalizer phase proof; no source imports.

Only the independent reviewer module next to this checker is loaded. Source
receipts are candidate circuit data. Their recorded PASS status is not used.
Clifford conjugation on all Pauli generators fixes an operator up to scalar;
exact nonzero anchor amplitudes fix that scalar, including absolute phase.
"""
import copy,gzip,hashlib,importlib.util,json,pathlib,sys,time

from . import source
from . import independent_clifford as C
HERE=pathlib.Path(__file__).resolve().parent
WORD_PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
CANONICAL='ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c'

def need(b,s):
    if not b:raise ValueError(s)

def normalizer_valid(C,r):
    need(set(r)=={'matrix_rows','quadratic_rows','linear_Z4','offset','phase'},'exact normalizer field schema')
    G,Q,a=r['matrix_rows'],r['quadratic_rows'],r['linear_Z4']
    need(len(G)==len(Q)==len(a)==9,'nine-dimensional monomial')
    need(all(type(x)is int and 0<=x<512 for x in G+Q),'binary normalizer matrices')
    need(C.rank(G)==9 and C.transpose(Q)==Q,'invertible linear permutation and symmetric quadratic form')
    need(all(type(x)is int and 0<=x<4 for x in a),'Z4 diagonal phases')
    need(all(a[j]%2==((Q[j]>>j)&1)for j in range(9)),'Clifford diagonal phase parity')
    need(type(r['offset'])is int and 0<=r['offset']<512,'monomial offset')
    need(type(r['phase'])is int and 0<=r['phase']<4,'absolute scalar phase')

def phase_equal(C,target,compiled):
    T,S=C.tableau(target),C.tableau(compiled)
    need(T==S,'all18 Pauli conjugations, with Pauli phases')
    a,d=C.state(target);b,e=C.state(compiled)
    need(sum(x*x+y*y for x,y in a)==1<<(2*d),'exact nonzero unit-norm anchor')
    need((a,d)==(b,e),'exact absolute-phase anchor amplitudes')
    return T,a,d

def cover(rows):
    roles=[i for r in rows for i in r['roles']]
    need(len(roles)==408 and sorted(roles)==list(range(224,632)),'complete exact408 role coverage, no duplicates')
    need(len({(r['input'],r['output'])for r in rows})==len(rows),'unique endpoint-pair source classes')

def run():
    start=time.monotonic()
    objects={k:source.js(p) for k,p in {'word':'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','selected_recipes':'research/joint-helper-lattice/NATIVE.json.gz','changed_recipes':'research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz'}.items()}
    source_hashes={}
    raw_word=gzip.decompress(source.raw('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'));need(hashlib.sha256(raw_word).hexdigest()==WORD_PAYLOAD,'exact final4610 canonical word payload')
    c=objects['word']['canonical'];need(len(c['start'])==len(c['final'])==632 and c['h']==9,'actual persistent width and digit axes')
    grouped={}
    for role in range(224,632):grouped.setdefault((c['start'][role],c['final'][role]),[]).append(role)
    catalogues={'selected_recipes':objects['selected_recipes']['new_physical_edges_and_boundaries'],'changed_recipes':objects['changed_recipes']['changed_helper_boundaries']}
    rows=[]
    for (a,b),roles in sorted(grouped.items()):
        choices=[(name,j) for name,cat in catalogues.items() for j,row in enumerate(cat) if (row.get('old',row.get('input')),row.get('new',row.get('output')))==(a,b)]
        need(choices,'actual helper recipe missing')
        name,j=choices[-1]
        rows.append(dict(input=a,output=b,rank=len(c['frames'][b])-len(c['frames'][a]),roles=roles,input_ordered_basis=c['frames'][a],output_ordered_basis=c['frames'][b],recipe_source=name,recipe_index=j))
    cover(rows)
    actual={}
    for i in range(224,632):actual.setdefault((c['start'][i],c['final'][i]),[]).append(i)
    need(len(actual)==len(rows)==17,'all17 actual final endpoint pairs')
    source_catalogues={'selected_recipes':objects['selected_recipes']['new_physical_edges_and_boundaries'],
                       'changed_recipes':objects['changed_recipes']['changed_helper_boundaries']}
    evidence=[];phase_controls=[];census={}
    for row in rows:
        a,b,r=row['input'],row['output'],row['rank'];need(actual[a,b]==row['roles'],'actual final roles, not inferred from count')
        U,V=c['frames'][a],c['frames'][b];need(U==row['input_ordered_basis']and V==row['output_ordered_basis'],'actual exact ordered frame bases')
        need(all(type(x)is int and 0<=x<512 for x in U+V),'binary frame domain')
        need(C.rank(U)==len(U)and C.rank(V)==len(V)and C.rank(U+V)==len(V),'independent exact nested frame bases')
        need(r==len(V)-len(U)>0,'positive complete relative Fourier rank')
        census[r]=census.get(r,0)+len(row['roles'])
        candidate=source_catalogues[row['recipe_source']][row['recipe_index']]
        ca,cb=(candidate['old'],candidate['new'])if row['recipe_source']=='selected_recipes'else(candidate['input'],candidate['output'])
        need((ca,cb)==(a,b)and candidate['rank']==r,'source recipe class label/rank')
        residual=C.adj(C.frame(U))+C.frame(V)
        for direction in ('forward','backward'):
            target=residual if direction=='forward'else C.conjugate(residual);rec=candidate['recipes'][direction]
            need(set(rec)=={'left','right','rank'}and rec['rank']==r,'actual complete two-sided recipe')
            normalizer_valid(C,rec['left']);normalizer_valid(C,rec['right'])
            compiled=C.recipe(rec['right'])+[('C',1<<j,1)for j in range(r)]+C.recipe(rec['left'])
            T,anchor,den=phase_equal(C,target,compiled)
            need(C.rank([x for x,z,p in T[9:]])==r,'independently computed physical Fourier rank')
            # Phase-only mutation preserves all tableaux but must fail anchor.
            bad=copy.deepcopy(rec);bad['left']['phase']=(bad['left']['phase']+1)%4
            wrong=C.recipe(bad['right'])+[('C',1<<j,1)for j in range(r)]+C.recipe(bad['left'])
            need(C.tableau(wrong)==T and C.state(wrong)!=(anchor,den),'phase-only mutation nonvacuously rejected')
            phase_controls.append({'input':a,'output':b,'direction':direction,'tableau_unchanged':True,'absolute_phase_rejected':True})
            evidence.append({'input':a,'output':b,'rank':r,'direction':direction,'roles':row['roles'],'recipe_source':row['recipe_source'],'recipe_index':row['recipe_index'],'recipe_sha256':hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'pauli_generators_checked':18,'explicit_anchor_basis_columns':1,'anchor_nonzero_entries':sum(v!=(0,0)for v in anchor),'anchor_denominator_power_of_two':den,'tableau_sha256':hashlib.sha256(json.dumps(T,separators=(',',':')).encode()).hexdigest(),'anchor_sha256':hashlib.sha256(json.dumps([anchor,den],separators=(',',':')).encode()).hexdigest(),'normalizers_monomial_schema_checked':True})
    need(census=={4:28,7:7,8:47,9:326},'derived final complete census')
    controls=[]
    for name,bad in [('missing_class',rows[:-1]),('duplicate_helper_role',copy.deepcopy(rows))]:
        if name=='duplicate_helper_role':bad[0]['roles'].append(bad[0]['roles'][0])
        try:cover(bad)
        except ValueError as e:controls.append({'name':name,'rejected':str(e)})
        else:raise ValueError('coverage mutation accepted '+name)
    normal=copy.deepcopy(source_catalogues['selected_recipes'][0]['recipes']['forward']['left']);normal['matrix_rows'][0]=normal['matrix_rows'][1]
    try:normalizer_valid(C,normal)
    except ValueError as e:controls.append({'name':'singular_normalizer','rejected':str(e)})
    else:raise ValueError('singular normalizer accepted')
    out={'status':'PASS_ALL408_HELPER_RELATIVE_OPERATORS_AND_ABSOLUTE_PHASES','canonical_commit':CANONICAL,'candidate_head':'20bb93cd990d2ff683e4d0fc56b87a42cd5d3296','word_payload_sha256':WORD_PAYLOAD,'helper_roles':408,'unique_ordered_endpoint_pairs':17,'oriented_classes':34,'helper_orientation_instances':816,'census':census,'proof_method':'Exact Clifford conjugation on all18 Pauli generators plus exact nonzero unit-norm anchor amplitudes; yields equality on all512 basis columns and all vectors without enumerating them.','explicit_basis_columns_per_class':1,'all512_explicitly_enumerated':False,'fresh_or_inherited':'Fresh independent semantic proof of every required final class; source recipes are candidate data, no PASS receipt truth or ancestry inference reused.','classes':evidence,'phase_only_controls':phase_controls,'coverage_schema_controls':controls,'source_sha256':source_hashes,'checker_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'independent_clifford_sha256':hashlib.sha256((HERE/'independent_clifford.py').read_bytes()).hexdigest(),'sources_manifest_sha256':'central live manifest','inventory_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),'seconds':time.monotonic()-start,'python':sys.version,'proc_memory':{l.split(':')[0]:l.split(':',1)[1].strip()for l in (pathlib.Path('/proc/self/status').read_text().splitlines() if pathlib.Path('/proc/self/status').is_file() else []) if l.startswith(('VmHWM:','VmPeak:'))},'E0_helper_phase_catalogue_closed':True,'uniform_physical_realization_or_tariff_proved':False,'new_kappa_or_selection':False}
    return out
