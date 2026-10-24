"""Executed native Gaussian block via the chirp identity, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Decimal occurs only in the independent check.
"""
from pathlib import Path
from decimal import Decimal,localcontext
import json


def need(ok,why):
    if not ok:raise ValueError(why)


def module(name):
    p=Path(__file__).with_name(name)
    scope={'__name__':'gaussian_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),scope)
    return scope


def block(data,c,table,convolver,kernel):
    # Concrete all-length family a=1/16, u=v=1, integral c.
    # data coordinates use table.p fractional bits. Caller supplies paid tables.
    q=len(data);S=1<<table.p
    need(q>=1 and 4*q<=convolver.N and convolver.p==table.p,'block contract')
    def weight(numerator):return table.query(numerator,4)
    d=[weight(-2*x*x-2*c*x-c*c) for x in range(q)]
    e=[weight(-2*y*y+2*c*y) for y in range(q)]
    source=[convolver.cmul((e[y],0),data[y]) for y in range(q)][::-1]
    conv=convolver.apply(source,kernel,3*q-2)
    return [convolver.cmul((d[x],0),conv[x+q-1]) for x in range(q)]


def check():
    ExpTable=module('exp_table.py')['ExpTable']
    Convolver=module('native_convolution.py')['Convolver']
    table=ExpTable((1<<20)-1,8,8)
    cases=outputs=0;peak=0
    for q in (1,2,4,8):
        N=4*q;P=table.p;S=1<<P
        cv=Convolver(N,P,max(table.width,16*(P+16)+20))
        h=[(table.query(z*z,4),0) for z in range(2*q-1)]
        kernel=cv.prepare(h)
        data=[(((-1)**j*S)//(j+2),0) for j in range(q)]
        for c in (-1,0,1):
            got=block(data,c,table,cv,kernel)
            with localcontext() as ctx:
                ctx.prec=100
                for x,(real,imag) in enumerate(got):
                    exact=sum((-(Decimal(x-y+c)**2)/16).exp()*Decimal(data[y][0])/Decimal(S) for y in range(q))
                    need(abs(Decimal(real)/Decimal(S)-exact)<Decimal(2)**-60,'native Gaussian block real error')
                    need(abs(Decimal(imag)/Decimal(S))<Decimal(2)**-60,'native Gaussian block imaginary error')
                    outputs+=1
            cases+=1
        peak=max(peak,cv.maximum_bits,table.maximum_bits)
    return dict(status='PASS',native_blocks=cases,native_outputs=outputs,
                checked_tolerance_bits=60,maximum_bits=peak,
                root_exp_kernel_preparation_paid=True,TM_calls=0,
                scope='executed real-grid Gaussian block family; global blocking remains proof-level; periodic inverse is checked separately')


if __name__=='__main__':print(json.dumps(check(),indent=2))
