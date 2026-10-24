"""Discovery: move an existing logical warp to alternative transported frames.

Native source: Cinna Davis PR4470, retained credited dependencies. The universal
transported-frame lemma is credited to research/transported-warp-frames.
Apache-2.0; substantial OpenAI Codex assistance. No improvement is assumed.
"""
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/joint-helper-lattice'))
import native_joint as J
F=J.F


def roles(e):
    if e[0]=='scalar':
        g=e[1];return [r[1] for r in (g[1:3] if g[0] in ('add','copy') else g[1:2]) if r[0]=='L']
    return [e[1][1]] if e[0]=='warp' else []


def synthesize(c,program):
    current=c['start'][:];spaces=[F.span(b) for b in c['frames']];out=[]
    def climb(r,new):
        old=current[r]
        if old==new:return
        F.need(spaces[old]<spaces[new],f'Positive reconstructed transport role={r} old={old} new={new} dimensions={len(c["frames"][old])},{len(c["frames"][new])}')
        out.append(['climb','warp_retimed',r,old,new,len(c['frames'][new])-len(c['frames'][old])]);current[r]=new
    for e in program:
        if e[0]=='climb':continue
        if e[0]=='scalar':
            for r in roles(e):climb(r,e[2])
        elif e[0]=='warp':climb(e[1][1],e[3]);current[e[1][1]]=e[4]
        out.append(deepcopy(e))
    for r,new in enumerate(c['final']):climb(r,new)
    return out


def main():
    c,programs,*_=J.construct();spaces=[F.span(b) for b in c['frames']];dims=[len(b) for b in c['frames']]
    mappings={}
    for w in c['warps']:
        cols=w['G_columns'];a=[]
        for x in range(512):
            y=0
            for k,v in enumerate(cols):
                if x>>k&1:y^=v
            a.append(y)
        F.need(len(set(a))==512,'Invertible native map');mappings[w['op']]=a
        b=[0]*512
        for x,y in enumerate(a):b[y]=x
        mappings[-w['op']]=b
    p=[deepcopy(e) for e in programs['forward'] if e[0]!='climb']
    prev,nxt={},{};cur=c['start'][:]
    for i,e in enumerate(p):
        for r in roles(e):prev[i,r]=cur[r];cur[r]=e[4] if e[0]=='warp' else e[2]
    cur=c['final'][:]
    for i in reversed(range(len(p))):
        e=p[i]
        for r in roles(e):nxt[i,r]=cur[r];cur[r]=e[3] if e[0]=='warp' else e[2]
    nominees=[]
    for i,e in enumerate(p):
        if e[0]!='warp':continue
        _,role,op,old,new=e;r=role[1];M=mappings[op]
        image=frozenset(M[x] for x in spaces[old])
        F.need(image==spaces[new],'Original exact transported-frame identity')
        lo,hi=prev[i,r],nxt[i,r];before=dims[old]-dims[lo];after=dims[hi]-dims[new]
        F.need(before>=0 and after>=0,'Original monotone neighbor frames')
        output=frozenset(M[x] for x in spaces[lo]);F.need(output<=spaces[hi],'New warp output fits exact next cap')
        if before and after:
            t=1-.00302016597705;gain=before**t+after**t-(before+after)**t
            nominees.append({'event':i,'role':r,'operator':op,'old_input':old,'old_output':new,
                             'new_input':lo,'new_output_span':sorted(output),'next_cap':hi,
                             'before_rank':before,'after_rank':after,'merged_rank':before+after,
                             'moment_reduction':gain})
    nominees.sort(key=lambda x:x['moment_reduction'],reverse=True)
    record={'status':'DISCOVERY_ONLY','tested_warps':sum(e[0]=='warp' for e in p),'nominees':nominees}
    (HERE/'MERGE-SCREEN.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'tested_warps':record['tested_warps'],'nominee_count':len(nominees),'best':nominees[:3]},sort_keys=True))
    if not nominees:return
    best=nominees[0];output=frozenset(best['new_output_span'])
    labels={s:i for i,s in enumerate(spaces)}
    if output not in labels:
        # Every span is supplied as an exact independent basis.
        basis=[];span={0}
        for x in sorted(output):
            if x not in span:basis.append(x);span|={y^x for y in tuple(span)}
        c['frames'].append(basis);labels[output]=len(c['frames'])-1
    new_output=labels[output]
    altered={}
    for direction,word in programs.items():
        raw=[deepcopy(e) for e in word if e[0]!='climb']
        F.need(raw[best['event']][0]=='warp' and raw[best['event']][1]==['L',best['role']] and raw[best['event']][2]==best['operator'],'Exact dual warp event correspondence')
        raw[best['event']][3:5]=[best['new_input'],new_output]
        altered[direction]=synthesize(c,raw)
    prof={d:Counter(e[5] for e in word if e[0]=='climb') for d,word in altered.items()}
    for d,word in altered.items():prof[d].update(e[4] for e in word if e[0]=='center')
    F.need(prof['forward']==prof['backward'],'Equal complete dual paid profiles')
    best['new_output']=new_output;best['paid']=dict(prof['forward'])
    (HERE/'CANDIDATE.json').write_text(json.dumps(best,indent=2,sort_keys=True)+'\n')
    payload={'canonical':c,'programs':altered}
    (HERE/'CANDIDATE-WORD.json.gz').write_bytes(gzip.compress(json.dumps(payload,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print('CANDIDATE',json.dumps(best,sort_keys=True))


if __name__=='__main__':main()
