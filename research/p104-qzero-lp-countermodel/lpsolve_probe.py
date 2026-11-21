#!/usr/bin/env python3
"""Use system lp_solve for discovery; certify its dual with exact fractions."""
import argparse
import ctypes
import json
from fractions import Fraction
from pathlib import Path
from lp_probe import data

def expr(coefficients, columns):
    terms=[]
    for coeff,(kind,index) in zip(coefficients,columns):
        if not coeff: continue
        f=float(coeff)
        terms.append(('+' if f>=0 else '-')+format(abs(f),'.17g')+' '+kind+str(index))
    return ' '.join(terms) if terms else '0'

def solve(k, tail, root):
    cols,eqnames,E,eb,names,A,b,c=data(k,tail)
    lp=['max: '+expr(c,cols)+';']
    for name,row,rhs in zip(eqnames,E,eb): lp.append(name+': '+expr(row,cols)+' = '+str(rhs)+';')
    for name,row,rhs in zip(names,A,b): lp.append(name+': '+expr(row,cols)+' <= '+str(rhs)+';')
    path=root/('k%d%s.lp'%(k,'' if tail else '_no_tails')); path.write_text('\n'.join(lp)+'\n')
    D=ctypes.CDLL('/usr/lib/lp_solve/liblpsolve55.so')
    P=ctypes.c_void_p; I=ctypes.c_int; S=ctypes.c_char_p; F=ctypes.c_double
    for name,args,ret in [('read_LP',[S,I,S],P),('get_Nrows',[P],I),('get_Ncolumns',[P],I),
                          ('solve',[P],I),('get_objective',[P],F),('get_dual_solution',[P,ctypes.POINTER(F)],ctypes.c_ubyte),
                          ('get_variables',[P,ctypes.POINTER(F)],ctypes.c_ubyte),('delete_lp',[P],None)]:
        f=getattr(D,name); f.argtypes=args; f.restype=ret
    p=D.read_LP(str(path).encode(),1,b'')
    if not p: raise RuntimeError('failed to parse LP')
    nr=D.get_Nrows(p); nc=D.get_Ncolumns(p)
    assert nr==len(E)+len(A) and nc==len(cols),(nr,nc)
    status=D.solve(p); print('k',k,'solver status',status,flush=True)
    if status != 0: D.delete_lp(p); return {'k':k,'success':False,'status':status}
    val=D.get_objective(p)
    arr=(F*(1+nr+nc))(); assert D.get_dual_solution(p,arr)
    primal=(F*nc)(); assert D.get_variables(p,primal)
    z=[Fraction(round(arr[1+i]*10**12),10**12) for i in range(len(E))]
    y=[Fraction(max(0,round(arr[1+len(E)+i]*10**12)),10**12) for i in range(len(A))]
    D.delete_lp(p)
    def slack(j): return sum(y[i]*A[i][j] for i in range(len(y))) + sum(z[i]*E[i][j] for i in range(2)) - c[j]
    repair_e=max([Fraction(0)]+[-slack(j)/d for j,(t,d) in enumerate(cols) if t=='e'])
    z[1]-=repair_e
    repair_r=max([Fraction(0)]+[-slack(j) for j,(t,d) in enumerate(cols) if t=='r'])
    z[0]+=repair_r
    slacks=[slack(j) for j in range(len(cols))]
    assert all(v>=0 for v in y) and all(v>=0 for v in slacks)
    raw=sum(y[i]*b[i] for i in range(len(y)))+sum(z[i]*eb[i] for i in range(2))
    bound=Fraction(104,k)*raw
    out={'k':k,'tails':tail,'success':True,'numerical_value':val*104/k,'certified_bound':str(bound),
         'certified_decimal':float(bound),'strictly_below_bar':bound<Fraction(128891,1000),
         'dual_eq':{eqnames[i]:str(v) for i,v in enumerate(z)},
         'dual_nonzero':[{ 'name':names[i],'weight':str(v),'rhs':b[i]} for i,v in enumerate(y) if v],
         'repairs':{'event':str(repair_e),'role':str(repair_r)},'min_slack':str(min(slacks)),
         'primal_numerical_nonzero':[{'column':str(cols[i]),'value':v} for i,v in enumerate(primal) if v>1e-7],
         'source':'necessary event relaxation from #7852; this is not the original certificate'}
    outfile=root/('k%d%s.json'%(k,'' if tail else '_no_tails'));outfile.write_text(json.dumps(out,indent=2)+'\n')
    print('k',k,'bound',float(bound),'strict',out['strictly_below_bar'],flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('k',type=int,nargs='+');ap.add_argument('--no-tails',action='store_true');a=ap.parse_args()
    for k in a.k: solve(k,not a.no_tails,Path(__file__).resolve().parent)
