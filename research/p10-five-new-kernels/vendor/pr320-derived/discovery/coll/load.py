import sys, json, struct, collections, pickle
D = sys.argv[1]; OUT = sys.argv[2]
meta = json.load(open(D+'/meta.json')); frames = json.load(open(D+'/frames.json')); init = {int(k):v for k,v in json.load(open(D+'/initial.json')).items()}
n, v, ZERO, FULL = meta['n'], meta['v'], meta['ZERO'], meta['FULL']
cats = meta['category_names']; readcat = cats.index('dirty_read')
ev = list(struct.iter_unpack('<6i', open(D+'/records.bin','rb').read()))
gauge = {int(k) for k in meta['gauge']}
helpers = [s for s in range(2*v, n) if init[s]==ZERO and s not in gauge]
H = set(helpers)
reads = collections.defaultdict(list); touch = {}; firstframe = {}
for i,e in enumerate(ev):
    op,a,b,c,f,z = e
    if op==1:
        if z==readcat and b in H and f==ZERO and v<=a<2*v and c%2:
            reads[b].append((i,a)); continue
        for s in (a,b):
            if s in H and s not in touch: touch[s]=i; firstframe[s]=f
    elif op==2:
        if a in H and a not in touch: touch[a]=i; firstframe[a]=c
resp = {}; lastread = {}
for s in helpers:
    cnt = collections.Counter(a for i,a in reads[s])
    resp[s] = sum(1<<(a-v) for a,c in cnt.items() if c%2)
    lastread[s] = reads[s][-1][0]
    assert lastread[s] < touch[s]
ff = set(firstframe.values())
ftab = {f: dict(B=frames[str(f)]['B'], A=frames[str(f)]['A'], dim=frames[str(f)]['dim']) for f in ff}
print('helpers', len(helpers), 'distinct first frames', len(ff), 'dim hist of distinct first frames', sorted(collections.Counter(x['dim'] for x in ftab.values()).items()))
print('helpers per first frame: hist', sorted(collections.Counter(collections.Counter(firstframe.values()).values()).items())[:30])
pickle.dump(dict(n=n,v=v,ZERO=ZERO,FULL=FULL,readcat=readcat,helpers=helpers,resp=resp,lastread=lastread,touch=touch,firstframe=firstframe,ftab=ftab,nreads={s:len(reads[s]) for s in helpers}), open(OUT,'wb'))
