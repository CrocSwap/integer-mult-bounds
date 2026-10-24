"""Exact small-width execution and all-width channel certificates."""
import argparse,ast,hashlib,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from channels import *


def reject(call,text):
    try: call()
    except ValueError as exc:
        need(text in str(exc),'wrong rejection '+str(exc)); return
    raise ValueError('missing rejection '+text)


def main():
    source={}
    for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':
            content=(ROOT/r['path']).read_bytes()
            need(hashlib.sha256(content).hexdigest()==r['sha256'],'source bytes '+r['path'])
            source[r['path']]=content
    tree=ast.parse(source['research/complex-prefix-native-ports/verify_full_input_port.py'])
    mainfn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    assignments={ast.unparse(n.targets[0]):ast.unparse(n.value) for n in mainfn.body if isinstance(n,ast.Assign)}
    expected={'U':'v.monomial([0, 5, 2, 7, 4, 1, 6, 3])',
              'V':'v.monomial([0, 2, 1, 3, 4, 6, 5, 7])','S':'v.s_letter(7)',
              '(P, Q)':'(v.word(S, U, S), v.word(S, V, S))',
              'W':'v.pauli(0, 5)','J':'v.word(v.pauli(0, 2), V, C[2])',
              'A':'C[0]','D':'v.word(J, W, C[0])'}
    need(all(assignments.get(k)==v for k,v in expected.items()),'actual phase-letter/source bindings')
    b=letters()
    for k,a in b.items():
        need(product(a,adjoint(a))==eye(),'unitary actual letter '+k)
    # Flat row norms and row-zero coherent overlaps are finite base facts,
    # which tensor functoriality then extends to every positive width.
    checks=[('F',word(b['A'],b['P'],b['A']),word(b['A'],b['Q'],b['A']),2),
            ('AL',word(b['A'],b['P']),word(b['A'],b['Q']),1),
            ('B',word(b['D'],b['P'],b['A']),word(b['D'],b['Q'],b['A']),None),
            ('DL',word(b['D'],b['P']),word(b['D'],b['Q']),2),
            ('L',b['P'],b['Q'],0)]
    for name,x,y,k in checks:
        for row in (x[0],):
            for j,z in row.items():
                if j in y[0]:
                    ratio=mul(z,conj(y[0][j]))
                    need(ratio[1]==0 and ratio[0]>0,'coherent row-zero overlap '+name)
        if k is not None:
            need(all(l1(row)==Lpower(k) for row in x+y),'flat branch row norms '+name)
        else:
            need(all(l1(row)==Lpower(1) for row in x)
                 and all(l1(row)==Lpower(3) for row in y),'different-rank B branch norms')
    records=[]; trajectories=0; basis_cases=0
    for f in (1,2,3):
        n=8**f; zero=[ZERO]*n
        for kind in (2,3):
            for reverse in (False,True):
                channels=maps(b,f,kind,reverse)
                if reverse:
                    norms=[(Q(3),Q(0)),Lpower(f if kind==2 else 2*f)]
                    norms+=([(Q(1),Q(0))] if kind==2 else [Lpower(f),(Q(1),Q(0))])
                    norms.append((Q(0),Q(0)))
                else:
                    norms=[pair_scale(3,Lpower(2*f)) if kind==2 else pair_sum(pair_scale(2,Lpower(3*f)),Lpower(f)),
                           Lpower(f if kind==2 else 2*f),pair_scale(3,Lpower(f if kind==2 else 2*f)),
                           (Q(1),Q(0)) if kind==2 else Lpower(f)]
                    if kind==3: norms.append((Q(1),Q(0)))
                for matrix,wanted in zip(channels,norms):
                    if matrix is None: continue
                    need(l1(matrix[0])==wanted and all(leq(l1(r),wanted) for r in matrix),'sharp channel norm')
                summed=pair_sum(*norms)
                expected_sum=(pair_sum(Lpower(f),(Q(4),Q(0))) if kind==2 else
                              pair_sum(Lpower(2*f),Lpower(f),(Q(4),Q(0)))) if reverse else (
                              pair_sum(pair_scale(3,Lpower(2*f)),pair_scale(4,Lpower(f)),(Q(1),Q(0))) if kind==2 else
                              pair_sum(pair_scale(2,Lpower(3*f)),pair_scale(4,Lpower(2*f)),pair_scale(2,Lpower(f)),(Q(1),Q(0))))
                need(summed==expected_sum,'source-ordered total sharp amplification')
                x=[(Q((3*i+1)%7-3,8),Q((5*i+2)%9-4,8)) for i in range(n)]
                y=[(Q((-1)**i,4),Q(i%3,8)) for i in range(n)]
                unperturbed=schedule(b,f,kind,reverse,x,y,[zero]*(kind+2))
                for site in range(kind+2):
                    delta=[(Q((i+site)%5-2,16),Q((2*i+site)%7-3,16)) for i in range(n)]
                    ds=[zero]*(kind+2);ds[site]=delta
                    actual=schedule(b,f,kind,reverse,x,y,ds)
                    lower=zero if channels[site] is None else apply(channels[site],delta)
                    upper=(apply(power(adjoint(b['A']) if reverse else b['A'],f),delta) if site==0 else
                           delta if site==(kind+1 if reverse else 2) else zero)
                    need(actual==(vplus(unperturbed[0],upper),vplus(unperturbed[1],lower)),'actual chronological defect propagation')
                    trajectories+=1
                if f==1:
                    for site,matrix in enumerate(channels):
                        for j in range(n):
                            ds=[zero]*(kind+2); ds[site]=[ONE if i==j else ZERO for i in range(n)]
                            got=schedule(b,f,kind,reverse,zero,zero,ds)[1]
                            want=zero if matrix is None else [r.get(j,ZERO) for r in matrix]
                            need(got==want,'independent impulse columns');basis_cases+=1
                records.append(dict(f=f,kind=kind,reverse=reverse,total=[str(q) for q in summed],
                                    channel_norms=[[str(q) for q in z] for z in norms]))
    # Rational all-width gate: sqrt(2)<3/2, f>=1.
    need(Q(3,2)**2>2 and Q(51,8)<8 and Q(15,4)<4,'uniform dyadic guard margins')
    reject(lambda: power(b['A'],0),'bounded executable width')
    reject(lambda: l1({0:(Q(1),Q(2))}),'eighth-root')
    wrong=dict(b,Q=b['P'])
    need(maps(wrong,1,3)[0]!=maps(b,1,3)[0],'changed phase/monomial control')
    actual=maps(b,1,3)[3]
    need(actual!=power(word(b['W'],b['J']),1),'reversed second-defect propagation control')
    need(maps(b,1,3)[4]!=eye(),'third defect retains its post-call monomial')
    need(not leq((Q(7),Q(0)),(Q(6),Q(0))),'false cap control')
    result=dict(records=records,perturbed_trajectories=trajectories,impulse_columns=basis_cases,
                base_coherence_checks=len(checks),controls=6,new_kappa=False,
                gaussian_implementation_internal_error_guarantee='premise',physical_execution=False)
    encoded=json.dumps(result,sort_keys=True,separators=(',',':'))
    parser=argparse.ArgumentParser();parser.add_argument('--emit',type=Path);args=parser.parse_args()
    if args.emit:
        with args.emit.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    else:need(encoded==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True,separators=(',',':')),'complete typed receipt')
    print(json.dumps(dict(cases=len(records),trajectories=trajectories,impulse_columns=basis_cases,
                         result_sha256=hashlib.sha256(encoded.encode()).hexdigest()),sort_keys=True))
    print('PASS_NATIVE_ERROR_CHANNEL_AMPLIFICATION all_width_source_order no_new_kappa')


if __name__=='__main__':main()
