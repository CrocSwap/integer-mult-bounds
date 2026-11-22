"""Rebuild the all-but-one-terminal balanced fusion from the native #8027 word."""
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

def build(g):
    p=g['program'];assert p[7110:7113]==[['INIT',2241,0],['ADD',2241,626,0],['MOVE',2241,0,509]] and p[7208:7211]==[['INIT',2252,509],['ADD',2252,1528,509],['MOVE',2252,509,1]] and p[21250]==['ADD',3317,626,0]
    edit={7110:[['INIT',2241,509]],7111:[['ADD',2241,1528,509]],7112:[],7208:[['INIT',2252,0]],7209:[['ADD',2252,626,0]],7210:[['MOVE',2252,0,1]],21250:[]}
    tape=[r for k,row in enumerate(p) for r in edit.get(k,[row])]+[['SWAP',38,626]]+[['ADD',d,s,1] for d in (33,77,87) for s in (38,626)]
    return dict(g,program=tape)

def check(g,changed=False):
    n=g['public'];ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};clears={}
    for op,d,*a in g['program']:
        if op=='INIT':assert d not in ch;ch[d],v[d]=a[0],0
        elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
        elif op=='MOVE':assert ch[d]==a[0];ch[d]=a[1]
        elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
        elif op=='CLEAR':assert ch.pop(d)==a[0];clears[d]=(a[0],v.pop(d))
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['final']));assert [v[i] for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0)^((1<<38) if changed and i==130 else 0) for i in range(n)]
    assert len(clears)==3433;return clears

def reverse(g):
    n=g['public'];ch=dict(enumerate(g['final']));v={i:1<<i for i in ch}
    for op,d,*a in reversed(g['program']):
        if op=='CLEAR':assert d not in ch;ch[d],v[d]=a[0],0
        elif op=='INIT':assert ch.pop(d)==a[0];del v[d]
        elif op=='ADD':s,c=a;assert ch[s]==ch[d]==c;v[s]^=v[d]
        elif op=='MOVE':assert ch[d]==a[1];ch[d]=a[0]
        elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['start'])) and [v[i] for i in range(n)]==[(1<<i)^((1<<(i+111)) if i<111 else 0)^((1<<130) if i==38 else 0) for i in range(n)]

if __name__=='__main__':
    data=Path(sys.argv[1]).read_bytes();assert sha256(data).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326';orig=json.loads(gzip.decompress(data));changed=build(orig);c=check(orig);cc=check(changed,True);reverse(changed);
    try:check(dict(changed, program=changed['program'][:-1]),True)
    except AssertionError:pass
    else:raise AssertionError('missing final local correction accepted')
    assert [(i,x[0]) for i,x in c.items()]==[(i,x[0]) for i,x in cc.items()];raw=(json.dumps(changed,sort_keys=True,separators=(',',':'))+'\n').encode();Path(sys.argv[2]).write_bytes(gzip.compress(raw,mtime=0));print(json.dumps({'target_rows_exact':629,'error_row':130,'residual_support':[38],'other_rows_exact':True,'source_program_sha256':sha256(data).hexdigest(),'changed_expanded_sha256':sha256(raw).hexdigest(),'instructions':len(changed['program']),'native_instructions':len(orig['program']),'private_clears':len(cc),'reverse_transpose_exact':True,'corrupt_last_add_rejected':True,'changed_dirty_clear_fields':sum(cc[i]!=c[i] for i in c),'changed_clear_owners':[i for i in c if cc[i]!=c[i]],'nonzero_clears':sum(bool(r) for s,r in cc.values())},sort_keys=True,indent=2))
