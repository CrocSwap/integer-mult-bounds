#!/usr/bin/env python3
"""Exact mutable-source persistent connector pilot. Apache-2.0, woklerx/Codex."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, message):
    if not ok: raise ValueError(message)

def transform(matrix, vector):
    return [xor(vector[j] for j in range(len(vector)) if row >> j & 1) for row in matrix]

def xor(values):
    result = 0
    for value in values: result ^= value
    return result

def product(left, right):
    return tuple(xor(right[j] for j in range(len(right)) if row >> j & 1) for row in left)

def word(a1, a2, b, c, correction=True, reverse_product=False):
    out = [(3,2,a1), (2,0,b), (3,2,a1), (0,1,c)]
    if correction: out.append((2,1,product(c,b) if reverse_product else product(b,c)))
    return out + [(4,2,a2), (2,0,b), (4,2,a2)]

def apply(registers, operations):
    registers = [list(v) for v in registers]
    for target, source, matrix in operations:
        delta = transform(matrix, registers[source])
        registers[target] = [a ^ b for a,b in zip(registers[target],delta)]
    return registers

def expected(registers, a1, a2, b, c):
    x,u,z,y1,y2 = registers
    newx = [a ^ b for a,b in zip(x,transform(c,u))]
    return [newx,list(u),list(z),
            [a ^ b for a,b in zip(y1,transform(a1,transform(b,x)))],
            [a ^ b for a,b in zip(y2,transform(a2,transform(b,newx)))]]

def rank(rows):
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in basis: row ^= basis[p]
            else: basis[p]=row; break
    return len(basis)

def run():
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage']=='input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'source drift')
    matrices = list(itertools.product(range(4),repeat=2))
    basis = [[1 << (2*i+j) for j in range(2)] for i in range(5)]
    cases = 0
    for a1,a2,b,c in itertools.product(matrices,repeat=4):
        operations=word(a1,a2,b,c)
        actual=apply(basis,operations)
        need(actual==expected(basis,a1,a2,b,c),'all-matrix dirty column mismatch')
        need(apply(actual,reversed(operations))==basis,'all-matrix inverse mismatch')
        cases+=1
    a1,a2,b,c=(2,4,1),(3,2,4),(3,6,7),(1,0,0)
    baseline=[(2,0,b),(3,2,a1),(2,0,b),(3,2,a1),(0,1,c),
              (2,0,b),(4,2,a2),(2,0,b),(4,2,a2)]
    candidate=word(a1,a2,b,c)
    def lower(operations):
        return [(3*t+i,3*s+j) for t,s,m in operations
                for i,row in enumerate(m) for j in range(3) if row>>j&1]
    base_gates, new_gates=lower(baseline),lower(candidate)
    def scalar(bits,gates):
        values=list(bits)
        for t,s in gates: values[t]^=values[s]
        return values
    failures={'omit-correction':0,'reverse-product':0,'omit-final-B':0}
    mutants={'omit-correction':lower(word(a1,a2,b,c,False)),
             'reverse-product':lower(word(a1,a2,b,c,True,True)),
             'omit-final-B':lower(candidate[:-2]+candidate[-1:])}
    for bits in itertools.product(range(2),repeat=15):
        base=scalar(bits,base_gates)
        output=scalar(bits,new_gates)
        need(output==base,'literal scalar truth-table mismatch')
        need(scalar(output,list(reversed(new_gates)))==list(bits),'literal inverse')
        for key,gates in mutants.items(): failures[key]+=scalar(bits,gates)!=base
    need(all(failures.values()),'undetected mutation')
    need(len(base_gates)==43 and len(new_gates)==31,'complete XOR invoice')
    need(rank(b)==3 and rank(c)==rank(product(b,c))==1,'fixture ranks')
    travel_base=sum(2*max(t,s) for t,s in base_gates)
    travel_new=sum(2*max(t,s) for t,s in new_gates)
    need(travel_new<travel_base,'paid head travel')
    return dict(status='PASS_MUTABLE_SOURCE_PERSISTENT_CONNECTOR',all_2x2_matrix_quadruples=cases,
                dirty_columns_per_case=10,literal_3bit_dirty_inputs=32768,
                matrices=dict(A1=a1,A2=a2,B=b,C=c,BC=product(b,c)),
                scalar_XOR_baseline=len(base_gates),scalar_XOR_candidate=len(new_gates),
                removed_B_calls=2,paid_correction_XORs=2,
                origin_return_head_steps=dict(baseline=travel_base,candidate=travel_new),
                data_accesses=dict(baseline=3*len(base_gates),candidate=3*len(new_gates)),
                failure_controls=failures)

if __name__=='__main__':
    result=run()
    receipt=HERE/'EXPECTED.json'
    if receipt.exists(): need(json.loads(receipt.read_text())==json.loads(json.dumps(result)),'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
