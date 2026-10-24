"""Independent matrix evaluation of literal forms; no equality solver reused."""
from pathlib import Path
import gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
import owned_phase_probe as P

def rank(rows):
    pivots={}
    for row in rows:
        while row:
            lead=row.bit_length()-1
            if lead in pivots:row^=pivots[lead]
            else:pivots[lead]=row;break
    return len(pivots)

def check(graph,witness):
    frames,nodes,fixed,edges,helpers=graph
    forms={int(n):mask for n,mask in witness['forms'].items()};coordinates={}
    for n,mask in forms.items():
        assert n>=2 and n not in fixed
        B=frames[nodes[n]];d=len(B);assert 0<mask<1<<(d*(d+1)//2)
        if nodes[n] not in coordinates:
            values={0:0}
            for i,x in enumerate(B):values.update({v^x:c|(1<<i) for v,c in list(values.items())})
            assert len(values)==1<<d;coordinates[nodes[n]]=values
    def at(n,x,y):
        if n not in forms:return 0
        B=frames[nodes[n]];a,b=coordinates[nodes[n]][x],coordinates[nodes[n]][y]
        value=k=0
        for i in range(len(B)):
            for j in range(i,len(B)):
                if forms[n]>>k&1:
                    value^=((a>>i)&1)*((b>>j)&1)
                    if i!=j:value^=((a>>j)&1)*((b>>i)&1)
                k+=1
        return value
    changed=[]
    for e,(kind,a,b,U,image) in enumerate(edges):
        if a not in forms and b not in forms:continue
        matrix=[sum((at(a,x,y)^at(b,image[i],image[j]))<<j for j,y in enumerate(U)) for i,x in enumerate(U)]
        d=rank(matrix)
        if d:changed.append((e,d))
    assert len(changed)==1 and changed[0][0]==witness['edge'],('changed edges',changed)
    edge,d=changed[0];kind,a,b,_,_=edges[edge]
    old=len(frames[nodes[b]])-len(frames[nodes[a]]) if kind=='paid' else 0
    gains=[]
    for r,a,b,U in helpers:
        if a not in forms and b not in forms:continue
        dH=rank([sum((at(a,x,y)^at(b,x,y))<<j for j,y in enumerate(U)) for x in U])
        if dH:gains.append(dict(role=r,old_rank=len(frames[nodes[b]])-len(frames[nodes[a]]),added_rank=dH))
    claim=witness['claimed_ranks']
    assert (old,d,gains)==(claim['old_paid_rank'],claim['added_paid_rank'],claim['helper_gains'])
    return dict(edge=edge,old_paid_rank=old,added_paid_rank=d,helper_gains=gains,
        form_support_nodes=len(forms),all_other_edge_defect_ranks_zero=True)

def main():
    if not __debug__:raise ValueError('Run the research assertions enabled')
    M=P.load();payload=json.loads(gzip.decompress((ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
    _,graph=P.relaxed_graph(M,payload)
    source=HERE/'FORMS-WITNESSES.json';data=json.loads(source.read_text(encoding='utf-8'))
    assert data['source_witnesses_sha256']==P.digest(HERE/'ONE-DEFECT-WITNESSES.json')
    results=[check(graph,w) for w in data['witnesses']]
    from copy import deepcopy
    controls=[]
    for name,mutate in [
        ('omitted_phase_form',lambda w:w.update(forms={})),
        ('incorrect_paid_rank',lambda w:w['claimed_ranks'].update(old_paid_rank=9)),
        ('inflated_helper_gain',lambda w:w['claimed_ranks']['helper_gains'][0].update(added_rank=2))]:
        bad=deepcopy(data['witnesses'][0]);mutate(bad)
        try:check(graph,bad)
        except AssertionError:controls.append(name)
        else:raise AssertionError('corruption accepted '+name)
    result=dict(status='PASS_INDEPENDENT_LITERAL_PHASE_FORM_RANKS',script_sha256=P.digest(__file__),
        forms_sha256=P.digest(source),source_graph_probe_sha256=P.digest(HERE/'owned_phase_probe.py'),
        results=results,controls=controls,equality_solver_used=False,
        scope='Every fixed boundary, actual graph edge and helper form rank checked by independent coordinate/matrix evaluation. Original graph extraction retained. No native amplitude, absolute phase, compiler or kappa claim.')
    (HERE/'VERIFIED-FORMS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('PASS_INDEPENDENT_LITERAL_PHASE_FORM_RANKS',len(results),'witnesses',len(controls),'controls')
if __name__=='__main__':main()
