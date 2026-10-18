"""Exhaust a fixed two-edge neighborhood of three PR941 arithmetic optima."""
import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
OLD=ROOT/'research/r439-helper-matching'
WORD='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
FILES={WORD}|{'research/r439-helper-matching/'+x for x in (
    'build.py','common.py','verify.py','NOMINATION.json','README.md','PROOF.md','NOTICE.md',
    'vendor/pr915/candidate.json.gz','vendor/pr915/CERTIFICATE.json')}


def need(ok,msg):
    if not ok:raise ValueError(msg)


def canonical(x):return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def load(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def sha(path):
    raw=path.read_bytes();return hashlib.sha256(raw if path.suffix=='.gz' else raw.replace(b'\r\n',b'\n')).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def pins():
    p=load(P/'SOURCES.json');need(set(p['files'])==FILES,'source inventory')
    need(p['base_commit']=='abdc6a7002abdbcd9e21bfc5e1a795784deacfdf','base')
    for name,h in p['files'].items():need(sha(ROOT/name)==h,'source hash: '+name)
    need(sha(P/'BASE-SELECTED.json')==p['selected_snapshot_sha256'],'selected snapshot')


def columns(parent):
    v=parent['v'];out=[0]*parent['R'];middle=parent['D'][306:306+v]
    need([t for f,t,ss in middle]==list(range(v,2*v)),'middle target coverage')
    for f,t,ss in middle:
        need(f==0 and len(ss)==len(set(ss)),'middle row')
        for s in ss:need(2*v<=s<2*v+parent['R'],'middle helper');out[s-2*v]^=1<<(t-v)
    return out


def score(cols,pair):
    a,b=pair;return cols[b].bit_count()-(cols[a]^cols[b]).bit_count()-2


def enumerate_words(nominations,cols):
    result={};proposals=0;counts=[]
    for source,entry in enumerate(nominations):
        pairs=[tuple(x) for x in entry['pairs']];local=set()
        for i,j in itertools.combinations(range(len(pairs)),2):
            a,b=pairs[i];c,d=pairs[j];old=score(cols,pairs[i])+score(cols,pairs[j])
            for matching in (((a,b),(c,d)),((a,c),(b,d)),((a,d),(b,c))):
                for x,y in itertools.product((0,1),repeat=2):
                    e=matching[0][::1 if x==0 else -1];f=matching[1][::1 if y==0 else -1];proposals+=1
                    if score(cols,e)+score(cols,f)!=old:continue
                    key=tuple(sorted([p for k,p in enumerate(pairs) if k not in (i,j)]+[e,f]))
                    local.add(key)
                    result.setdefault(key,dict(source=source,remove=[i,j],insert=[list(e),list(f)]))
        counts.append(len(local))
    return result,proposals,counts


def boundary(word):
    n=2*word['v']+word['R'];values=[1<<j for j in range(n)]
    for f,t,ss in word['D']:
        need(f==0 and len(ss)==len(set(ss)),'D shape')
        for s in ss:values[t]^=values[s]
    return values


def run():
    pins();b=module('pr941_builder13',OLD/'build.py');v=module('pr941_verifier13',OLD/'verify.py')
    original=load(ROOT/WORD);parent=load(OLD/'vendor/pr915/candidate.json.gz');nom=load(OLD/'NOMINATION.json')
    rows,targets,gates=v.frozen_parent(original,parent)
    cols=columns(parent);as_sets=[{i for i in range(parent['v']) if col>>i&1} for col in cols]
    dual=v.dual_check(as_sets,nom['primary_dual'],nom['nominations'][0]['pairs'])
    need(dual['complete_ADD_floor']==11948,'inherited floor')
    words,proposals,counts=enumerate_words(nom['nominations'],cols)
    need(proposals==711624 and len(words)==857,'neighborhood inventory')
    wanted=boundary(parent);records=[];best=None;all_local=True
    for pairs,recipe in words.items():
        v.validate_pairs(pairs,parent['R'])
        need(sum(score(cols,pair) for pair in pairs)==1260,'preserved gain')
        candidate=b.assemble(parent,pairs)
        need(boundary(candidate)==wanted,'arbitrary dirty D boundary')
        bill=v.bill(candidate)
        need(bill['native_ADDs']==11948,'complete ADD price')
        need((b.positive(candidate),b.positive(candidate,True))==(bill['F'],bill['B']),'macro/literal positive agreement')
        local=64*bill['F']**3*bill['B']**2;nine=(1<<18)*bill['F']**5*bill['B']**4
        all_local &= local<(1<<104)
        record=dict(recipe=recipe,pairs_sha256=digest(pairs),**bill,
                    local_value=local,nine_value=nine,admitted=local<(1<<104) and nine<(1<<192))
        records.append(record)
        key=(nine,local,record['pairs_sha256'])
        if best is None or key<best[0]:best=(key,record,[list(x) for x in pairs])
    need(not any(x['admitted'] for x in records),'unexpected admitted neighbor')
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name)
        else:raise ValueError('accepted '+name)
    chosen=best[2]
    reject('overlapping_pairs',lambda:v.validate_pairs(chosen+[chosen[0]],parent['R']))
    reject('omit_two_paid_helper_gates',lambda:need(13208-sum(score(cols,p) +2 for p in chosen)==11948,'underpriced helpers'))
    reject('omit_nine_stage_guard',lambda:v.guards(best[1]['F'],best[1]['B']))
    changed=json.loads(json.dumps(nom['primary_dual']));changed['odd_sets']=[]
    reject('omit_odd_set_prices',lambda:v.dual_check(as_sets,changed,chosen))
    bad=b.assemble(parent,chosen);bad['D'].pop()
    reject('omit_final_restoration',lambda:need(boundary(bad)==wanted,'dirty helper restoration'))
    reject('claim_exhaustive_all_matchings',lambda:need(len({a for a,b in chosen}|{b for a,b in chosen})==parent['R'],'unmatched vertices excluded'))
    return dict(schema=1,status='passed',proposals=proposals,distinct_words=len(records),
                per_source_words=counts,local_guard_all_pass=all_local,admitted=0,dual=dual,
                records=records,best=best[1],best_pairs=chosen,mathematical_controls=controls,
                finite_neighborhood_only=True,native_replay=False,new_kappa=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--write-certificate',type=Path);args=p.parse_args();result=run()
    if args.write_certificate:
        with args.write_certificate.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    else:need(canonical(result)==canonical(load(P/'EXPECTED.json')),'certificate mismatch')
    print('PASS_MATCHING_NEIGHBORHOOD13 proposals=711624 words=857 admitted=0 controls=6')


if __name__=='__main__':main()
