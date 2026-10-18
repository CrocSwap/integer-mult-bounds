import sys,json,gzip,hashlib,difflib
def load(p):
    raw=gzip.decompress(open(p,'rb').read());return json.loads(raw),hashlib.sha256(raw).hexdigest()
a,sa=load(sys.argv[1]);b,sb=load(sys.argv[2])
A=[json.dumps(g[:-1]) for g in a['B']];Bb=[json.dumps(g[:-1]) for g in b['B']]
sm=difflib.SequenceMatcher(None,A,Bb,autojunk=False)
dele=[];ins=[];fr={}
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal':
        for k in range(i2-i1):
            if a['B'][i1+k][-1]!=b['B'][j1+k][-1]: fr[str(i1+k)]=b['B'][j1+k][-1]
    else:
        dele+=list(range(i1,i2))
        ins+=[[i1,b['B'][j]] for j in range(j1,j2)]
na=len(a['cleanup']);nb=len(b['cleanup'])
# cleanup: prepend k gates, append tails
k=nb-na-(len(b['early_cleanup'])-len(a['early_cleanup']))
pre=b['cleanup'][:k]
assert b['cleanup'][k:k+na]==a['cleanup']
tails_gates=b['cleanup'][k+na:]
emap={ci:j for j,(ci,U) in enumerate(b['early_cleanup'])}
tails=[[emap[k+na+t],g[:-1]+[b['early_cleanup'][emap[k+na+t]][1]]] for t,g in enumerate(tails_gates)]
rc=dict(base_sha256=sa,B_delete=dele,B_insert=ins,B_frames=fr,tail_insert=tails,cleanup_prepend=pre,
        local_profile=b['report']['local_profile'],expect_sha256=sb)
json.dump(rc,open(sys.argv[3],'w'),indent=1)
print(len(dele),len(ins),len(fr),len(tails),len(pre))
