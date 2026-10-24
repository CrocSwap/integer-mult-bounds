"""Proof-dependency reduction and exact one-physical-edge phase defects."""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import argparse,gzip,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import owned_phase_probe as P

class ProofEqualities:
    def __init__(self,n):
        self.parent=list(range(n+1));self.proof={};self.pending=[];self.merges=0
    def trace(self,x):
        links=[]
        while self.parent[x]!=x:links.append(x);x=self.parent[x]
        return x,links
    def equation(self,group,row):
        out=set();deps=set()
        for x in row:
            r,links=self.trace(x);deps.update(links)
            if r:out.symmetric_difference_update((r,))
        r=sorted(out)
        if len(r) in [1,2]:
            a,b=(0,r[0]) if len(r)==1 else r
            self.parent[b]=a;self.proof[b]=(group,tuple(deps));self.merges+=1
        elif r:self.pending.append((group,row))
    def finish(self):
        while self.pending:
            before=self.merges;rows,self.pending=self.pending,[]
            for group,row in rows:self.equation(group,row)
            if self.merges==before:break
    def dependencies(self,row):
        out=set();todo=[];seen=set();parity=set()
        for x in row:
            root,links=self.trace(x);todo.extend(links)
            if root:parity.symmetric_difference_update((root,))
        assert not parity
        while todo:
            x=todo.pop()
            if x in seen:continue
            seen.add(x);group,links=self.proof[x];out.add(group);todo.extend(links)
        return out

def gaussian(rows):
    basis={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p not in basis:basis[p]=x;break
            x^=basis[p]
    return basis
def reduce(x,basis):
    while x:
        p=x.bit_length()-1
        if p not in basis:return x
        x^=basis[p]
    return 0

def rank(rows):return len(gaussian(rows))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    began=time.monotonic();M=P.load()
    raw=(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()
    assert sha256(gzip.decompress(raw)).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
    payload=json.loads(gzip.decompress(raw));original,relaxed=P.relaxed_graph(M,payload)
    frames,nodes,fixed,edges,helpers=relaxed;forms=M.Forms(frames,nodes,fixed)
    grouped=[];allrows=[]
    for e,(kind,a,b,old,image) in enumerate(edges):
        rows=[]
        for i,x in enumerate(old):
            for j in range(i,len(old)):
                row=tuple(sorted(set(forms.at(a,x,old[j]))^set(forms.at(b,image[i],image[j]))))
                if row:rows.append(row);allrows.append((e,row))
        grouped.append(rows)
    queries=[]
    for r,a,b,basis in helpers:
        for i,x in enumerate(basis):
            for y in basis[i:]:
                row=tuple(sorted(set(forms.at(a,x,y))^set(forms.at(b,x,y))))
                if row:queries.append((r,row))
    proof=ProofEqualities(forms.count)
    for e,row in allrows:proof.equation(e,row)
    proof.finish();assert not proof.pending
    candidates=set();dependencies=[]
    for r,row in queries:
        deps=proof.dependencies(row);candidates.update(deps);dependencies.append((r,row,deps))
    print('PROOF_REDUCED_CANDIDATES',len(candidates),'of',len(edges),'edges',flush=True)
    results=[];witnesses=[]
    def existing_rank(e):
        kind,a,b,_,_=edges[e]
        return len(frames[nodes[b]])-len(frames[nodes[a]]) if kind=='paid' else 0
    ordered=sorted(candidates,key=lambda e:(-existing_rank(e),e))
    for step,excluded in enumerate(ordered):
        if args.limit is not None and step>=args.limit:break
        eq=M.Equalities(forms.count)
        for e,row in allrows:
            if e!=excluded:eq.equation(row)
        eq.finish()
        qrows=[(r,eq.simplify(row)) for r,row,deps in dependencies if excluded in deps]
        roots=sorted({x for row in eq.pending for x in eq.simplify(row)}|{x for _,row in qrows for x in row}|
            {x for row in grouped[excluded] for x in eq.simplify(row)})
        pos={x:i for i,x in enumerate(roots)}
        bits=lambda row:sum(1<<pos[x] for x in row)
        basis=gaussian(bits(eq.simplify(row)) for row in eq.pending)
        useful=[(r,row) for r,row in qrows if reduce(bits(row),basis)]
        result=dict(edge=excluded,residual_classes=len(roots),residual_equations=len(eq.pending),
            useful_helper_roles=sorted({r for r,_ in useful}))
        if useful:
            # Reconstruct the exact relevant kernel. Enumerate every rank-one
            # defect matrix (not a single fixed ambient form) in its image.
            kernel=[]
            for free in range(len(roots)):
                if free in basis:continue
                solution=1<<free
                for pivot,row in sorted(basis.items()):
                    if (row&solution).bit_count()%2:solution|=1<<pivot
                kernel.append(solution)
            relevant_bits=lambda row:sum(1<<pos[x] for x in eq.simplify(row) if x in pos)
            kind,edge_a,edge_b,old,image=edges[excluded]
            defect_functionals=[relevant_bits(set(forms.at(edge_a,x,old[j]))^
                set(forms.at(edge_b,image[i],image[j]))) for i,x in enumerate(old) for j in range(i,len(old))]
            defect_mask=lambda s:sum(((row&s).bit_count()%2)<<i for i,row in enumerate(defect_functionals))
            image_basis={}
            for solution in kernel:
                dmask=defect_mask(solution);s=solution
                while dmask:
                    pivot=dmask.bit_length()-1
                    if pivot not in image_basis:image_basis[pivot]=(dmask,s);break
                    d,s0=image_basis[pivot];dmask^=d;s^=s0
            helper_forms=[]
            for r,a,b,U in helpers:
                helper_forms.append((r,len(frames[nodes[b]])-len(frames[nodes[a]]),[
                    [relevant_bits(set(forms.at(a,x,y))^set(forms.at(b,x,y))) for y in U] for x in U]))
            def gain_list(solution):
                out=[]
                for r,g,rows in helper_forms:
                    d=rank([sum(((v&solution).bit_count()%2)<<j for j,v in enumerate(row)) for row in rows])
                    if d:out.append(dict(role=r,old_rank=g,added_rank=d))
                return out
            trials=[s for s in kernel if any((bits(row)&s).bit_count()%2 for _,row in useful)]
            rank_one_count=0
            for l in range(1,1<<len(old)):
                target=sum((((l>>i)&1)*((l>>j)&1))<<k for k,(i,j) in enumerate(
                    (i,j) for i in range(len(old)) for j in range(i,len(old))))
                sol=0
                while target:
                    p=target.bit_length()-1
                    if p not in image_basis:break
                    d,s=image_basis[p];target^=d;sol^=s
                if not target:rank_one_count+=1;trials.append(sol)
            assert trials
            def discovery_score(solution):
                dmask=defect_mask(solution);matrix=[[0]*len(old) for _ in old];k=0
                for i in range(len(old)):
                    for j in range(i,len(old)):
                        matrix[i][j]=matrix[j][i]=(dmask>>k)&1;k+=1
                d=rank([sum(v<<j for j,v in enumerate(row)) for row in matrix]);r=existing_rank(excluded)
                t=1-.00302177581
                return sum((g['old_rank']+g['added_rank'])**t-g['old_rank']**t for g in gain_list(solution))-((r+d)**t-r**t)
            solution=max(trials,key=discovery_score)
            result.update(relevant_phase_space_dimension=len(kernel),rank_one_defect_matrices_tested=rank_one_count,
                floating_discovery_surplus=discovery_score(solution))
            active={roots[i] for i in range(len(roots)) if solution>>i&1}
            val=lambda row:sum(eq.root(x) in active for x in row)%2
            assert all(val(row)==0 for e,row in allrows if e!=excluded)
            kind,a,b,old,image=edges[excluded]
            defect=[]
            for i,x in enumerate(old):
                row=0
                for j,y in enumerate(old):
                    if val(set(forms.at(a,x,y))^set(forms.at(b,image[i],image[j]))):row|=1<<j
                defect.append(row)
            added=rank(defect);assert added>0
            gains=[]
            for r,a,b,U in helpers:
                D=[]
                for x in U:
                    D.append(sum(val(set(forms.at(a,x,y))^set(forms.at(b,x,y)))<<j for j,y in enumerate(U)))
                d=rank(D)
                if d:gains.append(dict(role=r,old_rank=len(frames[nodes[b]])-len(frames[nodes[a]]),added_rank=d))
            _,edge_a,edge_b,_,_=edges[excluded]
            old_paid_rank=len(frames[nodes[edge_b]])-len(frames[nodes[edge_a]]) if kind=='paid' else 0
            result.update(old_paid_rank=old_paid_rank,added_paid_rank=added,helper_gains=gains,rank_surplus_change=sum(x['added_rank'] for x in gains)-added)
            witness=dict(edge=excluded,active_equality_classes=sorted(active),result=result)
            witnesses.append(witness)
            (HERE/'ONE-DEFECT-WITNESSES.json').write_text(json.dumps(witnesses,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
            print('PHASE_WITNESS',json.dumps(result,sort_keys=True),flush=True)
        results.append(result)
        if step%20==0:print('CHECKED',step+1,'useful',len(witnesses),flush=True)
    report=dict(status='EXACT_ONE_EDGE_PHASE_DEFECT_SCAN',script_sha256=P.digest(__file__),
        source_graph_probe_sha256=P.digest(HERE/'owned_phase_probe.py'),sources_sha256=P.digest(HERE/'SOURCES.json'),
        native_word_sha256=sha256(raw).hexdigest(),edge_count=len(edges),equations=len(allrows),
        helper_queries=len(queries),proof_dependency_candidates=len(candidates),tested=len(results),
        complete_candidate_scan=len(results)==len(candidates),requested_limit=args.limit,ordering='decreasing_existing_paid_rank_then_edge',
        results=results,witnesses=witnesses,seconds=time.monotonic()-began,
        scope='Exact homogeneous form feasibility after removing one physical paid/warp edge compatibility block; all owned contacts relaxed. A witness still requires its full rank histogram, moment, native lowering and whole controller. No kappa claimed.')
    (HERE/'EXACT-DEFECT-RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('EXACT_DEFECT_DONE',len(witnesses),'witnesses',report['seconds'],'seconds')

if __name__=='__main__':main()
