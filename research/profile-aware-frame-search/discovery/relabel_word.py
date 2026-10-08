"""Rename point coordinates, all source/output triples and physical frames.

No scratch role or XOR instruction is omitted. This searches the exact
ordered-prefix projector profile after a simultaneous point-label permutation.
Every transformed word requires fresh full-basis/frame/profile verification.
The complete data-triple family and permutation-invariant I+J basis are retained.
"""
from pathlib import Path
from itertools import combinations
import argparse,gzip,hashlib,json

def main():
    p=argparse.ArgumentParser();p.add_argument('word',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--mode',choices=['reverse','evenodd','halves','shift1','shift2','swap01','swapmid','adjacent'],required=True)
    p.add_argument('--swap-index',type=int)
    a=p.parse_args();raw=gzip.decompress(a.word.read_bytes());w=json.loads(raw);h=w['h'];v=w['v']
    if a.mode=='reverse':perm=list(range(h-1,-1,-1))
    elif a.mode=='evenodd':perm=list(range(0,h,2))+list(range(1,h,2))
    elif a.mode=='halves':
        left=list(range((h+1)//2));right=list(range((h+1)//2,h));perm=[]
        for i in range(len(left)):
            perm.append(left[i])
            if i<len(right):perm.append(right[i])
    elif a.mode.startswith('shift'):perm=[(i+int(a.mode[-1]))%h for i in range(h)]
    else:
        perm=list(range(h));i=a.swap_index if a.mode=='adjacent' else (0 if a.mode=='swap01' else h//2)
        assert i is not None and 0<=i<h-1
        perm[i],perm[i+1]=perm[i+1],perm[i]
    assert sorted(perm)==list(range(h))
    def mask(m):return sum(1<<perm[i]for i in range(h)if m>>i&1)
    triples=list(combinations(range(h),3));lookup={t:i for i,t in enumerate(triples)}
    index=[lookup[tuple(sorted(perm[x]for x in t))]for t in triples]
    assert sorted(index)==list(range(v))
    w['frames']=[[mask(c),mask(u)]for c,u in w['frames']]
    w['sources']={str(index[int(i)]):s for i,s in w['sources'].items()}
    w['outputs']=[[s,g,perm[c],sorted(perm[x]for x in t)]for s,g,c,t in w['outputs']]
    w['scatter']=[[v+index[t-v],s]for t,s in w['scatter']]
    transformed=(json.dumps(w,separators=(',',':'))+'\n').encode('utf-8')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(transformed)
    receipt={'scope':'simultaneous point/frame/source-triple/output-triple coordinate renaming; no instruction or physical role removed',
             'mode':a.mode,'point_permutation':perm,'h':h,'roles':w['R'],
             'source_word_sha256':hashlib.sha256(raw).hexdigest(),'word_sha256':hashlib.sha256(transformed).hexdigest()}
    a.output.with_suffix(a.output.suffix+'.rename.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
