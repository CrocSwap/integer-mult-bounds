#!/usr/bin/env python3
"""Independent local-rule checker for a degree-three ordinary characteristic-two PC refutation.

Tuple monomials and parity dictionaries are deliberately different from the
producer's packed coefficient rows and monomial bit masks.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
BASELINE=HERE.parents[1]/'turyn-profile-cnf'

def require(value,message):
    if not value: raise ValueError(message)

def add(polynomials):
    parity=Counter()
    for polynomial in polynomials: parity.update(polynomial)
    return frozenset(term for term,count in parity.items() if count%2)

def product(first,second):
    parity=Counter(tuple(sorted(a+b)) for a in first for b in second)
    return frozenset(term for term,count in parity.items() if count%2)

def encode(witness):
    coordinates=witness['coordinates']
    def edge(a,b):
        return all(sum(coordinates[a][8*k+i]*coordinates[b][8*k+i] for i in range(8))!=0 for k in range(3))
    variables=[];forms=[]
    for v in range(17):
        free=[k for k in range(8) if k==7 or not edge(v+7,k)]
        coordinate=[frozenset() for _ in range(8)]
        for k in free[:-1]:
            variables.append([v,k]);coordinate[k]=frozenset({(len(variables)-1,)})
        coordinate[free[-1]]=add([frozenset({()}),*(coordinate[k] for k in free[:-1])])
        forms.append(coordinate)
    equations=[add(product(forms[a][k],forms[b][k]) for k in range(8)) for a,b in witness['core_variable_edges']]
    return variables,forms,equations

def verify_steps(proof,equations,n):
    outputs=[];statistics=Counter();used_axioms=set()
    for i,step in enumerate(proof['steps']):
        kind=step['kind']
        if kind=='axiom':
            require(set(step)=={'kind','edge'},'Axiom schema')
            edge=step['edge'];require(type(edge) is int and 0<=edge<len(equations),'Axiom range')
            result=equations[edge];used_axioms.add(edge)
        elif kind=='multiply':
            require(set(step)=={'kind','input','variable'},'Multiplication schema')
            prior,var=step['input'],step['variable']
            require(type(prior) is int and 0<=prior<i,'Multiplication input precedes step')
            require(type(var) is int and 0<=var<n,'Multiplication variable range')
            result=product(outputs[prior],frozenset({(var,)}))
        elif kind=='xor':
            require(set(step)=={'kind','inputs'},'Addition schema')
            require(step['inputs'] and all(type(p) is int and 0<=p<i for p in step['inputs']),'Addition inputs precede step')
            result=add(outputs[p] for p in step['inputs'])
        else:
            raise ValueError('Unknown proof rule')
        degree=max(map(len,result),default=0)
        require(degree<=3,'Every ordinary polynomial has total degree at most three')
        outputs.append(result);statistics[kind]+=1
        statistics['max_monomials']=max(statistics['max_monomials'],len(result))
        statistics['max_degree']=max(statistics['max_degree'],degree)
    require(type(proof['final']) is int and proof['final']==len(outputs)-1,'Final is last proof step')
    require(outputs[proof['final']]==frozenset({()}),'Final polynomial is constant one')
    require(proof['degree_bound']==3,'Declared degree bound')
    require(used_axioms==set(range(len(equations))),'All 57 essential edge axioms are used')
    statistics['steps']=len(outputs)
    statistics['source_equations']=len(used_axioms)
    statistics['final_monomials']=len(outputs[-1])
    return dict(statistics),outputs

def check_controls(proof,equations,n):
    rejected=[]
    def check(name,changed):
        try: verify_steps(changed,equations,n)
        except (ValueError,KeyError,IndexError,TypeError):rejected.append(name)
        else:raise ValueError('Accepted corrupted proof '+name)
    wrong=copy.deepcopy(proof);wrong['steps'][0]['edge']=(wrong['steps'][0]['edge']+1)%len(equations)
    check('wrong_edge_axiom',wrong)
    bad=copy.deepcopy(proof)
    index=next(i for i,s in enumerate(bad['steps']) if s['kind']=='multiply')
    bad['steps'][index]['input']=index
    check('circular_multiplication',bad)
    missing=copy.deepcopy(proof)
    last=missing['steps'][-1]
    require(last['kind']=='xor' and len(last['inputs'])>1,'Final addition is nontrivial')
    last['inputs'].pop();check('omitted_final_summand',missing)
    sign=copy.deepcopy(proof)
    index=next(i for i,s in enumerate(sign['steps']) if s['kind']=='multiply')
    sign['steps'][index]['variable']=(sign['steps'][index]['variable']+1)%n
    check('wrong_multiplier',sign)
    return rejected

def check_quadratic_minor(equations, certificate):
    columns = [tuple(m) for m in certificate['pivot_monomials']]
    require(len(columns) == len(set(columns)) == len(equations) == 57,
            'A square 57-column minor')
    require(all(len(m) == 2 and tuple(sorted(m)) == m and
                all(type(i) is int and 0 <= i < 40 for i in m) for m in columns),
            'Ordinary quadratic monomial columns')
    all_columns = {m for polynomial in equations for m in polynomial if len(m) == 2}
    require(len(all_columns) == certificate['all_quadratic_monomials'] == 263,
            'Exact full quadratic support')
    matrix = [[int(m in polynomial) for m in columns] for polynomial in equations]
    for pivot in range(57):
        selected = next((i for i in range(pivot, 57) if matrix[i][pivot]), None)
        require(selected is not None, 'Quadratic minor is invertible')
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        for i in range(57):
            if i != pivot and matrix[i][pivot]:
                matrix[i] = [a ^ b for a, b in zip(matrix[i], matrix[pivot])]
    require(certificate['rank'] == certificate['rows'] == 57, 'Rank claim matches checked minor')
    return {'rows': 57, 'selected_columns': 57, 'full_quadratic_support': 263, 'rank': 57}


def run():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for name, digest in sources['baseline_files'].items():
        require(hashlib.sha256((BASELINE/name).read_bytes()).hexdigest() == digest,
                'Pinned baseline mismatch: ' + name)
    witness=json.loads((BASELINE/'WITNESS.json').read_text())
    proof=json.loads((HERE/'ORDINARY-PC-PROOF.json').read_text())
    spec=importlib.util.spec_from_file_location('baseline_geometry',BASELINE/'verify.py')
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    geometry.check_sources();geometry.geometry(witness)
    variables,forms,equations=encode(witness)
    require(proof['variables']==variables,'Exact field-coordinate variable map (no Boolean restriction)')
    require(proof['core_variable_edges']==witness['core_variable_edges'],'Exact core edges')
    statistics,outputs=verify_steps(proof,equations,len(variables))
    rejected=check_controls(proof,equations,len(variables))
    controls=json.loads((BASELINE/'CONTROLS.json').read_text())
    for control in controls['core_single_edge_deletions']:
        values=[(control['labels'][v]>>k)&1 for v,k in variables]
        expected=witness['core_variable_edges'].index(control['removed_edge'])
        for i,eq in enumerate(equations):
            value=sum(all(values[x] for x in term) for term in eq)%2
            require(value==(i==expected),'Polynomial encoding agrees with each exact deletion fitting')
    quadratic = check_quadratic_minor(equations, json.loads((HERE/'QUADRATIC-RANK.json').read_text()))
    return {'quadratic_minor': quadratic, 'status':'PASS_TURYN_ALL_CHAR2_PC_DEGREE_3','free_coordinates':len(variables),'statistics':statistics,'corruption_controls':rejected,'edge_deletion_assignment_controls':len(controls['core_single_edge_deletions'])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    report = run()
    if args.write:
        args.write.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    else:
        require(report == json.loads((HERE/'EXPECTED.json').read_text()), 'Exact algebraic receipt')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
