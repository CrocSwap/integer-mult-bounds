"""Actual periodic Gaussian N=C T D, native bounded-word model. Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Decimal appears only in independent residual checks.
"""
from pathlib import Path
from decimal import Decimal,localcontext
import json


def need(ok,why):
    if not ok:raise ValueError(why)


def module(name):
    p=Path(__file__).with_name(name);scope={'__name__':'gaussian_inverse_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),scope)
    return scope


def pi_grid(table):
    # Same paid Machin series/error argument as ROOTS-RECOVERY.md.
    S=table.S;v=table.val
    def atan(q):
        power=q;j=0;out=0
        while power<=S:
            term=v(S//v(power*(2*j+1)))
            out=v(out+term if j%2==0 else out-term)
            power=v(power*q*q);j+=1
        return out
    return v(16*atan(5)-4*atan(239))


def actual_matrix(s,t,alpha,h,table):
    need(s>2*h and t>s and alpha>=2,'Gaussian matrix domain')
    v=table.val;S=table.S;pi=pi_grid(table)
    v(s);v(t);v(alpha);den=v(s*s);alpha2=v(alpha*alpha)
    q=[v(v(v(2*v(t*i))+s)//v(2*s)) for i in range(s)]
    beta=[v(v(t*i)-v(s*q[i])) for i in range(s)]
    matrix=[]
    for i in range(s):
        row=[]
        for d in range(-h,h+1):
            j=(i+d)%s
            shifted=v(v(t*(i+d))-v(s*q[i]))
            difference=v(v(shifted*shifted)-v(beta[j]*beta[j]))
            argument=v(-v(v(pi*alpha2)*difference)//den)
            if argument < -table.C*table.ell*S:
                value=0 # explicit exp cutoff; caller's error budget includes its tail
            else:
                value=table.query(argument,table.P)
            row.append(value)
        matrix.append(row)
    return matrix


def check():
    ExpTable=module('exp_table.py')['ExpTable'];PeriodicSystem=module('periodic_solve.py')['PeriodicSystem']
    table=ExpTable((1<<20)-1,8,8);S=1<<table.p
    cases=rows=0;max_error=Decimal(0)
    with localcontext() as ctx:
        ctx.prec=120
        # Independent pi computation used only by this check.
        def atan(q):
            z=Decimal(q);power=z;j=0;out=Decimal(0)
            while True:
                term=1/(power*(2*j+1));out+=term if j%2==0 else -term
                if term<Decimal('1e-115'):return out
                power*=z*z;j+=1
        pi=16*atan(5)-4*atan(239)
        for s,t in ((13,14),(17,19),(25,27)):
            alpha=2;h=4
            a=actual_matrix(s,t,alpha,h,table)
            system=PeriodicSystem(a,h,table.p,table.width)
            rhs=[(((-1)**i)*S)//(i+2) for i in range(s)]
            out=system.solve(rhs)['solution']
            q=[(2*t*i+s)//(2*s) for i in range(s)]
            beta=[Decimal(t*i)/s-q[i] for i in range(s)]
            for i in range(s):
                total=Decimal(0)
                for j in range(s):
                    weight=sum((-pi*alpha*alpha*((Decimal(t)*(j+k*s)/s-q[i])**2-beta[j]**2)).exp() for k in range(-3,4))
                    total+=weight*Decimal(out[j])/Decimal(S)
                error=abs(total-Decimal(rhs[i])/Decimal(S))
                need(error<Decimal(2)**-100,'actual Gaussian inverse residual')
                max_error=max(max_error,error);rows+=1
            cases+=1
    return dict(status='PASS',actual_Gaussian_systems=cases,rows_checked=rows,
                maximum_reference_residual=str(max_error),checked_tolerance_bits=100,
                scope='actual positive Gaussian coefficient construction and periodic solve; independent finite Decimal sum is validation only',TM_calls=0)


if __name__=='__main__':print(json.dumps(check(),indent=2))
