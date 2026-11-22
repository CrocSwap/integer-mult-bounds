#!/usr/bin/env python3
"""Independent reconstruction of the literal chart-8 failed relay."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

SOURCE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
DONORS=(2841,2842,2942,2965,2966,2967,3003,3023,3045)

def rank(rows):
    b={}
    for v in rows:
        while v:
            p=v&-v
            if p not in b:b[p]=v;break
            v^=b[p]
    return len(b)

def execute(g,changed=False,drop_donor=None):
    at=dict(enumerate(g['start']));val={i:1<<i for i in at};seen={};cost=Counter();clears=Counter()
    dims={int(k):v['dim'] for k,v in g['frames'].items()}
    def step(row):
        op,i,*a=row
        if op=='INIT':assert i not in at;at[i]=a[0];val[i]=0
        elif op=='ADD':j,c=a;assert at[i]==at[j]==c;val[i]^=val[j]
        elif op=='MOVE':s,t=a;assert at[i]==s;at[i]=t;cost[abs(dims[s]-dims[t])]+=1
        elif op=='SWAP':j,=a;at[i],at[j]=at[j],at[i];val[i],val[j]=val[j],val[i]
        elif op=='CLEAR':assert at.pop(i)==a[0];clears['nonzero' if val.pop(i) else 'zero']+=1
        else:raise AssertionError(op)
    for k,row in enumerate(g['program']):
        if changed and 10994<=k<=11013:
            if k!=10994:continue
            step(['INIT',3148,1])
            for j in DONORS:
                if j!=drop_donor:step(['ADD',3148,j,1])
            seen['new_payload']=val[3148]
            step(['MOVE',3148,1,8]);step(['INIT',3150,0])
            continue
        if changed and row[:2]==['CLEAR',3149]:continue
        if changed and row[:2]==['CLEAR',3148]:step(['CLEAR',3148,8]);continue
        if changed and k==11026:step(['ADD',3153,3148,8])
        if k==11013:seen['native_first_return']=val[row[1]]
        if k==11026:seen['second_return']=val[row[1]]
        step(row)
    assert at==dict(enumerate(g['final']))
    return [val[i] for i in range(g['public'])],seen,cost,clears

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',nargs='?',type=Path,default=SOURCE)
    args=parser.parse_args();raw=args.source.read_bytes();assert sha256(raw).hexdigest()==SHA
    g=json.loads(gzip.decompress(raw))
    native,old,co,dc=execute(g);changed,new,cn,dn=execute(g,True)
    assert native==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    f=old['native_first_return'];assert new['new_payload']==f
    assert new['second_return']==old['second_return']^f
    bad=[i for i in range(630) if native[i]!=changed[i]]
    assert len(bad)==54 and all(native[i]^changed[i]==f for i in bad)
    assert rank(native)==rank(changed)==630
    assert co-cn==Counter({1:1,2:1,4:1}) and cn-co==Counter({7:1})
    broken,_,_,_=execute(g,True,DONORS[0]);assert broken!=changed
    print(json.dumps({'native_sha256':SHA,'new_send_owner':3148,'new_target_chart':8,
      'top_donors':DONORS,'top_send_equals_native_first_return':True,
      'recoded_second_return_equals_original_xor_first':True,
      'changed_public_operator_rank':rank(changed),'incorrect_output_count':len(bad),
      'all_errors_equal_first_return':True,'removed_grades':dict(co-cn),'added_grades':dict(cn-co),
      'private_clears':dict(dn),'omitted_donor_mutation_detected':True},sort_keys=True,indent=2))

if __name__=='__main__':main()
