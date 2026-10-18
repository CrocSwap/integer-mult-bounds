"""Separate set-valued semantic replay and literal chronological pricing.
No search imports. Apache-2.0; OpenAI Codex assistance for @woklerx.
"""
from collections import Counter
import copy


def need(ok,msg):
    if not ok:raise ValueError(msg)


def make(parent,d,s):
    # Build from literal target rows, without packed columns or search helpers.
    out=copy.deepcopy(parent);middle=out['D'][527:638]
    for frame,target,donors in middle:
        if 222+d in donors:
            if 222+s in donors:donors.remove(222+s)
            else:donors.append(222+s)
        donors.sort()
    edge=[0,222+d,[222+s]]
    out['D']=out['D'][:527]+[edge]+middle+[copy.deepcopy(edge)]+out['D'][638:]
    return out


def support_census(parent):
    columns=[set()for _ in range(439)]
    for i,(_,t,ss)in enumerate(parent['D'][527:638]):
        for s in ss:columns[s-222].add(i)
    # Explicit undirected components, not union-find parent labels.
    adjacency=[set()for _ in range(439)]
    for _,d,ss in parent['D'][:221]:
        s=ss[0]-222;d-=222;adjacency[d].add(s);adjacency[s].add(d)
    groups=[];visited=set()
    for start in range(439):
        if start in visited:continue
        group={start};queue=[start]
        for x in queue:
            for y in adjacency[x]:
                if y not in group:group.add(y);queue.append(y)
        groups.append(group);visited|=group
    owner={r:i for i,g in enumerate(groups)for r in g}
    hist=Counter();maximizers=[];best=-10**9
    for s in range(439):
        for d in range(439):
            if d==s or owner[d]==owner[s]:continue
            gain=len(columns[s])-len(columns[s].symmetric_difference(columns[d]))-2
            hist[str(gain)]+=1
            if gain>best:best=gain;maximizers=[]
            if gain==best:maximizers.append([d,s])
    return dict(hist),{'maximum_net_saving':best,'maximizers':sorted(maximizers),
           'components':[sorted(g)for g in groups]}


def events(word):
    out=[]
    def phase(name):
        for f,d,ss in word[name]:
            need(type(f)is int and type(d)is int and isinstance(ss,list),'gate shape')
            need(len(set([d]+ss))==1+len(ss),'aliased ADD operands')
            out.extend(('xor',d,s)for s in ss)
    phase('D');phase('A')
    for j,r in enumerate(word['ret']):
        out.append(('load',661,r))
        for t,indices in enumerate(word['scatter']):
            if j in indices:out.append(('xor',111+t,661))
        out.append(('unload',661,r))
    phase('B');phase('C')
    return out


def check_full(word,reverse=False):
    seq=events(word)
    if reverse:seq=[({'load':'unload','unload':'load'}.get(tag,tag),d,s)for tag,d,s in reversed(seq)]
    values=[{r}for r in range(661)]+[set()];magnitudes=[1]*662;peak=1;adds=0
    for tag,d,s in seq:
        if tag=='xor':
            values[d]=values[d].symmetric_difference(values[s]);magnitudes[d]+=magnitudes[s];adds+=1
        elif tag=='load':
            need(not values[d],'dirty private COPY destination');values[d]=set(values[s]);magnitudes[d]=magnitudes[s]
        else:
            need(values[d]==values[s],'ERASE source no longer matches');values[d]=set();magnitudes[d]=0
        peak=max(peak,magnitudes[d])
    expected=[{r,r-111}if 111<=r<222 else{r}for r in range(661)]+[set()]
    need(values==expected,'complete arbitrary dirty-input boundary')
    return peak,adds


def d_rows(word):
    rows=[{i}for i in range(661)]
    for f,d,ss in word['D']:
        need(f==0 and 111<=d<661 and all(111<=s<661 and s!=d for s in ss),'D legality')
        for s in ss:rows[d]=rows[d].symmetric_difference(rows[s])
    return rows


def paid_profile(word,dimensions):
    frames=list(word['start']);hist=Counter();paths=[[f]for f in frames]
    def move(r,f):
        if frames[r]!=f:
            delta=dimensions[f]-dimensions[frames[r]];need(delta>0,'nonpositive climb')
            hist[delta]+=1;frames[r]=f;paths[r].append(f)
    for section in ('D','A','scatter','B','C'):
        if section=='scatter':
            for r in word['ret']:hist[dimensions[frames[r]]]+=1
        else:
            for f,d,ss in word[section]:
                for r in [d]+ss:move(r,f)
    for r,f in enumerate(word['final']):move(r,f)
    return {str(k):v for k,v in sorted(hist.items())},paths
