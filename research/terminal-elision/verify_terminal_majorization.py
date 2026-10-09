"""Exact full-profile concavity certificate for distinct-target elisions."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def check(ok,msg):
    if not ok:raise ValueError(msg)


def main():
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True)
    p.add_argument('--old-profile',type=Path,required=True)
    p.add_argument('--elision',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();w=json.loads(gzip.decompress(a.word.read_bytes()))
    e=json.loads(gzip.decompress((a.elision/'word.json.gz').read_bytes()))
    old=json.loads(a.old_profile.read_text());new=json.loads((a.elision/'complex-profile.json').read_text())
    h,v=w['h'],w['v'];m=h*h
    frames={int(k):F for k,F in w['frames'].items()};sigma={int(k):F for k,F in w['sigma'].items()}
    roots={int(k):r for k,r in w['role_root'].items()}
    M=[0]*v
    for s in w['deferred']:
        for t in w['reach'][s]:M[t]=max(M[t],len(sigma[s]))
    formula=Counter();used=set();rows=[]
    for s in e['removed']:
        j=roots[s];t=w['target'][j]
        check(not w['kind'][j] and t not in used,'requires distinct ordinary targets')
        used.add(t);sig=len(sigma[s]);f=len(frames[w['first_node'][s]])
        check(sig<=M[t]<=f<=h-1,'packet order')
        before=sorted([m-h+sig,1,f-sig,h-1-M[t]],reverse=True)
        after=sorted([m,f-M[t],0,0],reverse=True)
        check(sum(before)==sum(after),'packet masses')
        check(all(sum(after[:k])>=sum(before[:k]) for k in range(1,5)),'majorization')
        check(after!=before,'strict majorization')
        for z in before:
            if z:formula[z]-=2*v
        for z in after:
            if z:formula[z]+=2*v
        rows.append(dict(role=s,target=t,sigma=sig,first=f,last_old_target=M[t],before=before,after=after))
    actual=Counter({int(t):c for t,c in new['child_multiplicities'].items()})
    actual.subtract({int(t):c for t,c in old['child_multiplicities'].items()})
    actual[m]+=old['W']-new['W']
    check(all(actual[t]==formula[t] for t in actual.keys()|formula.keys()),'full-profile linkage')
    hinges=[sum(min(t,k)*c for t,c in actual.items()) for k in range(1,m+1)]
    check(max(hinges)==0 and min(hinges)<0,'all-concave full profile')
    check(old['deficit']==new['deficit'],'deficit')
    out=dict(passed=True,roles=len(rows),packet_rows=rows,full_hinge_differences=hinges,
        complete_padded_delta={t:c for t,c in sorted(actual.items()) if c},
        statement='New profile plus (W_old−W_new) width-m dummy children strictly improves every power t^p for 0<p<1.',
        hashes={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in
                [a.word,a.old_profile,a.elision/'word.json.gz',a.elision/'complex-profile.json',Path(__file__)]})
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,roles=len(rows),hinge_min=min(hinges),hinge_max=max(hinges))))


if __name__=='__main__':main()
