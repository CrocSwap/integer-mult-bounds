"""Standard-library replay, cost dumps, adversarial controls and physical gap."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import json, struct, tempfile
import assignment_certificate as A

HERE=Path(__file__).resolve().parent


def rejected(call):
    try: call()
    except ValueError as error: return str(error)
    raise AssertionError('corrupted certificate was accepted')


def cost_dump(instance,path):
    with path.open('x',encoding='utf-8') as stream:
        stream.write('row\tcolumn\tinteger_cost\tkind\n')
        for i,row in enumerate(A.all_rows(instance)):
            for j,c in sorted(row):
                stream.write(f'{i}\t{j}\t{c}\t{"real" if j<instance["nu"] else "private_dummy"}\n')
    parsed=[]
    for line in path.read_text().splitlines()[1:]:
        i,j,c,kind=line.split('\t');parsed.append((int(i),int(j),int(c)))
    expected=[(i,j,c) for i,row in enumerate(A.all_rows(instance)) for j,c in sorted(row)]
    A.need(parsed==expected,'lossy integer cost dump')
    return {'file_name':path.name,'sha256':A.sha(path),'rows':len(parsed)}


def main():
    names=[('h23-even','fixed-dag-h23-dual-final.json'),
           ('h25-full','fixed-dag-h25-dual-final.json'),
           ('h23-selected','fixed-dag-h23-selected-dual.json'),
           ('h25-selected','fixed-dag-h25-selected-dual.json')]
    reports=[];last=None
    for name,cert_name in names:
        path=HERE/'inputs/matching'/f'{name}-edges.txt';cert_path=HERE/cert_name
        c=json.loads(cert_path.read_text());I=A.parse_instance(path,Q(c['exact_saving']),c['parent_width'],c['quantization_scale'])
        replay=A.replay(path,cert_path)
        negatives={}
        u=c['row_potentials'][:];u[0]+=1
        negatives['row_potential']=rejected(lambda:A.verify_integer_dual(I,c['selected_columns'],u,c['column_potentials']))
        dup=c['selected_columns'][:];dup[1]=dup[0]
        negatives['duplicate_matching_column']=rejected(lambda:A.verify_integer_dual(I,dup,c['row_potentials'],c['column_potentials']))
        v=c['column_potentials'][:];unused=next(j for j in range(I['nc']) if j not in set(c['selected_columns']));v[unused]=-1
        negatives['nonzero_unused_column_price']=rejected(lambda:A.verify_integer_dual(I,c['selected_columns'],c['row_potentials'],v))
        wrong=deepcopy(I);edge=wrong['edges'][0]
        edge['cost']=c['row_potentials'][edge['row']]+c['column_potentials'][edge['column']]-1
        negatives['edge_cost']=rejected(lambda:A.verify_integer_dual(wrong,c['selected_columns'],c['row_potentials'],c['column_potentials']))
        # Temporary data remains beneath this local catalogue directory.
        scratch=HERE/'work';scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            temporary=Path(temporary);A.need(HERE.resolve() in temporary.resolve().parents,'scratch escaped workspace')
            changed=temporary/'changed.txt';changed.write_bytes(path.read_bytes()+b'\n')
            negatives['edge_source_hash']=rejected(lambda:A.replay(changed,cert_path))
        dump=cost_dump(I,HERE/f'{name}-integer-costs.tsv')
        reports.append({'instance':name,'role':'fixed-DAG search/benchmark certificate; not a replacement physical candidate',
            'certificate_file':cert_name,'certificate_sha256':A.sha(cert_path),'edge_file_name':path.name,
            'edge_sha256':A.sha(path),'checked':replay['checked'],'cost_dump':dump,
            'regret_scaled_objective_display':c['true_cost_bounds']['regret_display'],
            'regret_normalized_axis_profile_display':c['true_cost_bounds']['normalized_axis_profile_regret_display'],
            'adversarial_controls':negatives})
        if name=='h25-selected':last=(I,c)
    # Bind the existing already-profiled physical candidate to a LOWER BOUND,
    # without changing its carrier uses or claiming it is quantized-optimal.
    I,c=last;matching=HERE/'inputs/matching/h25-physical-first-order.uses'
    raw=matching.read_bytes();nodes,K=struct.unpack_from('<2I',raw)
    A.need(len(raw)==8+8*K,'matching length changed')
    lookup={(e['donor'],e['use']):(e['row'],e['column']) for e in I['edges']}
    selected=[I['nu']+i for i in range(I['nd'])];touched=set()
    for at in range(K):
        edge=struct.unpack_from('<2I',raw,8+8*at)
        A.need(edge in lookup,'physical matching outside certified graph')
        row,col=lookup[edge];A.need(row not in touched,'duplicate physical donor')
        touched.add(row);selected[row]=col
    A.need(len(set(selected))==I['nd'],'physical matching has duplicate use')
    A.need(K==c['checked']['maximum_cardinality'],'physical matching cardinality differs')
    rows=A.all_rows(I);physical_integer=sum(dict(rows[i])[col] for i,col in enumerate(selected))
    integer_gap=physical_integer-c['checked']['integer_dual'];A.need(integer_gap>=0,'physical objective below exact dual lower bound')
    chosen_lookup={(e['row'],e['column']):e for e in I['edges']}
    chosen=[chosen_lookup[i,col] for i,col in enumerate(selected) if col<I['nu']]
    physical_upper=sum((e['upper'] for e in chosen),Q())
    global_lower=Q(c['true_cost_bounds']['all_maxcard_true_cost_lower_bound'])
    regret=physical_upper-global_lower;A.need(regret>=0,'physical regret interval reversed')
    physical={'matching_file_name':matching.name,'matching_sha256':A.sha(matching),'source_node_count':nodes,
        'status':'actual physical matching bounded against exact optimum dual; not optimum',
        'same_maximum_cardinality':K,'exact_integer_primal_gap':integer_gap,
        'true_scaled_cost_regret_upper':str(regret),'true_scaled_cost_regret_display':float(regret),
        'normalized_axis_profile_regret_upper':str(regret/I['m']),
        'normalized_axis_profile_regret_display':float(regret/I['m']),
        'candidate_replaced':False,'full_profile_and_physical_replay_required_for_new_candidate':True}
    result={'status':'all_four_stdlib_replays_and_twenty_negative_controls_passed',
        'instances':reports,'actual_h25_physical_candidate':physical,
        'objective_units':'F=m^a*sum delta[t]*t^(1-a); normalized axis profile sum delta[t]*(t/m)^(1-a)=F/m',
        'scope':'fixed DAG, fixed exact a from PR48, maximum-cardinality family; not current global optimizer or kappa optimum',
        'exact_source_costs_and_certificates_self_contained':True,'no_absolute_paths_in_evidence':True,
        'audit_tool_sha256':A.sha(__file__),'certificate_verifier_sha256':A.sha(HERE/'assignment_certificate.py'),
        'remote_writes':False}
    destination=HERE/'assignment-audit-receipt.json'
    with destination.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':result['status'],'physical_candidate_gap':integer_gap,
        'physical_true_cost_regret_bound':float(regret),'instances':len(reports),
        'receipt_file':destination.name,'receipt_sha256':A.sha(destination)},indent=2))


if __name__=='__main__':main()
