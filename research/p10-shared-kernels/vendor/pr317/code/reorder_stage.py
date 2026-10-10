#!/usr/bin/env python3
"""Reorder stage on the actual w3 word: just-in-time MOVE normalisation plus commuting-ADD relocation.

Each register's frame path is rebuilt from the frames of its actual incidences (ADD operands, COPY/ERASE
centres): before every event each operand climbs directly to the event frame (one nested MOVE), and after the
last event to its final frame. A relocation takes an ADD a += c*b out of a frame that is a strict breakpoint of
an operand path and executes it immediately before/after a neighbouring ADD incidence of a or b, inside that
incidence's frame, when no crossed event reads a (ADD source, COPY, ERASE) or writes b; the ADD then commutes
with every crossed event over every commutative coefficient ring. Moves are priced on the rebuilt paths with
phi(r) = r ln(100/r) and kept greedily over disjoint operand sets; round k screens the word after round k-1.
The screen is re-run here with exact rational rank-product scores. A frozen anchor acts only as a witness
choosing among provably equal maximizing scores; every admissibility and strict-improvement condition is
recomputed from the actual word, and floating phi values are diagnostics only. Checks: crossed-interval contract of
every move, nested exact-integer frame chains, fixed initial/final frames, an integer replay modulo 2^61-1 with
pseudo-random dirty values for every register (identical final values to the input word), a nonvacuous omission
control, and the frozen local histogram delta. The F2 all-column, legality, chart, bank and price checks of the
package then run unchanged on the output word.
p10 width100 adaptation prepared with OpenAI Codex assistance.
Port of PR #299/#306's reorder stage (Chafik Boukhalfa, Anthropic Claude assistance) to the PR249 cohort word; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse,bisect,hashlib,json,math,random,shutil,struct
from collections import Counter,defaultdict
from pathlib import Path
from fractions import Fraction as Q
sha=lambda b:hashlib.sha256(b).hexdigest()
def phi(r):return r*math.log(100/r) if r>0 else 0.0

class Word:
    def __init__(s,cand):
        s.st=json.loads((cand/'249-states.json').read_text());fr=json.loads((cand/'frames.json').read_text())['frames']
        s.n=s.st['n'];s.v=s.st['v']
        s.dim={int(k):int(f['dim']) for k,f in fr.items()};s.B={int(k):f['B'] for k,f in fr.items()};s.A={int(k):f['A'] for k,f in fr.items()}
        s.init={int(k):x for k,x in json.loads((cand/'COHORT249-INITIAL.json').read_text()).items()}
        s.final={int(k):x for k,x in s.st['final'].items()};s.raw=(cand/'COHORT249-RECORDS.bin').read_bytes()
        s.ev=list(struct.iter_unpack('<6i',s.raw));s._sub={}
    def sub(s,a,b):
        k=(a,b)
        if k not in s._sub:s._sub[k]=s.dim[a]<=s.dim[b] and all(sum(x*y for x,y in zip(r,q))==0 for r in s.B[a] for q in s.A[b])
        return s._sub[k]

def hist(ev):
    H=Counter()
    for op,a,b,c,f,z in ev:
        if op==0 and f:H[f]+=1
        elif op==2:H[z]+=1
    return H
def phisum(H):return sum(c*phi(r) for r,c in H.items())
def strip(ev):return [e for e in ev if e[0]!=0]
def rebuild(W,events):
    n=W.n;state=[W.init[r] for r in range(n)]+[None];out=[]
    def mv(r,f):
        if state[r]!=f:
            assert W.sub(state[r],f),('non-nested MOVE',r,state[r],f)
            out.append((0,r,state[r],f,W.dim[f]-W.dim[state[r]],0));state[r]=f
    for e in events:
        op,a,b,c,f,z=e
        if op==1:mv(a,f);mv(b,f)
        elif op==2:mv(a,c);state[n]=f
        elif op==3:mv(a,c);assert state[n]==f
        else:raise AssertionError('MOVE in event stream')
        out.append(e)
    for r in range(n):mv(r,W.final[r])
    return out
def replay(ev,n,seed=20261010):
    P=(1<<61)-1;rng=random.Random(seed);val=[rng.randrange(P) for _ in range(n+1)]
    for op,a,b,c,f,z in ev:
        if op==1:val[a]=(val[a]+c*val[b])%P
        elif op==2:val[n]=val[a]
    return val[:n]

def index(W,ne):
    n=W.n;incf=defaultdict(list);reads=defaultdict(list);writes=defaultdict(list)
    for i,(op,a,b,c,f,z) in enumerate(ne):
        if op==1:
            incf[a].append((i,f,True));writes[a].append(i)
            if b!=n:incf[b].append((i,f,True));reads[b].append(i)
        else:incf[a].append((i,c,False));reads[a].append(i)
    return incf,reads,writes
def count(L,lo,hi):return bisect.bisect_left(L,hi)-bisect.bisect_left(L,lo)
def screen(W,ne,window=6,tie_preferences=None):
    tie_preferences={} if tie_preferences is None else {m['record']:m for m in tie_preferences}
    n=W.n;incf,reads,writes=index(W,ne);inct={s:[t for t,f,x in L] for s,L in incf.items()}
    # Along each role path, total rank is fixed by its endpoints. Thus
    # sum(r*log(m/r)) = fixed_rank*log(m) - log(product(r**r)).
    # Integer products compare the objective exactly and avoid Python-version
    # changes to float summation. The frozen witness only chooses exact ties.
    def cost(fs):return math.prod((W.dim[b]-W.dim[a])**(W.dim[b]-W.dim[a]) for a,b in zip(fs,fs[1:]) if a!=b)
    def legal(fs):return all(W.sub(a,b) for a,b in zip(fs,fs[1:]))
    def path(r,dele=None,add=None):
        L=[(t,f) for t,f,x in incf[r] if t!=dele]+([add] if add else []);L.sort()
        return [W.init[r]]+[f for t,f in L]+[W.final[r]]
    cands=[]
    for i,(op,a,b,c,f,z) in enumerate(ne):
        if op!=1 or b==n:continue
        def bp(r):
            L=inct[r];k=bisect.bisect_left(L,i);pf=incf[r][k-1][1] if k else W.init[r];nf=incf[r][k+1][1] if k+1<len(L) else W.final[r]
            return pf!=f and nf!=f
        if not(bp(a) or bp(b)):continue
        base=cost(path(a))*cost(path(b));best=None
        for r in (a,b):
            L=inct[r];k=bisect.bisect_left(L,i)
            for j in range(1,window+1):
                for kk,side in ((k+j,'before'),(k-j,'after')):
                    if not(0<=kk<len(L)) or not incf[r][kk][2]:continue
                    T,F,_=incf[r][kk];lo,hi=(i+1,T) if side=='before' else (T+1,i)
                    if count(reads[a],lo,hi) or count(writes[b],lo,hi):continue
                    pos=T+(-.5 if side=='before' else .5);pa=path(a,i,(pos,F));pb=path(b,i,(pos,F))
                    if not(legal(pa) and legal(pb)):continue
                    score=Q(cost(pa)*cost(pb),base)
                    pref=tie_preferences.get(i,{})
                    tie=(int((T,side,F)!=(pref.get('anchor'),pref.get('side'),pref.get('frame'))),T,side,F)
                    if score>1 and (best is None or (-score,tie)<(-best[0],best[4])):best=(score,T,side,F,tie)
        if best:cands.append((best[0],i,best[1],best[2],best[3]))
    cands.sort(key=lambda x:(-x[0],x[1]));used=set();keep=[]
    for d,i,T,side,F in cands:
        a,b=ne[i][1],ne[i][2]
        if {a,b}&used:continue
        used|={a,b};keep.append(dict(record=i,anchor=T,side=side,frame=F,incidence=[a,b,ne[i][3]],phi=round(-math.log(float(d)),9)))
    return keep
def contract(W,ne,moves):
    """Independent check of each frozen move against the actual event stream."""
    n=W.n;incf,reads,writes=index(W,ne);used=set()
    for m in moves:
        i,T,side,F=m['record'],m['anchor'],m['side'],m['frame'];op,a,b,c,f,z=ne[i]
        assert op==1 and b!=n and [a,b,c]==m['incidence'] and not({a,b}&used);used|={a,b}
        assert ne[T][0]==1 and ne[T][4]==F and (a in ne[T][1:3] or b in ne[T][1:3]),'anchor is an ADD incidence in frame F'
        lo,hi=(i+1,T) if side=='before' else (T+1,i);assert lo<=hi
        for t in range(lo,hi):
            o,x,y=ne[t][0],ne[t][1],ne[t][2]
            assert not((o==1 and y==a) or (o in (2,3) and x==a)),'crossed read of target'
            assert not(o==1 and x==b),'crossed write of source'
def apply(ne,moves):
    mv={m['record']:m for m in moves};before=defaultdict(list);after=defaultdict(list)
    for i,m in mv.items():
        op,a,b,c,f,z=ne[i];(before if m['side']=='before' else after)[m['anchor']].append((op,a,b,c,m['frame'],z))
    out=[]
    for t,e in enumerate(ne):
        out+=before.get(t,[])
        if t not in mv:out.append(e)
        out+=after.get(t,[])
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--binding',type=Path);a=ap.parse_args()
    src=a.input.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);sel=json.loads(a.selection.read_text())
    W=Word(src);n=W.n;assert sha(W.raw)==sel['input_word_sha256']
    ne=strip(W.ev);base=replay(W.ev,n);H0=hist(W.ev)
    word=rebuild(W,ne);assert replay(word,n)==base;Hn=hist(word)
    rounds=[]
    for frozen in sel['rounds']:
        ne=strip(word);keep=screen(W,ne,sel['window'],tie_preferences=frozen)
        structural=lambda rows:[{k:v for k,v in row.items() if k!='phi'}for row in rows]
        assert structural(keep)==structural(frozen),'exact screen does not reproduce the frozen round'
        contract(W,ne,frozen);new=rebuild(W,apply(ne,frozen))
        assert replay(new,n)==base,'relocated word changes a final register value'
        assert sum(1 for e in new if e[0]==1)==sum(1 for e in word if e[0]==1)
        rounds.append({'moves':len(frozen),'phi':phisum(hist(new))-phisum(hist(word))});word=new
    assert screen(W,strip(word),sel['window'])==[],'selection is not a fixed point'
    # omission control: dropping the first relocated ADD must change the replay
    first=sel['rounds'][0][0];ne0=strip(rebuild(W,strip(W.ev)));e=ne0[first['record']]
    assert replay([x for x in ne0 if x is not e],n)!=base,'vacuous omission control'
    H=hist(word);d=Counter(H);d.subtract(H0);delta={str(r):c for r,c in sorted(d.items()) if c}
    assert delta==sel['expected_local_delta'] and sum(int(r)*c for r,c in delta.items())==0,'rank mass or delta'
    raw=b''.join(struct.pack('<6i',*e) for e in word);assert sha(raw)==sel['output_word_sha256']
    for p in src.iterdir():
        if p.is_file():shutil.copyfile(p,out/p.name)
    (out/'COHORT249-RECORDS.bin').write_bytes(raw);(out/'249-records.bin').write_bytes(raw)
    bind=json.loads(a.binding.read_text()) if a.binding else dict(freed_roles=[],source_word_sha256=sha(W.raw));freed=set(bind['freed_roles'])
    live=[r for r in range(n) if r not in freed];mp={r:i for i,r in enumerate(live)};mp[n]=len(live)
    compact=b''.join(struct.pack('<6i',op,mp[x],y if op==0 else mp[y],c,f,z) for op,x,y,c,f,z in word)
    for op,x,y,c,f,z in word:assert x not in freed and (op==0 or y not in freed)
    (out/'COMPACT-RECORDS.bin').write_bytes(compact)
    st=json.loads((src/'249-states.json').read_text());st['record_sha256']=sha(raw);st['record_count']=len(word)
    (out/'249-states.json').write_text(json.dumps(st,sort_keys=True,indent=2)+'\n')
    bind.update(word_sha256=sha(raw),compact_word_sha256=sha(compact),pre_reorder_word_sha256=sha(W.raw))
    (out/'SOURCE-BINDING.json').write_text(json.dumps(bind,sort_keys=True,indent=2)+'\n')
    receipt={'status':'PASS_REORDER_STAGE_REDERIVED_COMMUTING_RELOCATIONS','input_word_sha256':sha(W.raw),'output_word_sha256':sha(raw),
      'compact_word_sha256':sha(compact),'normalisation_phi':phisum(Hn)-phisum(H0),'rounds':rounds,'relocated_adds':sum(len(r) for r in sel['rounds']),
      'local_delta':delta,'local_phi_delta':phisum(H)-phisum(H0),'exact_rank_product_screen':True,'tie_rule':'frozen anchors resolve only exact maximizing rank-product ties; all admissibility and strict improvement recomputed','integer_replay_identical':True,'omission_control_rejected':True,'fixed_point':True}
    (out/'REORDER-STAGE.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print('PASS reorder stage',receipt['relocated_adds'],'relocations, local phi',round(receipt['local_phi_delta'],6),flush=True)
if __name__=='__main__':main()
