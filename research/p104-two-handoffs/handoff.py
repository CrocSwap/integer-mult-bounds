"""Derive the two-hand-off word from PR5551's pinned word.  Apache-2.0.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Helper 473 (event 13725) and helper 531 (event 13941) each end their first
rank-1 climb at a dim-2 frame F and are then idle; no other register holds
their symbol.  The successor hand-off rewrites the rest of the helper's life
onto a fresh helper that starts at F.  Pure rename: same 25,310 events, no new
ADD, identical paid profile.  Scratch registers 735..742 shift to 737..744.

  default   : old helper ends at F; fresh helper starts at F and keeps the old final frame.
  --variant-a: no old/fresh split; the helper's leading MOVE is deleted and the
               helper starts at F (public stays 735, program shorter by 2).
"""
import gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPLITS=((473,13725),(531,13941))   # (helper, index of the MOVE reaching F)

def source():
    return json.load(gzip.open(HERE/'inputs'/'pr5551-WORD.json.gz'))

def need(ok,why):
    if not ok: raise ValueError(why)

def regs(e):
    return (1,) if e[0] in('MOVE','INIT','CLEAR','SCALE') else (1,2)

def check_leading(P,h,j):
    uses=[i for i,e in enumerate(P) if any(e[k]==h for k in regs(e))]
    need(uses[0]==j and P[j][0]=='MOVE',f'helper {h} first event is the climb to F')
    return uses

def handoff(w):
    w=json.loads(json.dumps(w));P=w['program']
    need(w['public']==735 and len(w['initial'])==735,'pinned PR5551 shape')
    new={h:735+i for i,(h,_) in enumerate(SPLITS)}
    shift=lambda x:x+2 if 735<=x<743 else x
    out=[];done={}
    for i,e in enumerate(P):
        e=list(e)
        for k in regs(e):
            x=e[k]
            e[k]=done.get(x,x) if x<735 else shift(x)
        out.append(e)
        for h,j in SPLITS:
            if i==j:
                need(e[:2]==['MOVE',h],'split event');F=e[3]
                check_leading(P,h,j)
                done[h]=new[h]
    w['program']=out;w['public']=737
    for h,j in SPLITS:
        F=P[j][3]
        w['initial'].append(F);w['final'].append(w['final'][h]);w['final'][h]=F
    return w

def variant_a(w):
    w=json.loads(json.dumps(w));P=w['program'];drop=set()
    for h,j in SPLITS:
        check_leading(P,h,j);need(P[j][2]==w['initial'][h],'climb starts at the initial frame')
        w['initial'][h]=P[j][3];drop.add(j)
    w['program']=[e for i,e in enumerate(P) if i not in drop]
    return w

def dump(w,path):
    raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
    with open(path,'wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as g: g.write(raw)

if __name__=='__main__':
    w=source()
    dump(handoff(w),HERE/'WORD.json.gz');dump(variant_a(w),HERE/'WORD-VARIANT-A.json.gz')
    print('wrote WORD.json.gz and WORD-VARIANT-A.json.gz')
