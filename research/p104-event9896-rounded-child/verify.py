"""Verify the actual event9896 width-one rounded child; no whole supplier claim."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
c = types.ModuleType('event9896_owned_child')
c.__file__ = str(HERE/'child.py')
exec(compile((HERE/'child.py').read_bytes(),c.__file__,'exec',optimize=0),c.__dict__)


def typed(value):
    c.need(type(value) in (dict,list,str,int,type(None)),'typed JSON receipt')
    if isinstance(value,dict):
        c.need(all(type(k) is str for k in value),'string receipt keys')
        for child in value.values():
            typed(child)
    elif isinstance(value,list):
        for child in value:
            typed(child)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def exact_numerators(coarse):
    out = []
    for z,(a,b) in enumerate(coarse):
        u,v = coarse[z^21]
        eta = -1 if ((z&5).bit_count()&1) else 1
        out.append((a-b+eta*(u+v),a+b+eta*(v-u)))
    return out


def fixture_inputs(plan):
    zero = [[0,0] for _ in range(512)]
    sharp = [[0,0] for _ in range(512)]
    for x in range(512):
        if x&1 == 0:
            y = c.address(plan['G'],x)
            sharp[y] = list(c.rotate((1,0),c.quadratic(plan['Q'],plan['alpha'],y)))
    yield 'zero',14,zero
    yield 'sharp',14,sharp
    for p in (14,15,31,127):
        scale = 1<<(p-10)
        values = [[((37*j+11)%31-15)*scale,((23*j+7)%29-14)*scale] for j in range(512)]
        yield 'signed-'+str(p),p,values


def run_fixture(name,p,coarse,plan,kernel):
    # Each fixture is itself a legal initial236, with initial720=0.
    c.need(sum(a*a+b*b for a,b in coarse) <= (1<<p)**2,'valid unquantized initial-field fixture')
    fine = [[a*32,b*32] for a,b in coarse]
    D,invoice = c.execute(fine,p,plan,kernel)
    c.need(D is fine,'actual destination field updated in place')
    exact = exact_numerators(coarse)
    error = F(sum((2*(a//32)-u)**2+(2*(b//32)-v)**2
                  for (a,b),(u,v) in zip(D,exact)),4)
    c.need(error <= 256,'completed field defect <=16h')
    c.need(all(v%32 == 0 for z in D for v in z),'coarse-grid returned fine records')
    c.need(invoice['kernel']['butterflies'] == 256,'one256-pair layer')
    c.need(invoice['monomial_passes'] == 2,'both monomial passes charged')
    back = [list(z) for z in D]
    inverse,back_invoice = c.execute(back,p,plan,kernel,True)
    original = [[a*32,b*32] for a,b in coarse]
    c.need([list(z) for z in inverse] == original,'literal rounded inverse restores actual fine records')
    return {'name':name,'p':p,'fine_input':original,'fine_output':[list(z) for z in D],
            'swap_scratch':invoice['swap_scratch_final'],'inplace_object_preserved':'yes',
            'rounded_inverse_return':'exact','error_squared':{'numerator':error.numerator,'denominator':error.denominator},
            'invoice':invoice}


def reject(call,label):
    try:
        call()
    except ValueError as exc:
        return {'name':label,'rejected_by':str(exc)}
    raise ValueError('control not rejected: '+label)


def controls(plan,kernel,fixtures):
    nonzero = fixtures[-1]
    fine = [list(z) for z in nonzero['fine_input']]
    bad = [list(z) for z in fine]
    bad[0][0] += 1
    out = [reject(lambda:c.execute(bad,127,plan,kernel),'misaligned incoming fine code'),
           reject(lambda:c.execute([[32,0] for _ in range(512)],127,plan,kernel,fault='omit-final-swap'),'omitted final cycle scratch swap')]
    bad = [[0,0] for _ in range(512)]
    bad[0][0] = 32*(4*(1<<14))
    out.append(reject(lambda:c.execute(bad,14,plan,kernel),'outside actual entrance norm'))
    even = [[0,0] for _ in range(512)]
    even[1] = [64*32,0]
    reference,_ = c.execute([list(z) for z in even],14,plan,kernel)
    reference = [list(z) for z in reference]
    altered = c.strict(json.dumps(plan))
    altered['routes']['phase_K'] = [(phase+2)%4 for phase in altered['routes']['phase_K']]
    for name,program,adjoint,fault in [('wrong physical phase',altered,False,None),
                                      ('inverse Gaussian sign',plan,True,None),
                                      ('omitted source monomial',plan,False,'omit-K')]:
        actual,_ = c.execute([list(z) for z in even],14,program,kernel,adjoint,fault)
        target = exact_numerators([[v//32 for v in z] for z in even])
        error = F(sum((2*(a//32)-u)**2+(2*(b//32)-v)**2 for (a,b),(u,v) in zip(actual,target)),4)
        c.need(error > 256,'actual numerical mutation violates completed defect bound')
        index = next(i for i in range(512) if list(actual[i]) != reference[i])
        out.append({'name':name,'input':1,'coarse_amplitude':64,'p':14,'output':index,
                    'expected':reference[index],'actual':list(actual[index]),'error_squared':str(error)})
    return out


def build():
    files = c.authenticate()
    plan = c.get_plan()
    kernel = c.load_source('inputs/kernel.py','event9896_frozen_kernel',files)
    fixtures = [run_fixture(name,p,values,plan,kernel) for name,p,values in fixture_inputs(plan)]
    sharp = next(row for row in fixtures if row['name'] == 'sharp')
    c.need(sharp['error_squared'] == {'numerator':256,'denominator':1},'sharp256-pair error fixture')
    c.need(sharp['invoice']['kernel']['nonzero_roundings'] > 0,'genuine nonzero rounding')
    return {'schema_version':1,'source_manifest_sha256':c.MANIFEST,
            'source_binding':plan,'dimension':512,'tensor_width':1,
            'p':'t+14','coarse_grid':'h=B*2^-p','fine_grid':'h/32',
            'completed_error':'at most16h = B*2^-(t+10)',
            'fixtures':fixtures,'controls':controls(plan,kernel,fixtures),
            'limits':['width one only','one actual destination field updated in place; zero extra field banks',
                      'indexed arithmetic cleanup model for pair temporaries; no reversible bit circuit',
                      'no fixed tape, accelerated tariff, complete caller, physical supplier or new kappa']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = build()
    typed(result)
    if args.emit:
        print(encoded(result).decode(),end='')
    else:
        retained = c.strict((HERE/'RESULT.json').read_bytes())
        typed(retained)
        c.need(retained == result,'strict retained RESULT')
        print('PASS_P104_EVENT9896_ROUNDED_CHILD')


if __name__ == '__main__':
    main()
