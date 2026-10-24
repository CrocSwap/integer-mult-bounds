"""Screen every one-edge paid phase defect with exact rollback equalities.

All singleton/pair equations other than one physical edge are imposed. Longer
equations are initially omitted, an optimistic necessary relaxation. Any edge
that could change a helper phase must survive this screen; survivors need the
full system and exact rank/phase/moment checks.
"""
from pathlib import Path
from hashlib import sha256
import gzip,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import owned_phase_probe as P

class Rollback:
    def __init__(self,n):self.parent=list(range(n+1));self.size=[1]*(n+1);self.history=[];self.unions=0
    def root(self,x):
        while self.parent[x]!=x:x=self.parent[x]
        return x
    def union(self,a,b):
        a,b=self.root(a),self.root(b)
        if a==b:return
        if self.size[a]<self.size[b]:a,b=b,a
        self.history.append((b,a));self.parent[b]=a;self.size[a]+=self.size[b];self.unions+=1
    def rollback(self,checkpoint):
        while len(self.history)>checkpoint:
            b,a=self.history.pop();self.parent[b]=b;self.size[a]-=self.size[b]
    def reduced(self,row):
        zero=self.root(0);out=set()
        for x in row:
            r=self.root(x)
            if r!=zero:out.symmetric_difference_update((r,))
        return out

def main():
    began=time.monotonic();M=P.load()
    raw=(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()
    assert sha256(gzip.decompress(raw)).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
    payload=json.loads(gzip.decompress(raw));original,relaxed=P.relaxed_graph(M,payload)
    frames,nodes,fixed,edges,helpers=relaxed;forms=M.Forms(frames,nodes,fixed)
    groups=[];longer=0;total=0
    for e,(kind,a,b,old,image) in enumerate(edges):
        pairs=[]
        for i,x in enumerate(old):
            for j in range(i,len(old)):
                row=sorted(set(forms.at(a,x,old[j]))^set(forms.at(b,image[i],image[j])))
                if not row:continue
                total+=1
                if len(row)==1:pairs.append((0,row[0]))
                elif len(row)==2:pairs.append(tuple(row))
                else:longer+=1
        if pairs:groups.append((e,pairs))
    queries=[]
    for r,a,b,basis in helpers:
        for i,x in enumerate(basis):
            for y in basis[i:]:
                row=sorted(set(forms.at(a,x,y))^set(forms.at(b,x,y)))
                if row:queries.append((r,row))
    ds=Rollback(forms.count);survivors=[];leaves=0
    def add(lo,hi):
        for _,pairs in groups[lo:hi]:
            for a,b in pairs:ds.union(a,b)
    def visit(lo,hi):
        nonlocal leaves
        if hi-lo==1:
            possible=sorted({r for r,row in queries if ds.reduced(row)})
            if possible:
                e=groups[lo][0];kind,a,b,old,image=edges[e]
                survivors.append(dict(edge=e,kind=kind,source=a,target=b,possible_helper_roles=possible,
                    old_rank=len(frames[nodes[b]])-len(frames[nodes[a]]) if kind=='paid' else 0))
            leaves+=1
            return
        mid=(lo+hi)//2;checkpoint=len(ds.history)
        add(mid,hi);visit(lo,mid);ds.rollback(checkpoint)
        add(lo,mid);visit(mid,hi);ds.rollback(checkpoint)
    print('SCREEN',len(groups),'edge_groups',total,'equations',longer,'higher_arity_omitted',flush=True)
    visit(0,len(groups))
    result=dict(status='EXACT_ONE_PHYSICAL_PHASE_DEFECT_NECESSARY_SCREEN',script_sha256=P.digest(__file__),
        graph_probe_sha256=P.digest(HERE/'owned_phase_probe.py'),sources_sha256=P.digest(HERE/'SOURCES.json'),
        native_word_sha256=sha256(raw).hexdigest(),form_coordinates=forms.count,physical_edges=len(edges),
        screened_nontrivial_edge_groups=len(groups),equations=total,omitted_higher_arity=longer,
        helper_coefficient_queries=len(queries),screen_leaves=leaves,rollback_successful_unions=ds.unions,
        survivors=survivors,seconds=time.monotonic()-began,
        scope='Necessary optimistic screen only: exact singleton/pair constraints, all owned contact gauges relaxed, at most one physical paid/warp edge allowed any phase defect. Surviving edges are not feasible constructions. Original scalar order/subspaces/maps and main/adapter boundaries stay fixed. No paid-rank, native admission, controller, or kappa claim.')
    (HERE/'ONE-DEFECT-SCREEN.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('SURVIVORS',len(survivors),'seconds',result['seconds'])

if __name__=='__main__':main()
