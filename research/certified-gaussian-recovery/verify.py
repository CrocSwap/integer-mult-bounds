#!/usr/bin/env python3
"""Independent Gaussian integration replay; integer/rational acceptance only."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parent.parent


def authenticate():
    sources=json.loads((PACKAGE/'SOURCES.json').read_text())
    for entry in sources['files']:
        if entry['usage']=='input':
            actual=hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()
            if actual!=entry['sha256']:
                raise ValueError('pinned source drift: '+entry['path'])


authenticate()
sys.path.insert(0,str(PACKAGE))
from intervals import (Interval, need, pi_interval, exp_negative, root_of_unity,
                       cadd, cmul, cconj, grid_point, point, inward_quantize)
from gaussian import GaussianLine, correction_matrix
from pipeline import multiply, uniform_certificate


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def rejected(action,label):
    try:action()
    except ValueError:return label
    raise ValueError('negative control was accepted: '+label)


def strict_power_bound(value):
    need(value>0,'positive bound')
    k=0
    while value<F(1,1<<(k+1)):k+=1
    return k


def arithmetic_checks():
    bits=48
    values=[F(-3,2),F(-1,3),F(0),F(1,7),F(2),F(17,3)]
    boxes=[]
    for i,a in enumerate(values):
        for b in values[i:]:
            boxes.append((Interval(Interval.rational(a,bits).lo,
                                   Interval.rational(b,bits).hi,bits),a,b))
    operations=0
    for x,a,b in boxes:
        for y,c,d in boxes:
            added=x+y;multiplied=x*y
            for u in (a,(a+b)/2,b):
                for v in (c,(c+d)/2,d):
                    need(added.contains(u+v) and multiplied.contains(u*v),'rational interval arithmetic')
                    operations+=2
        if a>0:
            inv=x.reciprocal()
            need(inv.contains(1/a) and inv.contains(1/b),'positive interval reciprocal')
    # Independent positive exponential series, followed by rational inversion.
    exponentials=0
    for precision in (64,128):
        for x in (F(0),F(1,8),F(1,2),F(1),F(7),F(101)):
            box=exp_negative(Interval.rational(x,precision))
            total=term=F(1)
            n=0
            while True:
                n+=1;term*=x/n;total+=term
                following=term*x/(n+1)
                if n+2>x:
                    tail=following/(1-x/(n+2))
                    if tail<F(1,1<<(precision+32)):break
            need(F(box.lo,1<<precision)<=1/(total+tail) and
                 F(box.hi,1<<precision)>=1/total,'independent exponential enclosure')
            exponentials+=1
    p=pi_interval(256)
    need(F(333,106)<F(p.lo,1<<256)<=F(p.hi,1<<256)<F(355,113),'pi rational bounds')
    phases=0
    for k in (1,2,3,4,5,7,8,16,32):
        for j in range(k):
            z=root_of_unity(j,k,256)
            norm=z[0]*z[0]+z[1]*z[1]
            need(norm.contains(1),'unit phase norm')
            need(all(a.overlaps(b) for a,b in zip(cconj(z),root_of_unity(-j,k,256))),
                 'phase conjugation')
            phases+=1
    quantizations=0
    for a in range(-16,17):
        for b in range(-16,17):
            z=(Interval(a*256-3,a*256+5,20),Interval(b*256-5,b*256+3,20))
            q,error=inward_quantize(z,12)
            for u in (F(z[0].lo,1<<20),F(z[0].hi,1<<20)):
                for v in (F(z[1].lo,1<<20),F(z[1].hi,1<<20)):
                    need(abs(F(q[0],1<<12))<=abs(u) and abs(F(q[1],1<<12))<=abs(v),
                         'inward component magnitude')
                    need(abs(F(q[0],1<<12)-u)+abs(F(q[1],1<<12)-v)<=error,
                         'inward extraction error')
            quantizations+=1
    return {'rational_operations':operations,'exponential_brackets':exponentials,
            'phase_cases':phases,'quantization_boxes':quantizations}


def operator_checks(lines):
    entries=0;fixtures=0;operators=[];controls=[]
    for line in lines:
        bound,separated=line.certify_operator()
        need(separated==0,'Gaussian/Fourier enclosures overlap')
        entries+=line.s**2
        operators.append({'s':line.s,'t':line.t,'alpha':line.alpha,
                          'neumann_terms':line.neumann_terms,
                          'expansion_radius':line.expansion_radius,
                          'correction_cutoff':line.correction_cutoff,
                          'operator_error_lt_power_of_two':strict_power_bound(bound),
                          'uniform_rounding_error_lt_power_of_two':strict_power_bound(line.uniform_error)})
        columns=[line.direct_column(j) for j in range(line.s)]
        vectors=[[(0,0)]*line.s,
                 [(1<<(line.p-2),0)]*line.s,
                 [(((-1)**j)*(1<<(line.p-3)),((-1)**(j//2))*(1<<(line.p-4))) for j in range(line.s)],
                 [(j*37-91,53-j*31) for j in range(line.s)],
                 [((1<<(line.p-2))-j,j-13) for j in range(line.s)]]
        for vector in vectors:
            for opposite in (False,True):
                result,error=line.transform(vector,opposite)
                for i,z in enumerate(result):
                    expected=point(0,0,line.bits)
                    for j,value in enumerate(vector):
                        entry=columns[j][i]
                        if opposite:entry=cconj(entry)
                        expected=cadd(expected,cmul(entry,grid_point(value,line.p,line.bits)))
                    measured=grid_point(z,line.p,line.bits)
                    distance=sum((a-b).absolute_upper() for a,b in zip(measured,expected))
                    need(F(distance,1<<line.bits)<=error,'rounded source transform certificate')
                fixtures+=1
        for mutation in ('omit_target_permutation','wrong_selector','omit_correction','missing_rescale_bit'):
            # At the wider gaps the correction is below the p-bit error
            # budget; removing it is not a meaningful p-bit failure control.
            if mutation=='omit_correction' and line.s!=5:
                continue
            bad,witnesses=line.certify_operator(mutation)
            need(bad>F(1,1<<(line.p+8)) and witnesses>0,'operator mutation has a separated witness')
            controls.append({'operator':[line.s,line.t],'mutation':mutation,'separated_entries':witnesses})
    actual,cutoff=correction_matrix(2,3,2,448)
    omitted,_=correction_matrix(2,3,2,448,omit_winding=True)
    need(all(actual[i][i].lo>omitted[i][i].hi for i in range(2)),
         'nonzero winding terms survive periodic indexing')
    controls.append({'mutation':'omit_nonzero_periodic_windings','separated_entries':2,'cutoff':cutoff})
    return {'complete_matrix_entries':entries,'rounded_complex_vectors':fixtures,
            'operators':operators,'controls':controls}


def independent_coefficients(x,y,bits,size):
    radix=1<<bits
    a=[];b=[]
    while x:a.append(x%radix);x//=radix
    while y:b.append(y%radix);y//=radix
    answer=[0]*size
    for i,u in enumerate(a):
        for j,v in enumerate(b):answer[i+j]+=u*v
    return answer


def seeded_integer(label,bits):
    raw=b'';counter=0
    while len(raw)*8<bits:
        raw+=hashlib.sha256((label+':'+str(counter)).encode()).digest();counter+=1
    return int.from_bytes(raw,'big')&((1<<bits)-1)


def multiplication_checks(lines):
    records=[];line_calls=0;products=0;total_coefficients=0
    def check(x,y,used,digit_bits,input_bits):
        nonlocal line_calls,products,total_coefficients
        value,certificate=multiply(x,y,used,digit_bits,input_bits=input_bits)
        need(value==x*y,'independent Python integer product')
        coefficients=independent_coefficients(x,y,digit_bits,len(certificate['coefficients']))
        need(coefficients==certificate['coefficients'],'independent schoolbook coefficient convolution')
        need(len(certificate['output_bits'])==2*input_bits and int(certificate['output_bits'],2)==x*y,
             'leading-zero exact binary output')
        line_calls+=certificate['gaussian_line_executions']
        products+=certificate['pointwise_products'];total_coefficients+=len(coefficients)
        records.append({'input_bits':input_bits,'digit_bits':digit_bits,'shape':certificate['source_shape'],
                        'left_sha256':digest(hex(x)),'right_sha256':digest(hex(y)),
                        'output_sha256':hashlib.sha256(certificate['output_bits'].encode()).hexdigest(),
                        'coefficients_sha256':digest(coefficients)})
    for x in range(16):
        for y in range(16):check(x,y,lines[:1],4,4)
    for bits in (8,32,64,72):
        mask=(1<<bits)-1
        for x,y in ((0,mask),(1,mask),(mask,mask),
                    (seeded_integer('two-left',bits),seeded_integer('two-right',bits))):
            check(x,y,lines[:2],4,bits)
    for bits in (128,1024,4096,14592):
        mask=(1<<bits)-1
        for x,y in ((0,mask),(1,mask),(mask,mask),
                    (seeded_integer('three-left',bits),seeded_integer('three-right',bits))):
            check(x,y,lines,64,bits)
    alternative=[GaussianLine(s,t,4,128,320) for s,t in ((5,8),(7,16))]
    alternate_certificate=uniform_certificate(alternative,16)
    check((1<<288)-1,seeded_integer('alternative',288),alternative,16,288)
    controls=[]
    for mutation in ('omit_target_permutation','wrong_selector','missing_rescale_bit','missing_source_factor'):
        controls.append(rejected(lambda m=mutation:multiply(0x12345678,0x9abcdef0,lines[:2],4,mutation=m),mutation))
    weak=[GaussianLine(s,t,4,101,320) for s,t in ((5,8),(7,16),(13,32))]
    controls.append(rejected(lambda:uniform_certificate(weak,64),'insufficient_precision'))
    controls.append(rejected(lambda:multiply(1<<72,1,lines[:2],4),'cyclic_wrap_domain'))
    controls.append(rejected(lambda:GaussianLine(7,8,5,256,448),'original_theta_domain'))
    controls.append(rejected(lambda:GaussianLine(5,8,5,256,320),'insufficient_interval_guard'))
    return {'completed_integer_products':len(records),'input_bits_max':14592,
            'gaussian_line_executions':line_calls,'pointwise_products':products,
            'independently_checked_coefficients':total_coefficients,
            'case_manifest_sha256':digest(records),'controls':controls,
            'alternate_uniform_certificate':alternate_certificate}


def run():
    arithmetic=arithmetic_checks()
    lines=[GaussianLine(s,t,5,256,448) for s,t in ((5,8),(7,16),(13,32))]
    operators=operator_checks(lines)
    uniform=uniform_certificate(lines,64)
    radius=F(*uniform['error_radius'])
    need(radius<F(1,1<<49),'advertised uniform integer-recovery margin')
    uniform['error_radius_lt_power_of_two']=49
    products=multiplication_checks(lines)
    return {'schema_version':1,'status':'PASS_CERTIFIED_GAUSSIAN_RECOVERY',
            'arithmetic':arithmetic,'operators':operators,
            'uniform_certificate':uniform,'multiplication':products}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true',help='print fresh JSON without writing files')
    args=parser.parse_args()
    result=run()
    if args.emit:print(json.dumps(result,indent=2,sort_keys=True))
    else:
        expected=json.loads((PACKAGE/'RESULT.json').read_text())
        need(result==expected,'retained receipt mismatch')
        print(result['status'],'products='+str(result['multiplication']['completed_integer_products']),
              'input_bits_max=14592','uniform_error<2^-49','RECEIPT_MATCH')


if __name__=='__main__':main()
