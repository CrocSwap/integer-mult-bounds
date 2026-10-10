"""Kernel-eligible helper census on a dumped word (dump_at.py): ZERO->FULL ungauged helpers, F2 response, last initial read, first touch and first frame. Usage: census.py DUMP OUT.pkl
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import sys,json,struct,collections,pickle,math
D=sys.argv[1]
meta=json.load(open(D+'/meta.json'));frames=json.load(open(D+'/frames.json'))
init={int(k):v for k,v in json.load(open(D+'/initial.json')).items()};final={int(k):v for k,v in json.load(open(D+'/final.json')).items()}
n,v,ZERO,FULL=meta['n'],meta['v'],meta['ZERO'],meta['FULL'];cats=meta['category_names'];readcat=cats.index('dirty_read')
ev=list(struct.iter_unpack('<6i',open(D+'/records.bin','rb').read()))
bad=set(int(k) for k in meta['gauge'])|set(meta['donor_streams'])|set(meta['borrow_streams'])
cand=[s for s in range(2*v,n) if s not in bad and init[s]==ZERO and final[s]==FULL]
C=set(cand);reads=collections.defaultdict(list);touch={};ff={}
for i,(op,a,b,c,f,z) in enumerate(ev):
    if op==1:
        if b in C and z==readcat and f==ZERO and v<=a<2*v and c%2: reads[b].append((i,a));continue
        for s in (a,b):
            if s in C and s not in touch: touch[s]=i;ff[s]=f
    elif op==2:
        if a in C and a not in touch: touch[a]=i;ff[a]=c
hel=[s for s in cand if reads[s]]
print('eligible (ZERO->FULL, ungauged)',len(cand),'with reads',len(hel),'no reads',len(cand)-len(hel))
resp={};lastread={}
for s in hel:
    cnt=collections.Counter(a for i,a in reads[s]);resp[s]=sum(1<<(a-v) for a,c in cnt.items() if c%2);lastread[s]=reads[s][-1][0]
print('lastread<touch for all', all(lastread[s]<touch[s] for s in hel))
print('max lastread',max(lastread.values()),'min touch',min(touch[s] for s in hel))
print('first-frame dims', sorted(collections.Counter(frames[str(ff[s])]['dim'] for s in hel).items()))
print('zero response', sum(1 for s in hel if resp[s]==0))
cats_touch=collections.Counter(cats[ev[touch[s]][5]] if ev[touch[s]][0]==1 else 'copy' for s in hel);print('first touch categories',cats_touch.most_common(10))
pickle.dump(dict(n=n,v=v,ZERO=ZERO,FULL=FULL,helpers=hel,resp=resp,lastread=lastread,touch=touch,firstframe=ff,ftab={f:frames[str(f)] for f in set(ff.values())},nreads={s:len(reads[s]) for s in hel}),open(sys.argv[2],'wb'))
