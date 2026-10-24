#!/usr/bin/env python3
"""Propose paid normalizers, then independently verify a frozen catalogue.

`generate` alone executes the pinned retained Clifford compiler, as an
untrusted proposal generator. `verify` never imports that compiler; it checks
every record using the independent reviewer's circuit implementation.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,pathlib,sys,time
from . import source
from . import all_helpers as independent_check
from . import independent_clifford as independent_C
HERE=pathlib.Path(__file__).resolve().parent
PACKAGE=HERE.parent
WORD_SHA='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
COMPILER_SHA='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'

def need(b,s):
    if not b:raise ValueError(s)

def setup():
    check,C=independent_check,independent_C
    raw=gzip.decompress(source.raw('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'));need(hashlib.sha256(raw).hexdigest()==WORD_SHA,'exact final source word')
    word=json.loads(raw);c=word['canonical'];pairs={};directionsets={};counts={}
    for d,events in word['programs'].items():
        ps=set();count=0
        for j,e in enumerate(events):
            if e[0]=='climb':a,b,r=e[3:6];kind='borrowed'
            elif e[0]=='center':a,b,r=e[2:5];kind='owned'
            else:continue
            need(r==abs(len(c['frames'][a])-len(c['frames'][b]))>0,'actual event rank')
            pairs.setdefault((a,b),{'rank':r,'occurrences':[]})['occurrences'].append({'direction':d,'event':j,'kind':kind,'role':e[2]if kind=='borrowed'else e[1]})
            need(pairs[a,b]['rank']==r,'consistent pair rank');ps.add((a,b));count+=1
        directionsets[d]=ps;counts[d]=count
    need(len(directionsets['forward'])==len(directionsets['backward'])==2855,'actual orientation-specific paid pair counts')
    need(len(pairs)==2863 and counts=={'backward':3298,'forward':3298},'actual complete paid pair/job inventory')
    for a,b in pairs:
        U,V=c['frames'][a],c['frames'][b]
        need(all(type(x)is int and 0<=x<512 for x in U+V)and C.rank(U)==len(U)and C.rank(V)==len(V),'actual independent binary frame bases')
        need(C.rank(U+V)==max(len(U),len(V)),'actual nested paid frames')
    return check,C,c,pairs,counts

def chosen(pairs,limit):
    allpairs=sorted(pairs)
    if limit is None:return allpairs
    selected=[];seen=set()
    for key in allpairs:
        tag=(pairs[key]['rank'],any(x['kind']=='owned'for x in pairs[key]['occurrences']),tuple(sorted({x['direction']for x in pairs[key]['occurrences']})))
        if tag not in seen:seen.add(tag);selected.append(key)
    for i in range(limit):
        key=allpairs[min(len(allpairs)-1,(i*len(allpairs))//limit)]
        if key not in selected:selected.append(key)
    return sorted(selected[:limit])

def write_line(f,value):f.write((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode())

def generate(args,check,C,c,pairs,counts):
    # Source compiler loaded only in this proposal-generation branch.
    compiler_path='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
    compiler_bytes=source.raw(compiler_path);need(hashlib.sha256(compiler_bytes).hexdigest()==COMPILER_SHA,'pinned candidate compiler')
    import types
    ce=types.ModuleType('pinned_paid_candidate_compiler');sys.modules[ce.__name__]=ce
    exec(compile(compiler_bytes,compiler_path,'exec'),ce.__dict__)
    pick=chosen(pairs,args.limit_pairs);cache={}
    def frame(i):
        if i not in cache:cache[i]=ce.canonical_frame(9,c['frames'][i])
        return cache[i]
    with gzip.GzipFile(filename=str(args.catalog),mode='wb',mtime=0)as f:
        proposed_classes=sum(len({x['direction']for x in pairs[key]['occurrences']})for key in pick)
        write_line(f,{'schema':'paid-phase-candidate/1','word_payload_sha256':WORD_SHA,'compiler_sha256':COMPILER_SHA,'expected_complete_union_pairs':2863,'expected_complete_oriented_classes':5710,'proposed_pairs':len(pick),'proposed_oriented_classes':proposed_classes,'partial':args.limit_pairs is not None})
        for number,(a,b)in enumerate(pick):
            op=frame(a).adjoint().then(frame(b))
            for d in ('forward','backward'):
                if not any(x['direction']==d for x in pairs[a,b]['occurrences']):continue
                if d=='backward':actual=ce.Op(9,tuple((x,z,(-p)%4)for x,z,p in op.tab),C.conjugate(op.circuit))
                else:actual=op
                recipe,_=ce.lower_child(actual);need(recipe['rank']==pairs[a,b]['rank'],'proposed paid rank')
                write_line(f,{'input':a,'output':b,'direction':d,'rank':pairs[a,b]['rank'],'recipe':recipe})
            if(number+1)%250==0:print('GENERATED_PAIRS',number+1,flush=True)
    return {'status':'PROPOSED_CATALOGUE_NOT_YET_INDEPENDENTLY_VERIFIED','pairs':len(pick),'oriented_classes':proposed_classes,'compiler_sha256':COMPILER_SHA,'catalog_sha256':hashlib.sha256(args.catalog.read_bytes()).hexdigest()}

def verify(args,check,C,c,pairs,counts):
    seen=set();ranks={};controlled=set();controls=[];cache={};classes=0;fieldinstances=0
    def frame(i):
        if i not in cache:cache[i]=C.frame(c['frames'][i])
        return cache[i]
    with gzip.open(args.catalog,'rb')as f,gzip.GzipFile(filename=str(args.evidence),mode='wb',mtime=0)as evidence:
        head=json.loads(next(f));need(head['word_payload_sha256']==WORD_SHA and head['expected_complete_union_pairs']==2863 and head['expected_complete_oriented_classes']==5710,'candidate catalogue source binding')
        need(not head['partial']or args.allow_partial,'partial catalogue cannot establish complete paid phase closure')
        for raw in f:
            rec=json.loads(raw);a,b,d=rec['input'],rec['output'],rec['direction'];key=(a,b,d)
            need((a,b)in pairs and d in ('forward','backward')and key not in seen,'actual unique oriented paid pair')
            need(any(x['direction']==d for x in pairs[a,b]['occurrences']),'paid orientation actually occurs')
            need(rec['rank']==pairs[a,b]['rank'],'actual charged rank catalogue match');recipe=rec['recipe'];r=rec['rank']
            need(set(recipe)=={'rank','left','right'}and recipe['rank']==r,'complete paid factorization')
            check.normalizer_valid(C,recipe['left']);check.normalizer_valid(C,recipe['right'])
            target=C.adj(frame(a))+frame(b)
            if d=='backward':target=C.conjugate(target)
            compiled=C.recipe(recipe['right'])+[('C',1<<j,1)for j in range(r)]+C.recipe(recipe['left'])
            T,anchor,den=check.phase_equal(C,target,compiled);need(C.rank([x for x,z,p in T[9:]])==r,'fresh physical paid Fourier rank')
            tag=(r,d,any(x['kind']=='owned'for x in pairs[a,b]['occurrences']))
            if tag not in controlled:
                wrong=compiled+[('phase',1)];need(C.tableau(wrong)==T and C.state(wrong)!=(anchor,den),'global-phase-only paid control rejected')
                controls.append({'input':a,'output':b,'direction':d,'rank':r,'owned':tag[2],'phase_mutation_rejected':True});controlled.add(tag)
            seen.add(key);classes+=1;ranks[r]=ranks.get(r,0)+1;fieldinstances+=sum(x['direction']==d for x in pairs[a,b]['occurrences'])
            write_line(evidence,{'input':a,'output':b,'direction':d,'rank':r,'occurrences':[x for x in pairs[a,b]['occurrences']if x['direction']==d],'recipe_sha256':hashlib.sha256(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'all18Paulis_equal':True,'exact_nonzero_unit_norm_anchor_equal':True,'physical_Fourier_rank':r,'anchor_nonzero_entries':sum(v!=(0,0)for v in anchor),'anchor_denominator_power_of_two':den})
            if classes%500==0:print('VERIFIED_ORIENTED_CLASSES',classes,flush=True)
    expected={(a,b,x['direction'])for(a,b),p in pairs.items()for x in p['occurrences']}
    complete=seen==expected
    need(complete or args.allow_partial,'complete actual paid phase class coverage')
    need(classes==head['proposed_oriented_classes'],'catalogue record count exact')
    if complete:need(fieldinstances==6596,'all paid occurrences covered both orientations')
    return {'status':'PASS_ALL_PAID_PAIR_PHASES_BOTH_ACTUAL_ORIENTATIONS'if complete else'PASS_PARTIAL_PAID_PHASE_PILOT','complete':complete,'unique_union_pairs':len({(a,b)for a,b,d in seen}),'oriented_classes':classes,'covered_paid_event_instances':fieldinstances,'complete_paid_event_instances':counts,'ranks_oriented_class_count':ranks,'controls':controls,'catalog_sha256':hashlib.sha256(args.catalog.read_bytes()).hexdigest(),'evidence_sha256':hashlib.sha256(args.evidence.read_bytes()).hexdigest(),'independent_verifier_imported_source_compiler':False,'source_compiler_truth_assumed':False}

def run():
    import tempfile
    start=time.monotonic();check,C,c,pairs,counts=setup()
    source.local('PAID-CATALOG.jsonl.gz')
    with tempfile.TemporaryDirectory(prefix='4610-paid-') as tmp:
        args=argparse.Namespace(catalog=PACKAGE/'PAID-CATALOG.jsonl.gz',evidence=pathlib.Path(tmp)/'evidence.jsonl.gz',allow_partial=False)
        out=verify(args,check,C,c,pairs,counts)
    out['seconds']=time.monotonic()-start
    return out
