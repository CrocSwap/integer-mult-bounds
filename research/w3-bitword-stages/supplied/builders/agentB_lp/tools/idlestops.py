# Find register stops (frames) with no ADD activity; estimate saving if skipped.
import sys, json, numpy as np, math, collections
g=lambda r: r*math.log(120/r) if r>0 else 0.0
d=sys.argv[1]
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
s=json.load(open(d+'/249-states.json')); v=s['v']; n=s['n']
dim={}
with open(d+'/frames.txt') as f:
    nf=int(f.readline())
    for _ in range(nf):
        fid,dd=map(int,f.readline().split()); dim[fid]=dd
        for __ in range(dd): f.readline()
# per register: list of (k, frame) stays and count of adds during each stay
act=collections.defaultdict(list)
cur={r:s['initial'][str(r)] for r in range(n)}
stay_adds=collections.defaultdict(lambda: collections.Counter())
moves=collections.defaultdict(list)
for k in range(len(rec)):
    o,a,b,c,f,z=[int(x) for x in rec[k]]
    if o==0: moves[a].append((k,b,c))
    elif o==1:
        stay_adds[a][(f,len(moves[a]))]+=1
        if b!=a: stay_adds[b][(f,len(moves[b]))]+=1
tot=0; cnt=collections.Counter()
for r,mv in moves.items():
    # stays: index i (after i moves) at frame mv[i-1][2]
    for i in range(1,len(mv)):
        fr=mv[i-1][2]
        if dim[fr] in (0,24): continue
        if stay_adds[r][(fr,i)]==0:
            # idle intermediate stop between mv[i-1] (from a) and mv[i] (to b)
            a_=dim[mv[i-1][1]]; b_=dim[mv[i][2]]; m_=dim[fr]
            sav=g(m_-a_)+g(b_-m_)-g(b_-a_)
            tot+=sav; cnt['Y' if v<=r<2*v else ('X' if r<v else 'H')]+=1
print('idle stops',dict(cnt),'saving if skipped %.1f'%tot)
