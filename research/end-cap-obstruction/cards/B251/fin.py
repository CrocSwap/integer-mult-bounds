import sys,pickle,collections
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from feas import *
inc=pickle.load(open('inc.pkl','rb'));host=pickle.load(open('host.pkl','rb'));Yev=pickle.load(open('yevp.pkl','rb'))
def lay(h):
    return ('cold0' if len(start[h])==0 else 'enter%d'%len(start[h]))+('/endFULL' if end[h]==FULLB else '/endU')
H=[h for h in range(224,704) if h not in set(w['centers'])]
act=collections.Counter(lay(h) for h in H)
carr_real=collections.defaultdict(set);carr_gauge=collections.defaultdict(set)
for i in inc:
    for c in i['car']:
        if c>=224:carr_real[lay(c)].add(c)
for idx,tag,e,k,hh in Yev:
    if k==() and e[2]>=224:carr_gauge[lay(e[2])].add(e[2])
forced=collections.Counter()
for i,x in enumerate(inc):
    if x['nh']==0 and len(host[i])==1:forced[next(iter(host[i]))]+=1
print('class | actual | delivery-carriers(real value) | gauge-only carriers | no Y-read at all | forced-incarnations')
for L in sorted(act):
    d=carr_real[L];g=carr_gauge[L]-d
    print(L,act[L],len(d),len(g),act[L]-len(d|carr_gauge[L]),forced[L])
