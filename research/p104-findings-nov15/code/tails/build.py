from lib import *
from chart_fn import clean,okpath,newpath
import copy
def apply(W,M,moves):
    """moves: list of (event idx i, F'). Returns new word. Moves must touch disjoint stays."""
    paths={}
    for i,F in moves:
        for (r,k) in M.opnode[i]:
            p=newpath(M,r,k,i,F) if r not in paths else None
            assert p is not None,(i,r)
            paths[r]=p
    prog=W['program']; drop=set(); ins=collections.defaultdict(list)
    for r,out in paths.items():
        nd=M.nodes[r]
        for x in nd:
            if x['mv'] is not None: drop.add(x['mv'])
        # map chart-node -> first op position: walk original nodes, charts out; assign hops
        # first op position per original stay in order; new nodes inherit via chart sequence + op ordering
        evs=sorted(i for x in nd for i in x['ops'])
        # recompute which chart each op sits at in the new path: ops in M.opnode order; ops belong to node (old); new chart for op = F if op in moves else old node chart
        newc={}
        for x in nd:
            for i in x['ops']: newc[i]=x['c']
        for i,F in moves:
            if any(rr==r for rr,_ in M.opnode[i]): newc[i]=F
        # path positions: place hop into chart c' before first op at chart c' (in program order) if c' has ops else at end
        seq=[newc[i] for i in evs]
        first={}
        for i,c in zip(evs,seq): first.setdefault(c,i)
        # consistency: seq must follow out ordering
        comp=clean([out[0]]+seq+[out[-1]])
        assert comp==out,(r,comp,out)
        for a,b in zip(out,out[1:]):
            pos=first.get(b)
            if pos is None: pos=len(prog)
            ins[pos].append(['MOVE',r,a,b,False])
    newprog=[]
    mv={}
    for i,e in enumerate(prog):
        for m in ins.get(i,[]): newprog.append(m)
        if i in drop: continue
        e=list(e)
        newprog.append(e)
    for m in ins.get(len(prog),[]): newprog.append(m)
    for i,F in moves:
        pass
    # rewrite ADD/SCALE chart tags
    idx_new=[j for j,e in enumerate(newprog) if e[0]!='MOVE']
    old_nm=[i for i,e in enumerate(prog) if e[0]!='MOVE']
    assert len(idx_new)==len(old_nm)
    for i,F in moves:
        j=idx_new[old_nm.index(i)] if False else None
    pos_map=dict(zip(old_nm,idx_new))
    for i,F in moves:
        e=newprog[pos_map[i]]
        e[4]=F
    W2=dict(W); W2['program']=newprog; return W2
if __name__=='__main__':
    import sys
    W=load('../BASE7612/w7612.json.gz'); M=Model(W)
    mv=[(int(sys.argv[1]),int(sys.argv[2]))]
    W2=apply(W,M,mv)
    json.dump(W2,gzip.open(sys.argv[3],'wt'))
    print(len(W['program']),len(W2['program']))
