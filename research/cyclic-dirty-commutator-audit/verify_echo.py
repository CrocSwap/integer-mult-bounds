#!/usr/bin/env python3
"""Independent ideal identity, integer-grid differential, and dense error checks."""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = load('dirty_echo', HERE/'echo.py')
M = load('echo_integer_model', HERE/'integer_model.py')


def matvec(matrix, vector):
    return [sum(a*b for a,b in zip(row,vector)) for row in matrix]


def ideal_checks():
    # Arbitrary noncommuting integer maps: direct matrix composition, no leaf or
    # schedule recurrence, is the oracle for the streamed echo's target effect.
    rng = random.Random(67)
    cases = 0
    for nf in (1,2,3,5,8,15,16,64):
        matrices = [[[rng.randrange(-2,3) for _ in range(2)] for _ in range(2)] for _ in range(nf)]
        for fanout in sorted({2,3,4,8,max(2,nf)}):
            depth,calls = E.resources(nf,fanout)
            before = [[rng.randrange(-7,8) for _ in range(2)] for _ in range(depth+2)]
            expected = before[0][:]
            for matrix in matrices:
                expected = matvec(matrix,expected)
            positive = list(E.instructions(0,nf,0,1,2,fanout))
            negative = list(E.instructions(0,nf,0,1,2,fanout,-1))
            need(len(positive) == calls, 'ideal leaf count')
            need(negative == [(s,t,i,-q) for s,t,i,q in reversed(positive)], 'reverse inverse word')
            for sign,word in ((1,positive),(-1,negative)):
                arrays = copy.deepcopy(before)
                for src,dst,index,q in word:
                    increment = matvec(matrices[index],arrays[src])
                    arrays[dst] = [a+q*b for a,b in zip(arrays[dst],increment)]
                need(arrays[0] == before[0] and arrays[2:] == before[2:], 'ideal restoration')
                need(arrays[1] == [a+sign*b for a,b in zip(before[1],expected)], 'ideal noncommuting product')
                cases += 1
    # Drop the first-link undo: both restoration and ideal target checks detect it.
    nf=3;fanout=3;before=[[2],[7],[3],[5]];word=list(E.instructions(0,nf,0,1,2,fanout))
    mutants = {'missing_first_undo': [op for j,op in enumerate(word) if j != 4],
               'missing_dirty_subtraction': [op for op in word if op != (3,1,2,-1)]}
    for name,word in mutants.items():
        arrays=copy.deepcopy(before)
        for src,dst,index,q in word:
            arrays[dst][0] += q*(index+2)*arrays[src][0]
        need(arrays[0] != before[0] or arrays[2:] != before[2:] or arrays[1] != [55], name+' escaped')
    # Opposite signs in forward order are not generally the inverse of the word.
    arrays=copy.deepcopy(before[:3])
    for src,dst,index,q in E.instructions(0,2,0,1,2,2):
        arrays[dst][0] -= q*(index+2)*arrays[src][0]
    need(arrays != [before[0],[-5],before[2]], 'wrong inverse order escaped')
    return dict(noncommuting_cases=cases,negative_controls=list(mutants)+['sign_only_inverse'])


def rounded_checks(D):
    rng = random.Random(67)
    units = [(F(1),F(0)),(F(0),F(1)),(F(3,5),F(4,5))]
    cases=0;digest=hashlib.sha256()
    for nf in (1,2,3,5,8,15,16):
        factors=[(i%2==0,(F(1,4),F((-1)**i,8)),F(3 if i==0 else 1)) for i in range(nf)]
        for fanout in sorted({2,3,4,8,max(2,nf)}):
            depth,leaves=E.resources(nf,fanout)
            for length in (1,2,3):
                phases=[units[i%3] for i in range(length)]
                for bits in (4,16):
                    grid=1<<bits
                    integers=[[(rng.randrange(-grid,grid+1),rng.randrange(-grid,grid+1)) for _ in range(length)] for _ in range(2+depth)]
                    original=[[(F(a,grid),F(b,grid)) for a,b in array] for array in integers]
                    for direction in (-1,1):
                        for sign in (-1,1):
                            arrays=copy.deepcopy(original);expected=copy.deepcopy(integers)
                            stats=E.compose(D,*arrays[:2],factors,arrays[2:],phases,F(1,2),bits,direction,sign,fanout)
                            need(stats['leaves'] == leaves, 'rounded leaf count')
                            # Shared schedule; the independent arithmetic checks below
                            # do not constitute an independent identity proof.
                            for src,dst,index,q in E.instructions(0,nf,0,1,2,fanout,sign):
                                M.execute_leaf(expected,(src,dst,factors[index],q),phases,bits,direction)
                            need(arrays == [[(F(a,grid),F(b,grid)) for a,b in z] for z in expected], 'integer arithmetic differential')
                            need(arrays[0] == original[0] and arrays[2:] == original[2:], 'rounded restoration')
                            digest.update(json.dumps(arrays,default=str).encode())
                            E.compose(D,*arrays[:2],factors,arrays[2:],phases,F(1,2),bits,direction,-sign,fanout)
                            need(arrays == original, 'rounded exact inverse')
                            cases+=1
    return dict(cases=cases,output_digest=digest.hexdigest(),seed=67)


def ceil_log2(q):
    result=q.numerator.bit_length()-q.denominator.bit_length()
    if F(2)**result < q:
        result+=1
    return result


def dense_checks(D):
    results=[];beta=F(1,2);r=3;p=32;a=13*(r+1)/beta**3;G=2+F(r)/beta
    for nf in (1,3,8,15):
        factors=[(i%2==0,(F(1,4),F((-1)**i,8)),F(r if i==0 else 1)) for i in range(nf)]
        for fanout in sorted({2,8,max(2,nf)}):
            depth,N=E.resources(nf,fanout)
            for length in (1,3):
                phases=[(F(1),F(0)),(F(0),F(1)),(F(3,5),F(4,5))][:length]
                for direction in (-1,1):
                    for dirt in (0,7,-13):
                        before=[[(F(dirt+2*i+j,4),F(dirt-3*i-j,8)) for i in range(length)] for j in range(depth+2)]
                        magnitude=max(abs(x)+abs(y) for array in before for x,y in array)
                        bits=max(p+1+ceil_log2(N*a*(magnitude+1))+(N-1)*ceil_log2(G),ceil_log2(a),ceil_log2(2/beta**2))
                        u=F(1,1<<bits);bound=N*a*(magnitude+1)*u*G**(N-1)
                        need(a*u<=1 and u<=beta**2/2 and bound<=F(1,1<<(p+1)), 'complete precision budget')
                        expected=D.exact_operator(before[0],factors,phases,direction)
                        arrays=copy.deepcopy(before)
                        E.compose(D,*arrays[:2],factors,arrays[2:],phases,beta,bits,direction,fanout=fanout)
                        error=max(D.c.norm2(D.c.sub(D.c.sub(y,y0),z)) for y,y0,z in zip(arrays[1],before[1],expected))
                        need(error<=bound**2, 'dense error bound')
                        need(arrays[0]==before[0] and arrays[2:]==before[2:], 'dense source/scratch restoration')
                        results.append(dict(factors=nf,fanout=fanout,length=length,direction=direction,dirt=dirt,leaves=N,bits=bits,error_squared=str(error),bound=str(bound)))
    return results


def admission_checks(D):
    cases=0
    for nf in (1,3,8,15):
        for fanout in sorted({2,8,max(2,nf)}):
            depth,_=E.resources(nf,fanout)
            for alias in range(depth+2):
                arrays=[[(F(1),F(0))]*2 for _ in range(depth+2)]
                before=copy.deepcopy(arrays)
                try:
                    E.compose(D,*arrays[:2],[(False,(F(1,4),F(0)),F(1))]*nf,arrays[2:],arrays[alias],F(1,2),8,1,fanout=fanout)
                except ValueError as error:
                    need(str(error)=='phase array aliases mutable data' and arrays==before, 'late alias rejection')
                else:
                    raise ValueError('phase alias accepted')
                cases+=1
    for count,fanout in ((0,2),(1,1),(2,0)):
        try:
            E.resources(count,fanout)
        except ValueError:
            pass
        else:
            raise ValueError('invalid resource domain accepted')
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    source=json.loads((HERE/'SOURCE.json').read_text())
    with tempfile.TemporaryDirectory(prefix='dirty-echo-') as temp:
        root=Path(temp)
        for name,digest in source['files'].items():
            result=subprocess.run(['git','show',source['commit']+':'+source['package']+'/'+name],cwd=REPO,capture_output=True)
            need(result.returncode==0,'fetch pinned PR628 first')
            need(hashlib.sha256(result.stdout).hexdigest()==digest,'source hash '+name)
            (root/name).write_bytes(result.stdout)
        D=load('echo_leaf_source',root/'dirty.py')
        ideal=ideal_checks();print('PASS ideal noncommuting identity',ideal['noncommuting_cases'],flush=True)
        rounded=rounded_checks(D);print('PASS rounded integer differential',rounded['cases'],flush=True)
        dense=dense_checks(D);print('PASS dense error checks',len(dense),flush=True)
        aliases=admission_checks(D)
    resources=[]
    for nf in (8,16,64,512):
        for fanout in sorted({2,8,nf}):
            depth,calls=E.resources(nf,fanout)
            resources.append(dict(factors=nf,fanout=fanout,borrowed_arrays=depth,leaf_calls=calls))
            if nf==fanout:
                need(depth==nf-1 and calls==4*nf-4,'flat resources')
    report=dict(status='PASS_MULTIWAY_DIRTY_ECHO',source_commit=source['commit'],ideal=ideal,rounded=rounded,dense=dense,alias_rejections=aliases,resources=resources,scope='Classical local primitive with a symbolic proof; finite executable evidence is not formal verification or a new kappa.')
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],ideal['noncommuting_cases'],'ideal;',rounded['cases'],'rounded;',len(dense),'dense;',aliases,'alias rejections')


if __name__=='__main__':
    main()
