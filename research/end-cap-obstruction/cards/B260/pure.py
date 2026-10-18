import sys,collections,pickle
sys.path.insert(0,'../B256')
from lib import *
w=load(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz');P=w['ports']
keep=pickle.load(open('merge.pkl','rb'))
seq=w['A']+w['B']
writes=collections.defaultdict(list); oreads=collections.defaultdict(list)
for k,e in enumerate(seq):
    if e[0]=='add':
        writes[e[1]].append(k)
        if not (V<=e[1]<2*V): oreads[e[2]].append(k)
    else: writes[e[1]].append(k)
st=collections.Counter()
for k,h,s,T,a,late,val,nx in keep:
    pure=not any(kk>k for kk in writes[h])
    hreads=[kk for kk,e in enumerate(seq) if e[0]=='add' and e[2]==h and kk>k]
    last=max(hreads)
    version=any(k<kk<last for kk in writes[s])
    drag=any(k<kk<last for kk in oreads[s])
    st[(pure,version,drag,late)]+=1
print('(pure copy, s written before copy last read=version, s read by non-target before=drag, late-anc ok):')
for x in sorted(st.items()): print(' ',x)
