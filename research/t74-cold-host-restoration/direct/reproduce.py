"""Portable source-bound direct-restoration census (standard library only)."""
from pathlib import Path
import argparse,sys,json,lzma,hashlib,time,concurrent.futures,os,copy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from engine import check_case,require,Model,FULL,recovery,first_missing,basis,subset,verify_derivation


def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def worker(item):return check_case(*item)


def inputs():
 pins=json.loads((HERE/'SOURCE-PINS.json').read_text());raw=(HERE/'words.json.xz').read_bytes()
 require(digest(raw)==pins['words_json_xz_sha256'],'words archive digest')
 data=lzma.decompress(raw);require(digest(data)==pins['words_json_uncompressed_sha256'],'words payload digest')
 words=json.loads(data);require(set(words)==set(pins['canonical_word_payloads']),'case inventory')
 for name,w in words.items():require(digest(canonical(w))==pins['canonical_word_payloads'][name],('word pin',name))
 parents_data=(HERE/'parents.json.xz').read_bytes();require(digest(parents_data)==pins['parents_json_xz_sha256'],'parent archive digest')
 parents=json.loads(lzma.decompress(parents_data))
 for name,w in words.items():
  h,c=map(int,name[2:].split('_'));verify_derivation(parents[name[0]],w,h,c)
 return words


def controls(words):
    w=words['b-473_277'];m=Model(w);rows,_=recovery(w,m)
    require(rows[0]['expression']=={'277':'1','100':'-1','226':'-1','54':'1'},'positive scalar recovery fixture')
    require(rows[0]['rank']==8,'positive framefloor fixture')
    # A width9 cold fixture after all old restores is feasible. It is the
    # operator lane's independently audited fixture with only frames checked here.
    p=copy.deepcopy(w);c=277;p['A'].insert(0,['warp',c,-73,[],[]]);p['prelude_events']+=1
    p['helper_final'][str(c)]=list(FULL)
    for q,a,b in ((100,-1,2),(226,-1,1),(54,1,1),(67,1,1)):
        p['restore'].append(['add',c,q,a,b,list(FULL)])
    require(not Model(p).violations,'positive FULL-end frame fixture')
    q=copy.deepcopy(p);q['helper_final'][str(c)]=rows[0]['floor_join']
    require(Model(q).violations,'rank8 full-tail mutant not rejected')
    q=copy.deepcopy(w);q['B'][q['warps'][-1][0]][3]*=-1
    changed,_=recovery(q,Model(q));require(changed[0]['expression']!=rows[0]['expression'],'flipped write mutant not detected')
    q=copy.deepcopy(w);q['warps'][-1][3]=[]
    require(Model(q).violations,'changed warp frame mutant not rejected')
    q=copy.deepcopy(w);q['ports'][0]^=1
    require(Model(q).violations,'changed port-frame mutant not rejected')
    return dict(positive_fixtures=3,negative_controls=4,status='PASS')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=8);p.add_argument('--output',type=Path);p.add_argument('--quick',action='store_true');args=p.parse_args()
    require(1<=args.workers<=24,'workers must be1..24');start=time.monotonic();words=inputs();ctrl=controls(words)
    expected=json.loads((HERE/'EXPECTED.json').read_text());names=sorted(words)
    if args.quick:names=expected['quick_cases']
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(worker,((name,words[name],True) for name in names)):
            e=expected['cases'][r['case']]
            for key in ('slots','B_boundary_checks','min_rank','rows_sha256','classes','orders'):
                require(r[key]==e[key],('replay mismatch',r['case'],key,r[key],e[key]))
            require(r['target_end_witnesses']==r['orders'],('non-target obstruction needs narrower claim',r['case']))
            for rr in r['results']:
                ww=rr['witness'];port=words[r['case']]['ports'][ww['register']-112]
                require((port&ww['missing_vector']).bit_count()%2==1,'target cap witness does not violate port parity')
            results.append(r)
    out=dict(status='PASS_INDEPENDENT_DIRECT_RESTORATION_FRAME_CENSUS',quick=args.quick,cases=len(results),slots=sum(r['slots'] for r in results),B_boundary_checks=sum(r['B_boundary_checks'] for r in results),classes=sum(r['classes'] for r in results),orders=sum(r['orders'] for r in results),target_end_witnesses=sum(r['target_end_witnesses'] for r in results),minimum_rank=min(r['min_rank'] for r in results),controls=ctrl,seconds=time.monotonic()-start,scope=expected['scope'],results=results)
    if args.output:
        require(not args.output.resolve().is_relative_to(HERE.resolve()),'output must be outside verifier directory')
        args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='results'},sort_keys=True))
if __name__=='__main__':main()
