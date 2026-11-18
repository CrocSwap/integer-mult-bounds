# SPDX-License-Identifier: Apache-2.0
"""Compose two literal edit manifests; no replay or scientific calculation."""
import gzip, hashlib, json, runpy
from pathlib import Path
H=Path(__file__).resolve().parent
P=H
def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def main():
    u=runpy.run_path(str(H/'word_checks.py'))
    base=read(P/'source7644/retained/pr7605/data/word.json.gz')
    prev=read(P/'baseline.json.gz')
    candidate_path=H/'candidate.json.gz'
    assert sha(gzip.decompress(candidate_path.read_bytes()))=='450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66'
    candidate=read(candidate_path)
    assert sha(canonical(prev))=='6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
    tagged=u['reconstruct'](base,read(P/'baseline-edits.json'))
    assert [e for _,e in tagged]==prev['program']
    m=read(H/'manifest.json')
    aligned={v:int(k) for k,v in m['aligned_origins'].items()}
    inserts={x['candidate_clock']:x['event'] for x in m['inserted']}
    assert len(aligned)+len(inserts)==len(candidate['program'])
    assert set(aligned).isdisjoint(inserts) and set(aligned)|set(inserts)==set(range(len(candidate['program'])))
    result=[]
    for i,e in enumerate(candidate['program']):
        if i in aligned:
            j=aligned[i]; assert prev['program'][j]==e; result.append(tagged[j])
        else:
            assert inserts[i]==e; result.append((-1,e))
    retained=[i for i,e in result if i>=0]
    assert retained==sorted(set(retained))
    retained_set=set(retained)
    delete=[[i,e] for i,e in enumerate(base['program']) if i not in retained_set]
    before={}; pending=[]
    for i,e in result:
        if i<0: pending.append(e)
        else:
            if pending: before[i]=pending; pending=[]
    assert not pending
    edits={'base_events':len(base['program']),'delete':delete,'insert_before':[[i,es] for i,es in before.items()],'append':[]}
    assert [e for _,e in u['reconstruct'](base,edits)]==candidate['program']
    assert {k:v for k,v in base.items() if k!='program'}=={k:v for k,v in candidate.items() if k!='program'}
    out=H/'combined-edits.json'; assert not out.exists()
    out.write_text(json.dumps(edits,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'edits_sha256':sha(out.read_bytes()),'candidate_canonical_sha256':sha(canonical(candidate)),'deleted':len(delete),'insertion_anchors':len(before)}))
if __name__=='__main__': main()
