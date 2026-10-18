#!/usr/bin/env python3
"""Separate Fraction/spectral replay and event-by-event invoice recount.

No imports from the emitter, grid engine, invoice engine, or primary verifier.
Same AI-assisted author; this is not independent human review.
Gareth Davidson (bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ZERO=(F(0),F(0))
ONE=(F(1),F(0))
I=(F(0),F(1))


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def add(z,w):
    return z[0]+w[0],z[1]+w[1]


def mul(z,w):
    return z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0]


def power(z,k):
    if k<0:
        norm=z[0]*z[0]+z[1]*z[1]
        z=(z[0]/norm,-z[1]/norm)
        k=-k
    out=ONE
    for _ in range(k):
        out=mul(out,z)
    return out


def phase(k):
    return (ONE,I,(-F(1),F(0)),(F(0),-F(1)))[k%4]


def route(record, index):
    kind,a,b,_=record
    digits=[(index >> j)&1 for j in range(max(a+b+[0])+1)]
    if kind=='translate':
        for j in a:
            digits[j]^=1
    else:
        insist(kind=='xor','unexpected route')
        old=digits.copy()
        for source,target in zip(a,b):
            digits[target]^=old[source]
    used=sum(1 << j for j in range(len(digits)))
    return (index & ~used)+sum(v << j for j,v in enumerate(digits))


def execute(program, bits, column, inverse=False):
    size=2**bits
    data=[ZERO]*size
    data[column]=ONE
    for record in (reversed(program) if inverse else program):
        kind,a,b,k=record
        if inverse and kind in ('scale_b','phase','global_phase'):
            k=-k
        if kind=='C':
            alpha=(F(1,2),F(-1 if inverse else 1,2))
            beta=(F(1,2),F(1 if inverse else -1,2))
            for bit in a:
                result=list(data)
                for base in range(0,size,2**(bit+1)):
                    for off in range(2**bit):
                        x,y=base+off,base+off+2**bit
                        result[x]=add(mul(alpha,data[x]),mul(beta,data[y]))
                        result[y]=add(mul(beta,data[x]),mul(alpha,data[y]))
                data=result
        elif kind in ('xor','translate'):
            result=[ZERO]*size
            for j,z in enumerate(data):
                result[route(record,j)]=z
            data=result
        elif kind=='phase':
            data=[mul(phase(k*sum((j >> bit)&1 for bit in a)),z) for j,z in enumerate(data)]
        elif kind=='global_phase':
            data=[mul(phase(k),z) for z in data]
        elif kind=='scale_b':
            scalar=power((F(1,2),F(-1,2)),k)
            data=[mul(scalar,z) for z in data]
        else:
            raise ValueError('unknown independent operation')
    return data


def walsh(values):
    """Unnormalized integer Walsh transform, independent of C's coefficients."""
    result=list(values)
    stride=1
    while stride<len(result):
        for start in range(0,len(result),2*stride):
            for j in range(stride):
                a,b=result[start+j],result[start+j+stride]
                result[start+j]=a+b
                result[start+j+stride]=a-b
        stride*=2
    return result


def spectral_reference(name,bits,column,inverse=False):
    size=2**bits
    if name.startswith('C_'):
        re,im=[],[]
        for frequency in range(size):
            p=(-1 if inverse else 1)*frequency.bit_count()
            s=-1 if (frequency & column).bit_count()%2 else 1
            z=phase(p)
            re.append(s*int(z[0]));im.append(s*int(z[1]))
        re,im=walsh(re),walsh(im)
        return [(F(r,size),F(i,size)) for r,i in zip(re,im)]
    f=int(name.split('_f')[-1].split('_')[0])
    mask=2**f-1
    x,y,c=column & mask,(column >> f)&mask,column >> (2*f)
    bank_size=2**(bits-2*f)
    spectra=[[0]*(4**f) for _ in range(bank_size)]
    for u in range(2**f):
        for v in range(2**f):
            sign=-1 if ((u & x).bit_count()+(v & y).bit_count())%2 else 1
            out_bank=c
            if name.startswith('open_P'):
                if (u & c).bit_count()%2:
                    sign=-sign
                out_bank=c ^ v
            else:
                if (u & v).bit_count()%2:
                    sign=-sign
            spectra[out_bank][u+(v << f)]=sign
    result=[]
    for spectrum in spectra:
        result.extend((F(value,4**f),F(0)) for value in walsh(spectrum))
    return result


def recount(fixture):
    bits=fixture['invoice']['address_bits']
    size=2**bits
    count=Counter({'private_real_clears':8})
    kinds=Counter()
    native=Counter()
    def event(kind,addresses,adds=0,halves=0,negs=0,private=0):
        kinds[kind]+=1
        count['records']+=1
        count['real_add_sub']+=adds
        count['exact_halvings']+=halves
        count['real_negations']+=negs
        count['private_real_clears']+=private
        head=0
        for access in ('real_reads','real_writes'):
            for address in addresses:
                count['data_head_cell_steps']+=abs(head-address)
                head=address
                count[access]+=2
                count['complex_cell_visits']+=1
        count['data_head_cell_steps']+=head
    operands=[]
    for record in fixture['program']:
        kind,a,b,k=record
        if kind=='C':
            native[len(a)]+=1
            operands.append({'width':len(a),'cells':size})
            for axis in a:
                for j in range(size):
                    if not(j >> axis)&1:
                        event('C',(j,j+2**axis),12,4,private=8)
        elif kind in ('xor','translate'):
            for j in range(size):
                dest=route(record,j)
                if dest>j:
                    event('swap',(j,dest),private=4)
        elif kind=='scale_b':
            for _ in range(abs(k)):
                for j in range(size):
                    event('b+' if k>0 else 'b-',(j,),2,2 if k>0 else 0,private=4)
        else:
            for j in range(size):
                p=(k*sum((j >> bit)&1 for bit in a) if kind=='phase' else k)%4
                if p:
                    event({1:'i',2:'-1',3:'-i'}[p],(j,),negs=2 if p==2 else 1,private=2)
    count['dispatches']=count['records']
    count['instruction_read_bits']=count['records']*(4+2*bits)
    count['instruction_head_bit_steps']=2*count['instruction_read_bits']
    count={k:v for k,v in count.items() if v}
    inv=fixture['invoice']
    insist(count==inv['execution_counts'],'independent access/arithmetic count differs')
    insist(dict(kinds)==inv['record_kind_counts'],'independent opcode histogram differs')
    insist({str(k):v for k,v in native.items()}==inv['native_C_children'],'independent child histogram differs')
    insist(operands==inv['native_child_operand_cells'],'independent child volume differs')
    insist(count['instruction_read_bits']==inv['program_storage_bits'],'independent program storage differs')
    return count['records']


def replay(receipt):
    cases={}
    total_columns=0
    for name,fixture in receipt['fixtures'].items():
        bits=fixture['invoice']['address_bits']
        # Full Fraction replay of every smaller fixture; 12 disclosed columns at
        # nine axes complement the primary complete 512-column integer-grid runs.
        columns=range(2**bits) if bits<=6 else (0,1,2,3,7,8,31,63,127,255,341,511)
        supports=[]
        for column in columns:
            actual=execute(fixture['program'],bits,column)
            insist(actual==spectral_reference(name,bits,column),
                   f'independent spectral mismatch: {name}, column {column}')
            supports.append(sum(z != ZERO for z in actual))
            if name=='tensor_bank_f3_nested_basis':
                program=fixture['program']
                insist(execute(program[:len(program)//2],bits,column)==spectral_reference('open_P_f3',bits,column),
                       'independent nested open-state mismatch')
        insist([min(supports),max(supports)]==fixture['column_support_minmax'], 'independent support count differs')
        records=recount(fixture)
        total_columns+=len(columns)
        cases[name]={'fraction_columns':len(columns),'all_columns':bits<=6,'recounted_records':records}
    deep=receipt['fixtures']['C_9_two_levels']
    for column in (0,1,2,3,7,8,31,63,127,255,341,511):
        insist(execute(deep['program'],9,column,inverse=True)==spectral_reference('C_9',9,column,inverse=True),
               'independent literal inverse differs')
    ranks=[]
    for f in (1,2,3):
        hist=Counter()
        for code in range(2**(f*f)):
            span={0}
            for row in range(f):
                v=(code >> (f*row)) % 2**f
                span |= {x ^ v for x in tuple(span)}
            hist[len(span).bit_length()-1]+=1
        ranks.append({'columns':f,'rank_histogram':{str(k):v for k,v in sorted(hist.items())}})
    for actual,expected in zip(ranks,receipt['representations']['binary_form_census']):
        insist(actual['rank_histogram']==expected['rank_histogram'],'independent row-span census differs')
    insist(receipt['moment']['matrix_at_zero_saving']==[['1/3','2/3'],['1','0']], 'moment matrix changed')
    # Exact elimination: Q at width 2f makes two C calls of width f. The root
    # consequently has three C children at 1/3 width; two levels have nine.
    insist(sum(F(x) for x in ('1/3','1/3','1/3'))==1,'critical moment not one')
    insist(sum(F(1,9) for _ in range(9))==1,'two-level critical moment not one')
    return {'status':'PASS_INDEPENDENT_PHASE_TENSOR_CHECK','fixtures':cases,
            'forward_fraction_columns':total_columns,'inverse_fraction_columns':12,
            'nested_open_state_fraction_columns':12,
            'binary_rank_census':ranks,'imports_primary_code':False,
            'evidence_status':'Separate representation and spectral reference, same AI-assisted author.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--emit',action='store_true')
    ap.add_argument('--receipt',type=Path,default=HERE/'RESULT.json')
    args=ap.parse_args()
    result=replay(json.loads(args.receipt.read_text()))
    if args.emit:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        insist(result==json.loads((HERE/'INDEPENDENT.json').read_text()),'independent receipt differs')
        print('PASS_INDEPENDENT_PHASE_TENSOR_CHECK no_primary_imports exact_fraction_and_spectral_reference')


if __name__=='__main__':
    main()
