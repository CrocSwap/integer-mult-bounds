#!/usr/bin/env python3
"""Independent source-bound zero-normalised-stream proof; no physical admission."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

N, PUBLIC, DELETE = 1569, 1501, 38623
SOURCE_GZ = 'bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
SOURCE_CAN = 'c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
SOURCE_PATH = 'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz'
PATCH = {
 38369: (['MOVE',902,3,618,False], ['MOVE',902,3,373,False]),
 38623: (['MOVE',1091,373,618,False], None),
 40279: (['ADD',1091,902,'1/2',618], ['ADD',1091,902,'1/2',373]),
 40280: (['MOVE',1091,618,733,False], ['MOVE',1091,373,733,False]),
 41663: (['MOVE',902,618,913,False], ['MOVE',902,373,913,False]),
}
INCIDENTS = [
 (37928,['ADD',1091,1097,'1/2',373]),
 (38365,['ADD',643,902,'-1/4',3]), (38366,['ADD',496,902,'-1/2',3]),
 (38367,['ADD',1466,902,'1/2',3]), (38368,['ADD',450,902,'-1/2',3]),
 (38369,PATCH[38369][0]), (38623,PATCH[38623][0]),
 (40279,PATCH[40279][0]), (40280,PATCH[40280][0]),
 (40281,['ADD',1091,1093,'-1',733]), (40283,['MOVE',1091,733,238,False]),
 (40285,['ADD',1091,1087,'1',238]), (41663,PATCH[41663][0]),
 (41664,['ADD',985,902,'-1',913]),
]

class Refusal(ValueError):
    pass

def need(value, message):
    if not value:
        raise Refusal(message)

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_gz(path):
    raw = path.read_bytes()
    plain = gzip.decompress(raw)
    return json.loads(plain), sha(raw), plain

def check_exact_schema(result):
    need(isinstance(result,dict) and result.get('schema')=='compose7624-exact/v1', 'exact schema')

def literal_at(program, index, expected):
    need(type(index) is int and 0 <= index < len(program), 'source edit index')
    need(program[index] == expected, 'source edit literal')

def operand_roles(event):
    need(isinstance(event,list) and len(event)>=2, 'event shape')
    op = event[0]
    if op in ('ADD','COPY'):
        need(len(event)==5, 'binary shape')
        return {event[1],event[2]}
    if op in ('INIT','CLEAR'):
        need(len(event)==3, 'lifetime shape')
    elif op == 'MOVE':
        need(len(event)==5, 'move shape')
    elif op == 'SCALE':
        need(len(event)==4, 'scale shape')
    else:
        raise Refusal('unknown opcode')
    return {event[1]}

def normalized(event):
    op = event[0]
    operand_roles(event)
    if op == 'MOVE':
        return None
    if op in ('ADD','COPY'):
        return tuple(event[:4])  # chart is physical, not a normalized scalar coefficient
    if op == 'SCALE':
        return tuple(event[:3])
    return tuple(event[:2]) # INIT/CLEAR reset semantics; physical chart checked elsewhere

def map_and_rebuild(program, patch):
    for i,(old,_) in patch.items():
        literal_at(program,i,old)
    out=[]; origins=[]; reverse=[None]*len(program)
    for i,event in enumerate(program):
        if i in patch:
            event=patch[i][1]
            if event is None:
                continue
        reverse[i]=len(out); origins.append(i); out.append(event)
    return out,origins,reverse

def checked_origins(origins, reverse, n, deleted):
    need(type(n) is int and 0 <= deleted < n, 'invalid source origin boundary')
    need(isinstance(origins,list) and isinstance(reverse,list), 'map shape')
    need(all(type(x) is int and 0<=x<n for x in origins), 'origin type or bounds')
    need(len(reverse)==n and all((x is None if i==deleted else type(x) is int and 0<=x<n-1) for i,x in enumerate(reverse)), 'reverse type or bounds')
    expected=[i for i in range(n) if i != deleted]
    expected_reverse=[None if i==deleted else i if i<deleted else i-1 for i in range(n)]
    need(origins==expected and reverse==expected_reverse, 'origin or reverse map')

def index_observations(items, expected, label):
    need(isinstance(items,list), label+' observations not list')
    records={}
    for item in items:
        need(isinstance(item,dict), label+' observation not object')
        clock=item.get('original_clock')
        need(type(clock) is int and clock not in records, label+' duplicate or invalid clock')
        records[clock]=item
    need(set(records)==set(expected), label+' missing or unexpected observations')
    return records

def paired_observations(old, new, expected, reverse, label):
    a=index_observations(old,expected,label+' original')
    b=index_observations(new,expected,label+' candidate')
    for i in expected:
        need(type(a[i].get('candidate_clock')) is int and type(b[i].get('candidate_clock')) is int and a[i]['candidate_clock']>=0 and b[i]['candidate_clock']>=0 and a[i]['candidate_clock']==reverse[i] and b[i]['candidate_clock']==reverse[i], label+' clock binding')
        need(a[i]==b[i], label+' changed observation')
    return len(a)

def inventories(program):
    clears=[]; interfaces=[]; copies=[]; owned=[]
    for i,e in enumerate(program):
        operand_roles(e)
        op,r=e[:2]
        if op=='CLEAR': clears.append(i)
        if op=='COPY': copies.append(i)
        if (op=='SCALE' and r>=PUBLIC) or (op in ('ADD','COPY') and (r>=PUBLIC or e[2]>=PUBLIC)):
            interfaces.append(i)
        if op in ('INIT','CLEAR') or (op=='MOVE' and r>=PUBLIC):
            owned.append(i)
    return clears, interfaces, copies, owned

def owned_record_matches(record, event, lifetime):
    op,r=event[:2]
    need(record.get('op')==op and record.get('owner')==r and record.get('lifetime')==lifetime, 'owned stream identity')
    if op=='MOVE':
        need(record.get('from')==event[2] and record.get('to')==event[3], 'owned MOVE identity')
    else:
        need(record.get('chart')==event[2], 'owned lifecycle chart identity')

def compare_results(old,new,program,reverse,mains):
    expected_clears, expected_interfaces, expected_copies, expected_owned=inventories(program)
    need(tuple(map(len,(expected_clears,expected_interfaces,expected_copies,expected_owned)))==(204,700,1,455), 'source positive inventory census')
    counts={}
    for field,expected in (('clears',expected_clears),('interfaces',expected_interfaces),
                           ('copy_guards',expected_copies),('owned_stream',expected_owned)):
        counts[field]=paired_observations(old[field],new[field],expected,reverse,field)
    active={}; occurrences={}; stream=index_observations(old['owned_stream'],expected_owned,'owned identity')
    for i,e in enumerate(program):
        op,r=e[:2]
        if op=='INIT':
            need(r>=PUBLIC and r not in active, 'owned INIT identity')
            occurrences[r]=occurrences.get(r,0)+1; active[r]=occurrences[r]
        if i in stream:
            need(r in active, 'inactive owned stream')
            owned_record_matches(stream[i],e,active[r])
        if op=='CLEAR':
            need(r in active, 'inactive CLEAR')
            del active[r]
    need(not active, 'unclosed owned stream')
    for record in old['clears']:
        i=record['original_clock']; e=program[i]
        need((record.get('owner'),record.get('chart'))==(e[1],e[2]), 'CLEAR literal identity')
        need(record.get('lifetime')==stream[i].get('lifetime') and isinstance(record.get('row'),dict), 'CLEAR fields')
    for record in old['interfaces']:
        i=record['original_clock']; need(record.get('event')==program[i], 'owned interface literal')
        need('dest_before' in record and 'dest_after' in record, 'interface row fields')
    for record in old['copy_guards']:
        i=record['original_clock']; e=program[i]
        need((record.get('dest'),record.get('source'),record.get('chart'))==(e[1],e[2],e[4]), 'COPY literal identity')
        need(record.get('row')=={}, 'dirty COPY guard')
    need(new.get('virtual_deleted_interfaces',[])==[], 'unexpected deleted owned interface')
    need(len(old['endpoint_rows'])==len(new['endpoint_rows'])==N, 'endpoint census')
    need(old['endpoint_rows']==new['endpoint_rows'], 'endpoint rows changed')
    need(old['end_charts']==new['end_charts'], 'endpoint charts changed')
    need(len(old['end_charts'])==N, 'endpoint chart census')
    need(isinstance(mains,set) and mains and all(type(r) is int and 0<=r<PUBLIC for r in mains), 'main role census')
    changed=[r for r in sorted(mains) if old['endpoint_rows'][r]!={str(r):'1'}]
    need(changed, 'public main endpoint identity')
    counts['nonidentity_public_mains']=len(changed)
    return counts

def validate_manifest_maps(manifest,n,deleted,patch):
    checked_origins(manifest['candidate_origins'],manifest['original_to_candidate'],n,deleted)
    edits=manifest['edits']
    need(isinstance(edits,list) and all(isinstance(e,dict) and type(e.get('original_index')) is int and 0<=e['original_index']<n for e in edits), 'manifest edit index type or bounds')
    need(edits==[{'original_index':i,'old':a,'new_or_null':b} for i,(a,b) in patch.items()], 'manifest edits')

def control_fixture():
    program=[]; lists={k:[] for k in ('clears','interfaces','copy_guards','owned_stream')}
    def put(e,life):
        i=len(program);program.append(e);base={'original_clock':i,'candidate_clock':i};op,r=e[:2]
        if op in ('INIT','CLEAR','MOVE'):
            x={**base,'op':op,'owner':r,'lifetime':life}
            if op=='MOVE': x.update({'from':e[2],'to':e[3]})
            else: x['chart']=e[2]
            lists['owned_stream'].append(x)
        if op=='CLEAR': lists['clears'].append({**base,'owner':r,'lifetime':life,'chart':e[2],'row':{'0':'1'}})
        if op in ('ADD','COPY'):
            lists['interfaces'].append({**base,'event':e,'dest_before':{},'dest_after':{}})
            if op=='COPY': lists['copy_guards'].append({**base,'dest':r,'source':e[2],'chart':e[4],'row':{}})
    for life in range(1,205):
        put(['INIT',1501,0],life)
        if life==1:
            for _ in range(47):put(['MOVE',1501,0,0,True],life)
            for _ in range(699):put(['ADD',1501,0,'1',0],life)
            put(['COPY',1501,0,'1',0],life)
        put(['CLEAR',1501,0],life)
    endpoints=[{str(i):'1'} for i in range(PUBLIC)]+[{} for _ in range(N-PUBLIC)]
    endpoints[0]={'1':'1'}
    lists.update({'endpoint_rows':endpoints,'end_charts':[None]*N,'virtual_deleted_interfaces':[]})
    return program,lists

def controls():
    results=[]
    def reject(name,fn):
        try: fn()
        except (Refusal,KeyError,TypeError,IndexError):
            results.append(name); return
        raise Refusal('control accepted '+name)
    sample=[['ADD',0,1,'1',0],['MOVE',0,0,1,False],['CLEAR',1501,0]]
    literal_at(sample,0,sample[0])
    reject('bad_source_index',lambda:literal_at(sample,3,sample[0]))
    reject('bad_source_literal',lambda:literal_at(sample,0,['ADD',0,1,'2',0]))
    checked_origins([0,2],[0,None,1],3,1)
    reject('wrong_origin',lambda:checked_origins([0,1],[0,None,1],3,1))
    row={'original_clock':2,'candidate_clock':1,'owner':1501,'lifetime':1,'chart':0,'row':{'0':'1'}}
    paired_observations([row],[dict(row)],[2],[0,None,1],'toy')
    reject('missing_owned_observation',lambda:paired_observations([row],[],[2],[0,None,1],'toy'))
    reject('duplicate_owned_observation',lambda:paired_observations([row,row],[row],[2],[0,None,1],'toy'))
    altered=dict(row); altered['row']={'0':'2'}
    reject('altered_clear_row',lambda:paired_observations([row],[altered],[2],[0,None,1],'toy'))
    altered=dict(row); altered['chart']=1
    reject('altered_clear_event',lambda:owned_record_matches({'op':'CLEAR','owner':1501,'lifetime':1,'chart':1},sample[2],1))
    reject('empty_census',lambda:index_observations([], [2], 'toy'))
    reject('old_source_proof',lambda:check_exact_schema({'schema':'compose7623-exact/v1'}))
    reject('boolean_origin',lambda:checked_origins([False,2],[0,None,1],3,1))
    reject('boolean_reverse',lambda:checked_origins([0,2],[False,None,1],3,1))
    reject('negative_origin',lambda:checked_origins([-1,2],[0,None,1],3,1))
    toy_manifest={'candidate_origins':[0,2],'original_to_candidate':[0,None,1],'edits':[{'original_index':False,'old':sample[0],'new_or_null':None}]}
    reject('boolean_edit_index',lambda:validate_manifest_maps(toy_manifest,3,1,{0:(sample[0],None)}))
    toy_manifest['edits'][0]['original_index']=-1
    reject('negative_edit_index',lambda:validate_manifest_maps(toy_manifest,3,1,{0:(sample[0],None)}))
    program,base=control_fixture(); reverse=list(range(len(program)))
    def clone(x): return json.loads(json.dumps(x))
    compare_results(base,clone(base),program,reverse,{0})
    reject('empty_expected_inventory',lambda:compare_results(base,clone(base),[],[],{0}))
    for field in ('clears','interfaces','copy_guards','owned_stream'):
        inv_index={'clears':0,'interfaces':1,'copy_guards':2,'owned_stream':3}[field]
        removed=set(inventories(program)[inv_index])
        truncated=[e for i,e in enumerate(program) if i not in removed]
        empty_a,empty_b=clone(base),clone(base);empty_a[field]=[];empty_b[field]=[]
        reject(field+'_both_empty_expected',lambda a=empty_a,b=empty_b,p=truncated:compare_results(a,b,p,list(range(len(p))),{0}))
        for mode in ('both_empty','missing_original','missing_candidate','duplicate_original','duplicate_candidate'):
            a,b=clone(base),clone(base)
            if mode=='both_empty': a[field]=[];b[field]=[]
            elif mode=='missing_original': a[field].pop()
            elif mode=='missing_candidate': b[field].pop()
            elif mode=='duplicate_original': a[field].append(clone(a[field][0]))
            else: b[field].append(clone(b[field][0]))
            reject(field+'_'+mode,lambda a=a,b=b:compare_results(a,b,program,reverse,{0}))
    a,b=clone(base),clone(base);b['clears'][0]['row']={'0':'2'}
    reject('production_clear_row',lambda:compare_results(a,b,program,reverse,{0}))
    a,b=clone(base),clone(base);a['endpoint_rows'][0]={'0':'1'};b['endpoint_rows'][0]={'0':'1'}
    reject('identity_public_endpoint',lambda:compare_results(a,b,program,reverse,{0}))
    a,b=clone(base),clone(base);b['clears'][0]['candidate_clock']=False
    reject('boolean_observation_clock',lambda:compare_results(a,b,program,reverse,{0}))
    need(normalized(['COPY',2,1,'3',0])==('COPY',2,1,'3'), 'COPY positive')
    reject('altered_scalar',lambda:need(normalized(['ADD',0,1,'2',0])==normalized(sample[0]),'scalar changed'))
    return results

def prove(root,built,exact):
    source,source_gz,_=read_gz(root/SOURCE_PATH)
    need(source_gz==SOURCE_GZ and sha(canon(source))==SOURCE_CAN, 'source custody')
    candidate,candidate_gz,_=read_gz(built/'candidate-word.json.gz')
    manifest_raw=(built/'edit-manifest.json').read_bytes(); manifest=json.loads(manifest_raw)
    result,exact_gz,exact_raw=read_gz(exact/'EXACT.json.gz')
    status_raw=(exact/'status.json').read_bytes(); status=json.loads(status_raw)
    check_exact_schema(result)
    need(manifest.get('schema')=='compose7624-edit-manifest/v1','manifest schema')
    need(status.get('status')=='U_CONDITIONAL_LITERAL_EXACT_ONLY', 'exact status')
    need(exact_raw==canon(result), 'exact canonical encoding')
    need(status.get('exact_sha256')==sha(exact_raw) and status.get('exact_gzip_sha256')==exact_gz, 'exact receipt hash')
    need(status.get('source')==result.get('source'), 'exact status source binding')
    binding=result['source']; candidate_can=sha(canon(candidate))
    need(binding['original_canonical_sha256']==SOURCE_CAN and binding['original_gzip_sha256']==source_gz and
         binding['candidate_canonical_sha256']==candidate_can and binding['candidate_gzip_sha256']==candidate_gz and
         binding['manifest_sha256']==sha(manifest_raw), 'exact input binding')
    need(manifest['source_canonical_sha256']==SOURCE_CAN and manifest['source_gzip_sha256']==source_gz and
         manifest['candidate_canonical_sha256']==candidate_can and manifest['candidate_gzip_sha256']==candidate_gz, 'manifest binding')
    need((source['public'],source['owned_fields'],len(source['program']))==(PUBLIC,68,77372), 'source shape')
    need({k:v for k,v in source.items() if k!='program'}=={k:v for k,v in candidate.items() if k!='program'}, 'metadata changed')
    program=source['program']; rebuilt,origins,reverse=map_and_rebuild(program,PATCH)
    checked_origins(origins,reverse,len(program),DELETE)
    need(len(candidate['program'])==77371 and candidate['program']==rebuilt, 'candidate reconstruction')
    validate_manifest_maps(manifest,len(program),DELETE,PATCH)
    need(manifest['candidate_origins']==origins and manifest['original_to_candidate']==reverse, 'manifest map')
    actual=[(i,program[i]) for i in range(37928,41665) if operand_roles(program[i]) & {902,1091}]
    need(actual==INCIDENTS, 'typed incident mismatch')
    original_stream=[normalized(e) for e in program if e[0]!='MOVE']
    candidate_stream=[normalized(e) for e in candidate['program'] if e[0]!='MOVE']
    need(original_stream==candidate_stream, 'normalized scalar or reset stream changed')
    live=set(source['live']); mains=live|{x+112 for x in live}|set(source['hosted']['X2'])|set(source['hosted']['Y2'])
    counts=compare_results(result['original'],result['candidate'],program,reverse,mains)
    need(all(result['changed'][k]==[] for k in ('clears','interfaces','copy_guards')), 'changed observations nonempty')
    return {'schema':'compose7624-zero-proof/v1','status':'ZERO_NORMALIZED_STREAM_ONLY_UNQUALIFIED',
            'source_canonical_sha256':SOURCE_CAN,'source_gzip_sha256':source_gz,
            'candidate_canonical_sha256':candidate_can,'candidate_gzip_sha256':candidate_gz,
            'manifest_sha256':sha(manifest_raw),'exact_sha256':sha(exact_raw),'exact_gzip_sha256':exact_gz,
            'exact_status_sha256':sha(status_raw),'edits':5,'deleted_source_clock':DELETE,
            'incident_count':len(actual),'normalized_nonmove_count':len(original_stream),'observation_counts':counts,
            'scope':'Exact normalized stream induction and observed equality under explicit common U; no phase, physical, resource, certificate or price qualification.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--built',type=Path);p.add_argument('--exact',type=Path);p.add_argument('--out',type=Path);p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        if any(x is not None for x in (a.root,a.built,a.exact,a.out)): p.error('controls-only takes no paths')
        try:
            result=controls(); print(json.dumps({'status':'PASS_SOURCE_FREE_PROOF_CONTROLS','controls':result},sort_keys=True)); return 0
        except Exception as e:
            print(json.dumps({'status':'REFUSED','type':type(e).__name__,'reason':str(e)},sort_keys=True)); return 1
    if any(x is None for x in (a.root,a.built,a.exact,a.out)): p.error('all paths required')
    a.out.mkdir(parents=True,exist_ok=False)
    try:
        control_results=controls(); receipt=prove(a.root,a.built,a.exact);receipt['rejected_controls']=control_results
        raw=canon(receipt);(a.out/'proof.json').write_bytes(raw+b'\n')
        status={'status':receipt['status'],'proof_sha256':sha(raw+b'\n'),'controls':len(control_results)};code=0
    except Exception as e:
        status={'status':'REFUSED','type':type(e).__name__,'reason':str(e)};code=1
    (a.out/'status.json').write_bytes(canon(status)+b'\n');print(json.dumps(status,sort_keys=True),flush=True)
    return code
if __name__=='__main__':
    raise SystemExit(main())
