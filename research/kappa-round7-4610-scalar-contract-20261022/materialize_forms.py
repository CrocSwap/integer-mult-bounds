"""Expand discovery class labels to sparse literal node-form certificates."""
from pathlib import Path
import gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import owned_phase_probe as P

def main():
    M=P.load();payload=json.loads(gzip.decompress((ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
    _,graph=P.relaxed_graph(M,payload);frames,nodes,fixed,edges,helpers=graph
    forms=M.Forms(frames,nodes,fixed);rows=[]
    incident={n for edge in edges for n in edge[1:3]}
    for e,(kind,a,b,old,image) in enumerate(edges):
        for i,x in enumerate(old):
            for j in range(i,len(old)):
                row=tuple(sorted(set(forms.at(a,x,old[j]))^set(forms.at(b,image[i],image[j]))))
                if row:rows.append((e,row))
    source=HERE/'ONE-DEFECT-WITNESSES.json';witnesses=json.loads(source.read_text(encoding='utf-8'));out=[]
    for w in witnesses:
        eq=M.Equalities(forms.count)
        for e,row in rows:
            if e!=w['edge']:eq.equation(row)
        eq.finish();active=set(w['active_equality_classes']);support={};kernel_support={}
        for n,f in enumerate(nodes):
            if n<2 or n in fixed:continue
            d=len(frames[f]);mask=sum((eq.root(forms.offsets[n]+i) in active)<<i for i in range(d*(d+1)//2))
            if mask:support[n]=mask
            if n in incident:
                possible=sum((eq.root(forms.offsets[n]+i)!=0)<<i for i in range(d*(d+1)//2))
                if possible:kernel_support[n]=possible
        classification=dict(all_residual_equations_discharged=not eq.pending,
            whole_kernel_incident_support_nodes=list(kernel_support))
        if len(kernel_support)==1 and not eq.pending:
            n=next(iter(kernel_support));matches=[(r,a,b,U) for r,a,b,U in helpers if n in [a,b]]
            kind,ea,eb,U,image=edges[w['edge']]
            oldrank=len(frames[nodes[eb]])-len(frames[nodes[ea]]) if kind=='paid' else 0
            if len(matches)==1 and kind=='paid' and oldrank==0 and n in [ea,eb]:
                r,a,b,helperU=matches[0]
                classification.update(all_forms_are_one_helper_boundary_only=True,role=r,
                    boundary='entrance' if n==a else 'exit',old_helper_rank=len(frames[nodes[b]])-len(frames[nodes[a]]),
                    zero_rank_edge=True,helper_form_is_restriction_of_paid_defect=True,
                    all_rank_nonimprovement_by_strict_subadditivity=True)
        out.append(dict(edge=w['edge'],forms=support,claimed_ranks=w['result'],whole_kernel_classification=classification))
    report=dict(status='LITERAL_NODE_FORM_CERTIFICATES',script_sha256=P.digest(__file__),
        source_witnesses_sha256=P.digest(source),sources_sha256=P.digest(HERE/'SOURCES.json'),witnesses=out,
        scope='Literal phase-form matrices only; independent evaluation is in verify_forms.py. No Clifford/native admission.')
    (HERE/'FORMS-WITNESSES.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('MATERIALIZED_FORMS',len(out),'supports',[len(w['forms']) for w in out])
if __name__=='__main__':main()
