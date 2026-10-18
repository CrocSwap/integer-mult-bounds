"""Normalize PR1169's exact flow certificate for the retained T37 constructor.

The integer entries are unchanged. Width indices become literal widths;
physical window groups become explicit replica/child labels.
Credit Rohan Arun's PR1169, Ali Romman's PR1129 and the retained source notices.
"""
from common import P,read,dump

def normalize():
    d=read(P/'vendor/pr1169/research/three-demotions-t37-composition/PATTERN-FLOW.json')
    assert d['T']==37 and d['order']==read(P/'data/ORDER.json')
    ws=(4,5,7,8,9);xs={};ys={}
    for entry,n in d['entries']:
        assert type(n)is int and n>0
        if entry[0]=='x':
            _,g,p=entry;assert(g,p)not in xs;xs[g,p]=n
        else:
            assert entry[0]=='y';_,g,p,t,w=entry
            assert(g,p,t,w)not in ys and 0<=w<5;ys[g,p,t,w]=n
    result=[];used_x=set();used_y=set()
    for gi,(r,cap,ts,children)in enumerate(d['groups']):
        group=dict(physical_windows=[f'{r},{c}'for c in children],patterns=[])
        for pi,pat in enumerate(d['patterns'][str(cap)]):
            n=xs.get((gi,pi),0)
            if not n:continue
            used_x.add((gi,pi));assert len(pat)==5 and all(type(z)is int and z>=0 for z in pat)
            widths=[w for w,z in zip(ws,pat)for _ in range(z)]
            flows=[]
            for key,count in sorted(ys.items()):
                g,p,t,w=key
                if(g,p)==(gi,pi):flows.append([t,ws[w],count]);used_y.add(key)
            group['patterns'].append(dict(count=n,widths=widths,flow=flows))
        result.append(group)
    assert used_x==set(xs) and used_y==set(ys)
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=__import__('pathlib').Path,required=True);a=ap.parse_args()
    assert not a.out.exists();flow=normalize();assert flow==read(P/'data/FLOW.json.gz')
    dump(a.out,dict(status='PASS_PR1169_LITERAL_INTEGER_FLOW_NORMALIZATION',groups=len(flow)))
    print('PASS_PR1169_LITERAL_INTEGER_FLOW_NORMALIZATION')
