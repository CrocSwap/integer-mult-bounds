"""Audit the complete rational bypass and its parameter-dependent error."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('exact_arithmetic',HERE/'retained/arithmetic/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
need,read,encoded = v.need,v.read,v.encoded


def restore(word, delta, reverse=False):
    before, after = ('result','source') if reverse else ('source','result')
    need(sha256(encoded(word)).hexdigest()==delta[before+'_word_sha256'],'exact journal input')
    result = word.copy()
    for field, label in [('forms','changed_forms'),('moves','paid_move_changes')]:
        rows = {r[0]:r[1:] for r in word[field]}
        for key,a,b in delta[label]:
            old,new = (b,a) if reverse else (a,b)
            need(rows.get(key)==old,'exact changed-row preimage')
            if new is None:
                del rows[key]
            else:
                rows[key] = new
        result[field] = [[k,*row] for k,row in sorted(rows.items())]
    result['schedule'] = delta[after+'_schedule']
    need(sha256(encoded(result)).hexdigest()==delta[after+'_word_sha256'],'exact journal output')
    return result


def expected(layout):
    result = [{i:F(1)} for i in range(layout['public'])]
    mains = set()
    for i,x in enumerate(layout['live']):
        y=x+112
        mains.update((x,y))
        if i in layout['hosted']['Dports']:
            result[y][x]=F(1)
        else:
            result[x][y]=F(-1)
            result[y]={x:F(1,2),y:F(1,2)}
    for x,y in zip(layout['hosted']['X2'],layout['hosted']['Y2'],strict=True):
        result[x][y]=F(-1)
        mains.update((x,y))
    need(len(mains)==400,'all main fields')
    return result,mains


def transposed(graph,moves,rows):
    first=graph['first_output']
    result=dict.fromkeys(rows)
    result={k:{} for k in result}
    for target,row in rows.items():
        for donor,q in row.items():
            new_target=first+~donor if donor<0 else donor
            new_donor=~(target-first) if target>=first else target
            result[new_target][new_donor]=q
    return graph | dict(initial=graph['final'],final=graph['initial']),{k:(b,a) for k,(a,b) in moves.items()},result


def tariff(graph,moves,mains):
    spaces=[v.span(f) for f in graph['frames']]
    paid=Counter(abs(len(graph['frames'][a])-len(graph['frames'][b])) for a,b in moves.values())
    targets=Counter()
    for i,(a,b) in enumerate(zip(graph['initial'],graph['final'],strict=True)):
        if i not in mains:
            need(spaces[a]<spaces[b],'positive independent helper target')
            targets[len(graph['frames'][b])-len(graph['frames'][a])]+=1
    return paid,targets


def response(graph,moves,rows,node):
    values=v.scalar(graph,moves,rows,{},[(node,F(1))])
    first=graph['first_output']
    return {i:values[first+i] for i in range(len(graph['initial'])) if values[first+i]}


def plain(row):
    return [[i,str(q)] for i,q in sorted(row.items()) if q]


def scalar_cached(graph,rows,order,inputs):
    values={~i:inputs.get(i,F(0)) for i in range(len(graph['initial']))}
    for k in order:
        values[k]=sum(q*values[j] for j,q in rows[k].items())
    first=graph['first_output']
    return {i:values[first+i] for i in range(len(graph['initial'])) if values[first+i]}


def declared_schedule(graph,rows):
    sequence=graph['schedule']
    need(len(sequence)==len(rows) and set(sequence)==set(rows),'complete declared schedule')
    seen={~i for i in range(len(graph['initial']))}
    for k in sequence:
        need(set(rows[k])<=seen,'declared causal donor order')
        seen.add(k)


def reject(name,action):
    try:
        action()
    except ValueError as error:
        return dict(control=name,rejection=str(error))
    raise ValueError('control passed: '+name)


def run():
    pins=read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw=(HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'source bytes')
    root=HERE/'retained/source/complex'
    after=read(root/'WORD.json.gz')
    layout=read(root/'LAYOUT.json.gz')
    delta=read(root/'POST-BIRTH-CHAIN-1.json.gz')
    before=restore(after,delta,True)
    need(restore(before,delta)==after,'exact bidirectional delta')
    need(all(before[k]==after[k] for k in before.keys()-{'forms','moves','schedule'}),'unchanged entire boundary and geometry')
    need(after['frames']==layout['frames'] and len(after['initial'])==layout['public']==1284,'source-bound complete layout')
    moves0,rows0=v.unpack(before)
    moves,rows=v.unpack(after)
    declared_schedule(before,rows0)
    declared_schedule(after,rows)
    old,old_products=v.expand(before,moves0,rows0)
    new,new_products=v.expand(after,moves,rows)
    wanted,mains=expected(layout)
    first,n=after['first_output'],layout['public']
    need(all(v.vector(old[first+i])==v.vector(new[first+i])==wanted[i] for i in range(n)),'both full forward operators')
    adj_graph,adj_moves,adj_rows=transposed(after,moves,rows)
    adj,adj_products=v.expand(adj_graph,adj_moves,adj_rows)
    transpose=[{} for _ in range(n)]
    for i,row in enumerate(wanted):
        for j,q in row.items():
            transpose[j][i]=q
    need(all(v.vector(adj[first+i])==transpose[i] for i in range(n)),'independent complete adjoint')
    u=v.vector(new[80])
    need(len(u)==17 and u[22]==1 and 1282 not in u,'actual independent bypass payload')
    need(v.add(v.vector(new[34002]),v.vector(old[34002]),F(-1))=={i:q/2 for i,q in u.items()},'exact half-payload recoding')
    need(v.add(v.vector(new[11]),v.vector(old[11]),F(-1))=={i:q/2 for i,q in u.items()},'same downstream alias shift')
    need(all(80 not in rows[k] for k in moves),'new packet has terminal-only readers')
    h=response(after,moves,rows,34002)
    z=response(after,moves,rows,80)
    need((h[1282],z.get(1282,0),h[488],z[488])==(2,0,-1,F(-1,2)),'independent-response minor of determinant minus one')
    bank=sorted([k for k,(_,b) in moves.items() if b==127 and k!=80]+[~i for i,c in enumerate(after['initial']) if c==127])
    basis={}
    for k in bank:
        row=v.reduced(v.vector(new[k]),basis)
        if row:
            pivot=max(row)
            basis[pivot]={j:q/row[pivot] for j,q in row.items()}
    residual=v.reduced(u,basis)
    need(len(bank)==len(basis)==901 and residual,'missing receiving-bank direction')
    witness={max(residual):F(1)}
    for pivot in sorted(basis):
        q=-v.dot(basis[pivot],witness)
        if q:
            witness[pivot]=q
    def separator(w):
        need(all(v.dot(v.vector(new[k]),w)==0 for k in bank),'annihilate every receiving bank')
        need(v.dot(u,w)==-2,'detect missing payload')
    separator(witness)
    need(len(witness)==16,'sparse exact bank separator')
    paid0,targets0=tariff(before,moves0,mains)
    paid,targets=tariff(after,moves,mains)
    difference={r:paid[r]-paid0[r] for r in set(paid)|set(paid0) if paid[r]!=paid0[r]}
    need(difference=={1:-1,4:-1,5:1} and targets==targets0,'whole paid delta and unchanged independent targets')
    need(moves0[12]==(477,127) and moves0[95829]==(237,477) and moves[80]==(237,127),'literal retired and inserted routes')
    need(set(moves0)-set(moves)=={12,95829} and set(moves)-set(moves0)=={80},'all changed paid identifiers')
    sequence=v.order(after,moves,rows)
    tests=[]
    for slope,scale in [(F(0),F(0)),(F(1,2),F(0)),(F(0),F(1)),(F(1),F(1)),(F(3,7),F(-2,5)),(F(1,2),F(1))]:
        altered=rows.copy()
        altered[34002]=v.add(rows[34002].copy(),rows[80],slope-F(1,2))
        altered[80]={j:scale*q for j,q in rows[80].items() if scale*q}
        actual=scalar_cached(after,altered,sequence,{22:F(1)})
        law={i:(slope-F(1,2))*h.get(i,0)+(scale-1)*z.get(i,0) for i in set(h)|set(z)}
        need(all(actual.get(i,0)-wanted[i].get(22,0)==law.get(i,0) for i in range(n)),'full parameter-dependent error column')
        g,mm,rr=transposed(after,moves,altered)
        covector=scalar_cached(g,rr,v.order(g,mm,rr),{488:F(1)})
        need(all(covector.get(j,0)-wanted[488].get(j,0)==law.get(488,0)*u.get(j,0) for j in range(n)),'full parameter-dependent adjoint covector')
        changed=sum(bool(q) for q in law.values())
        need((changed==0)==(slope==F(1,2) and scale==1),'unique correct parameter pair')
        tests.append(dict(slope=str(slope),scale=str(scale),changed_output_rows=changed,
                          error_488_22=str(law.get(488,0)),error_1282_22=str(law.get(1282,0))))
    need(-z[488]*u[22]==F(1,2),'advertised exact omission witness')
    wrong=delta.copy();wrong['result_word_sha256']='0'*64
    controls=[reject('false delta result pin',lambda:restore(after,wrong,True))]
    wrong_moves=moves | {80:(477,127)}
    controls.append(reject('wrong source chart for bypass',lambda:v.order(after,wrong_moves,rows)))
    wrong_witness=witness.copy();wrong_witness[488]+=1
    controls.append(reject('altered separator',lambda:separator(wrong_witness)))
    return dict(source_files=len(pins),source_word=delta['source_word_sha256'],final_word=delta['result_word_sha256'],
                owners=n,coefficients_per_operator=n*n,full_operator_expansions=3,
                integer_coefficient_products=old_products+new_products+adj_products,
                changed_forms=len(delta['changed_forms']),paid_before=len(moves0),paid_after=len(moves),
                paid_delta={str(r):c for r,c in sorted(difference.items())},
                complete_48_call_paid_delta={str(r):48*c for r,c in sorted(difference.items())},
                native_productive={str(r):c for r,c in sorted(targets.items())},
                payload=plain(u),recoding_response=plain(h),bypass_response=plain(z),
                response_minor=[['2','0'],['-1','-1/2']],response_minor_determinant='-1',
                receiving_banks=len(bank),receiving_bank_rank=len(basis),separator=plain(witness),separator_value='-2',
                omission_changed_coefficients=len(u)*len(z),omission_witness=dict(output=488,input=22,value='1/2'),
                parameter_checks=tests,controls=controls)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    start=time.monotonic()
    result=run()
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==read(HERE/'RESULT.json'),'deposited complete audit')
    print('PASS_P104_FINAL_BYPASS_AUDIT',result['coefficients_per_operator'],'coefficients per operator',
          result['receiving_banks'],'bank separator',round(time.monotonic()-start,2),'seconds')
