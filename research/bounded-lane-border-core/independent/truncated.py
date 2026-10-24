#!/usr/bin/env python3
"""Independent truncated-input border review. Apache-2.0.
Yiyang (@Lyy-iiis), substantial OpenAI Codex parallel-agent assistance.
Imports only this reviewer's own exact matrix implementation, no primary code.
"""
import importlib.util
from pathlib import Path
import json
spec=importlib.util.spec_from_file_location('review_matrix',Path(__file__).with_name('check.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
F=m.F

def rect(rows,cols):return [[F(0) for _ in range(cols)] for _ in range(rows)]
def compression(a,w):return [r[:-w] for r in a[:-w]]
def Pmatrix(n,w):
    p=rect(n-w,n)
    for j in range(n-w):p[j][j]=1
    return p

def Eminus(a,w,inverse=False):
    n=len(a);b=m.inv(a);p=Pmatrix(n,w)
    upper=b if inverse else a
    cross=m.mul(p,m.sub(b,m.eye(n))) if inverse else m.mul(p,m.sub(m.eye(n),b))
    lower=compression(a if inverse else b,w)
    return [row+[F(0)]*(n-w) for row in upper]+[row1+row2 for row1,row2 in zip(cross,lower)]

def physical(a,w,inverse=False):
    n=len(a);c=m.inv(m.core(a)) if inverse else m.core(a)
    size=2*n-w;ans=rect(size,size);dirty=0
    for col in range(size):
        inp=[F(i==col) for i in range(size)]
        x=inp[:n];y=inp[n:];owned=[F(0)]*w
        data=x+y+owned
        out=[sum((u*v for u,v in zip(row,data)),F(0)) for row in c]
        retained=out[:-w];terminal=out[-w:]
        dirty+=any(terminal)
        terminal=[F(0)]*w
        m.need(not any(terminal),'owned terminal clear')
        for i,v in enumerate(retained):ans[i][col]=v
    return ans,dirty

def grade_check(a,L,w):
    # Flat X block precedes Y block. Y input/output block k is physical grade k+1.
    grades=[j for j in range(L) for _ in range(w)]+[j for j in range(1,L) for _ in range(w)]
    for i,row in enumerate(a):
        for j,v in enumerate(row):
            if v:m.need(grades[i]>=grades[j],'negative output grade')

def main():
    q=[[F(1),F(1)],[F(1),F(2)]];r=[[F(1),F(0)],[F(2),F(1)]]
    result={'scope':'Independently declared truncated productive contract; no Y0 provider; not fixed recursive inventory','cases':[]}
    for L in range(2,6):
        w=2;n=L*w;a=m.constant_diagonal(L,q,100+L);b=m.inv(a);c=m.constant_diagonal(L,r,200+L);p=Pmatrix(n,w)
        m.need(compression(m.mul(a,c),w)==m.mul(compression(a,w),compression(c,w)),'compression homomorphism')
        m.need(m.mul(compression(a,w),p)==m.mul(p,a),'compression intertwiner')
        e=Eminus(a,w);f=Eminus(a,w,True);size=2*n-w
        m.need(m.mul(e,f)==m.eye(size) and m.mul(f,e)==m.eye(size),'both inverse orders')
        pe,d=physical(a,w);pf,di=physical(a,w,True)
        m.need(pe==e and pf==f,'literal endpoint with no missing productive input')
        grade_check(e,L,w);grade_check(f,L,w)
        m.need(Eminus(b,w)!=f,'nominal opposite not actual inverse')
        # Adding an arbitrary unprocessed Y0 is a different and incorrect contract.
        wrong=m.block(e,m.zero(size,w),m.zero(w,size),m.eye(w))
        wanted=m.block(e,m.zero(size,w),m.zero(w,size),m.inv(q))
        m.need(wrong!=wanted,'extra arbitrary Y0 cannot get free transform credit')
        result['cases'].append({'lanes':L,'payload_width':w,'declared_input_columns':size,'owned_terminal_columns':w,'both_inverse_orders':True,'literal_forward_inverse':True,'graded_endpoint':True,'nonzero_terminal_clears':[d,di]})
    print(json.dumps(result,indent=2))
    print('PASS_INDEPENDENT_TRUNCATED_LANE_REVIEW')
if __name__=='__main__':main()
