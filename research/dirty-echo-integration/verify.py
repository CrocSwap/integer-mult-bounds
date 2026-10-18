#!/usr/bin/env python3
"""Exact functional integration plus rejection of an unprofitable supplier bill."""
import argparse
import copy
from fractions import Fraction as F
import importlib.util
import json
from math import prod
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


A=load('verified_adapter',HERE/'adapter.py')
T=load('verified_transform',HERE/'transform.py')
O=load('direct_oracles',HERE/'oracles.py')
need=A.need


def complex_checks():
    cases=0;calls=0
    for bits in ((0,),(0,1),(0,2),(0,1,2)):
        length=1<<(max(bits)+1)
        for fanout in (2,8):
            W=A.role_count(len(bits),fanout)
            # Full complex basis, including every borrowed role's input column.
            for column in range(W*length):
                rows=[[A.ZERO]*length for _ in range(W)]
                rows[column//length][column%length]=A.ONE
                expected=[O.c_tensor(row,bits) for row in rows]
                receipt=A.complex_layer(rows,bits,1,fanout)
                need(rows==expected,'all-role complex basis')
                need(receipt['leaf_calls']==3*(W//2)*A.E.resources(len(bits),fanout)[1],'complex child count')
                cases+=1;calls+=receipt['leaf_calls']
    return dict(basis_cases=cases,leaf_executions=calls)


def bit_checks():
    rows_checked=0;results=[]
    for q in (3,5):
        for groups in ((1,2,3) if q==3 else (1,2)):
            permutations,whole=O.address_swap_permutations(q,groups);length=len(whole)
            for fanout in (2,8):
                W=A.role_count(groups,fanout)
                # Each integer's bits are formal coefficients of ALL W*length
                # independent input bits. Equality checks the entire linear map.
                rows=[[1<<(role*length+j) for j in range(length)] for role in range(W)]
                expected=[[row[j] for j in whole] for row in rows]
                receipt=A.boolean_layer(rows,permutations,fanout)
                need(rows==expected,'all-role Boolean address interchange')
                need(receipt['leaf_calls']==3*(W//2)*A.E.resources(groups,fanout)[1],'bit child count')
                rows_checked+=W*length
                results.append(dict(radix=q,groups=groups,fanout=fanout,independent_input_bits=W*length,**receipt))
    return dict(symbolic_output_rows=rows_checked,cases=results)


def full_transform_checks():
    results=[];basis_count=0
    for axes,r in (((2,),2),((2,2),2),((4,2),2),((4,4),2),((8,2),4),((4,2,2),2)):
        W=A.role_count(len(axes),8);length=prod(axes)*r
        initial=[[(F(2*j+role+1,16),F(j-3*role-1,16)) for j in range(length)] for role in range(W)]
        expected=[O.bit_reverse_records(O.fourier(row,axes,r,-1),axes,r) for row in initial]
        rows=copy.deepcopy(initial);receipt=T.transform(rows,axes,r)
        need(rows==expected,'complete stored-order forward transform')
        T.transform(rows,axes,r,opposite=True)
        need(rows==[[A.scale(z,F(1,prod(axes))) for z in row] for row in initial],'opposite normalization and round trip')
        left=copy.deepcopy(initial)
        right=[[(F(3*j-role+2,32),F(role+j+1,32)) for j in range(length)] for role in range(W)]
        exact=[O.convolution(x,y,axes,r) for x,y in zip(left,right)]
        T.transform(left,axes,r);T.transform(right,axes,r)
        product_rows=[]
        for x,y in zip(left,right):
            product_row=[]
            for start in range(0,length,r):
                product_row.extend(O.polynomial_product(x[start:start+r],y[start:start+r]))
            product_rows.append(product_row)
        T.transform(product_rows,axes,r,opposite=True)
        restored=[[A.scale(z,prod(axes)**2) for z in row] for row in product_rows]
        need(restored==exact,'complete cyclic/negacyclic convolution normalization')
        need([[A.scale(z,prod(axes)) for z in row] for row in product_rows]!=exact,'missing convolution normalization control')
        results.append(receipt)
        if axes in ((2,),(2,2)):
            for column in range(W*length):
                rows=[[A.ZERO]*length for _ in range(W)]
                rows[column//length][column%length]=A.ONE
                expected=[O.bit_reverse_records(O.fourier(row,axes,r,-1),axes,r) for row in rows]
                T.transform(rows,axes,r)
                need(rows==expected,'complete transform basis column')
                basis_count+=1
    rotations=0
    for r in (2,4,8):
        row=[(F(i+1),F(2*i-1)) for i in range(r)]
        for exponent in range(-2*r,2*r+1):
            result=row[:];T.rotate_record_in_place(result,0,r,exponent)
            need(result==O.rotate(row,exponent),'signed monomial cycle')
            rotations+=1
    return dict(cases=results,additional_basis_columns=basis_count,signed_rotation_checks=rotations,wrong_convolution_scale_rejected_cases=len(results))


def mutation_checks():
    controls=[]
    d=3;length=1<<d;W=A.role_count(d,8)
    initial=[[(F(2*j+role+1,16),F(j-3*role-1,16)) for j in range(length)] for role in range(W)]
    expected=[O.c_tensor(row,range(d)) for row in initial]
    for mutant in ('omit_negative_leaf','skip_borrowed_outputs','omit_role_exchange','omit_inverse_phase'):
        rows=copy.deepcopy(initial);A.complex_layer(rows,range(d),1,8,mutant)
        need(rows!=expected,'complex mutation escaped: '+mutant);controls.append('complex:'+mutant)
    permutations,whole=O.address_swap_permutations(3,2);length=len(whole);W=A.role_count(2,8)
    initial=[[1<<(role*length+j) for j in range(length)] for role in range(W)]
    expected=[[row[j] for j in whole] for row in initial]
    for mutant in ('omit_negative_leaf','skip_borrowed_outputs','omit_role_exchange'):
        rows=copy.deepcopy(initial);A.boolean_layer(rows,permutations,8,mutant)
        need(rows!=expected,'Boolean mutation escaped: '+mutant);controls.append('bit:'+mutant)
    axes=(4,2);r=2;length=prod(axes)*r;W=A.role_count(2,8)
    initial=[[(F(j+role+1,8),F(role-j,8)) for j in range(length)] for role in range(W)]
    expected=[O.bit_reverse_records(O.fourier(row,axes,r,-1),axes,r) for row in initial]
    for mutant in ('omit_normalization','reverse_twiddle_sign'):
        rows=copy.deepcopy(initial);T.transform(rows,axes,r,mutant=mutant)
        need(rows!=expected,'transform mutation escaped: '+mutant);controls.append('transform:'+mutant)
    # Both interfaces must reject borrowed/input aliases before execution.
    for label,call in [('complex',lambda arrays:A.complex_layer(arrays,(0,1),1)),
                       ('bit',lambda arrays:A.boolean_layer(arrays,[list(range(8))]*2)),
                       ('full_transform',lambda arrays:T.transform(arrays,(2,2),2))]:
        row=[A.ONE]*8;arrays=[row,row,[A.ZERO]*8,[A.ZERO]*8];saved=copy.deepcopy(arrays)
        try:call(arrays)
        except ValueError as error:
            need(str(error)=='distinct arrays' and arrays==saved,'alias rejection after mutation')
        else:raise ValueError('alias admitted')
        controls.append(label+':role_alias')
    return controls


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    pins=load('functional_provenance',HERE/'provenance.py').check()
    complex_result=complex_checks();print('PASS complex all-role basis',complex_result['basis_cases'],flush=True)
    bit_result=bit_checks();print('PASS Boolean full-domain symbolic rows',bit_result['symbolic_output_rows'],flush=True)
    transforms=full_transform_checks();print('PASS complete transforms and convolution',len(transforms['cases']),flush=True)
    controls=mutation_checks()
    report=dict(status='PASS_FUNCTIONAL_ECHO_INTEGRATION',inherited_source_hashes=pins['files'],complex=complex_result,bit=bit_result,transforms=transforms,negative_controls=controls,
                scope='Exact finite functional adapters and full stored-order synthetic transforms. These are indexed-read prototypes, not admitted fixed-tape suppliers or a new kappa.')
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(controls),'negative controls')


if __name__=='__main__':main()
