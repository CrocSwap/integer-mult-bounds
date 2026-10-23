#!/usr/bin/env python3
"""Independent literal-data parser and exact all-column scalar check.
No supplied source is imported, compiled, evaluated, or executed.
"""
from pathlib import Path
import hashlib
import argparse
import json
import math
import re
import time

if not __debug__:
    raise RuntimeError('Run without Python -O: assertions are part of this exact checker.')

HERE=Path(__file__).resolve().parent
PIN='f010392c923279e3dd59ef3aa5fedad23affc5fd'

class LiteralParser:
    def __init__(self,text,defs):
        token=re.compile(r'\s*(\.out|\.inn|\+\+|[A-Za-z_][A-Za-z_0-9]*|\d+|[\[\](),])')
        self.tokens=[];pos=0
        while pos<len(text):
            m=token.match(text,pos)
            assert m, ('unsupported literal syntax',text[pos:pos+80])
            self.tokens.append(m[1]);pos=m.end()
        self.i=0;self.defs=defs
    def pop(self,expected=None):
        t=self.tokens[self.i];self.i+=1
        assert expected is None or t==expected,(expected,t)
        return t
    def peek(self):return self.tokens[self.i] if self.i<len(self.tokens) else None
    def expr(self):
        result=self.atom()
        if self.peek()=='++':
            self.pop();right=self.expr();assert isinstance(result,list) and isinstance(right,list)
            result=result+right
        return result
    def atom(self):
        t=self.pop()
        if t.isdigit():return int(t)
        if t=='[':
            out=[]
            while self.peek()!=']':
                out.append(self.expr())
                if self.peek()==',':self.pop()
                else:break
            self.pop(']');return out
        if t=='(':
            out=self.expr()
            if self.peek()==',':
                self.pop();second=self.expr();self.pop(')');return (out,second)
            self.pop(')');return out
        if t in ('.out','.inn'):
            frame=self.atom();reg=self.atom();pairs=self.atom()
            extras=self.atom() if t=='.out' else []
            assert isinstance(frame,int) and isinstance(reg,int) and isinstance(pairs,list)
            assert isinstance(extras,list) and all(isinstance(x,int) for x in extras)
            return (t,frame,reg,pairs,extras)
        assert t in self.defs,('unbound literal reference',t)
        return self.defs[t]
    def parse(self):
        out=self.expr();assert self.i==len(self.tokens);return out

def parse_data(ROOT):
    defs={};used=[]
    records={r['path']:r for r in json.loads((HERE/'source-bindings.json').read_text())}
    paths=list(records)
    for name in paths:
        data=(ROOT/name).read_bytes();r=records[name]
        sha=hashlib.sha256(data).hexdigest();blob=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        assert r['commit']==PIN and len(data)==r['bytes']
        assert sha==r['sha256'] and blob==r['git_blob_sha1'], ('source hash mismatch',name)
        used.append({'path':name,'commit':PIN,'sha256':sha,'git_blob_sha1':blob,'bytes':len(data)})
    raw=(ROOT/paths[0]).read_text()
    params={name:int(re.search(r'\b'+name+r' := (\d+)',raw)[1]) for name in ('h','v','R')}
    for field,value in [('ports','ports'),('ret','ret'),('scat','scat'),('A','gA'),('B','gB')]:
        assert re.search(r'\b'+field+r' := '+value+r'\b',raw)
    for i in range(2,8):
        later=(ROOT/f'Work/GCert/Data/Gen/P193/S{i}.lean').read_text()
        assert not re.search(r'\bdef (k\d+|ports(?:_\d+)?|ret(?:_\d+)?|scat|gA|gB|seg[0-4](?:_\d+)?)\s*:',later)
    for part in ('S0','S1'):
        lines=(ROOT/f'Work/GCert/Data/Gen/P193/{part}.lean').read_text().splitlines()
        for line_no,line in enumerate(lines,1):
            coef=re.fullmatch(r'noncomputable def (k\d+) : Co := ⟨(false|true), (\d+), (\d+)⟩',line)
            if coef:
                name,neg,num,den=coef.groups();num=int(num)*(-1 if neg=='true' else 1);den=int(den)
                assert den>0 and name not in defs;defs[name]=(num,den);continue
            m=re.fullmatch(r'noncomputable def ((?:ports|ret)(?:_\d+)?|seg[0-4](?:_\d+)?|gA|gB) : .*? := (.*)',line)
            if m:
                name,expr=m.groups();assert name not in defs
                defs[name]=LiteralParser(expr,defs).parse()
            if line.startswith('noncomputable def scat :'):
                m=re.fullmatch(r'noncomputable def scat : Scat := \.star (k\d+) (k\d+)',line)
                assert m;defs['scatter_inside']=defs[m[1]];defs['scatter_outside']=defs[m[2]]
    v=params['v'];h=params['h'];nr=2*v+params['R']
    assert len(defs['ports'])==v and len(defs['ret'])==h
    assert all(2*v<=r<nr for r,_ in defs['ret'])
    def flatten(chunks):
        ops=[]
        for chunk in chunks:
            for kind,frame,reg,pairs,extras in chunk:
                for other,(n,d) in pairs:
                    t,s=(other,reg) if kind=='.out' else (reg,other)
                    assert 0<=t<nr and 0<=s<nr and t!=s and d>0
                    ops.append((t,s,n,d))
        return ops
    a=flatten(defs['gA']);b=flatten(defs['gB'])
    scatter=[]
    for t,p in enumerate(defs['ports']):
        for k in range(h-1,-1,-1):
            n,d=defs['scatter_inside'] if (p>>k)&1 else defs['scatter_outside']
            scatter.append((v+t,defs['ret'][k][0],n,d))
    assert all(t>=2*v and (s<v or s>=2*v) for t,s,n,d in a)
    assert all((t>=v or s<v) and (not v<=s<2*v or v<=t<2*v) for t,s,n,d in b)
    return params,defs,a,scatter,b,used

def plan_bounds(program,nr,source_first,v):
    # A row denotes a polynomial in formal input columns over Q. D is a
    # common denominator and L bounds the numerator coefficient l1 norm.
    D=[1]*nr;L=[0]*nr
    for j in range(source_first,source_first+v):L[j]=1
    plan=[];largest=1;largest_d=1
    for t,s,n,d in program:
        if L[s]==0 or n==0:continue
        newD=math.lcm(D[t],D[s]*d)
        u=newD//D[t];z=n*(newD//(D[s]*d))
        L[t]=u*L[t]+abs(z)*L[s];D[t]=newD
        plan.append((t,s,u,z))
        largest=max(largest,L[t]);largest_d=max(largest_d,newD)
    # Every coefficient of output minus expected has absolute value < base.
    bits=(largest+largest_d).bit_length()+1
    assert 1<<bits > largest+largest_d
    return plan,D,L,bits,{'max_numerator_l1_bound':str(largest),'max_denominator':str(largest_d),'radix_bits':bits,'plan_steps':len(plan)}

def exact_columns(program,nr,v,source_first,targets,batch=96):
    plan,D,L,bits,bounds=plan_bounds(program,nr,source_first,v)
    assert bits<=4096,('unexpected coefficient-bound growth',bits)
    for lo in range(0,v,batch):
        hi=min(v,lo+batch);rows=[0]*nr
        for t in range(lo,hi):rows[source_first+t]=1<<(bits*(t-lo))
        for t,s,u,z in plan:rows[t]=u*rows[t]+z*rows[s]
        for offset in targets:
            for t in range(v):
                expected=D[offset+t]*(1<<(bits*(t-lo))) if lo<=t<hi else 0
                if rows[offset+t]!=expected:
                    delta=rows[offset+t]-expected
                    for col in range(lo,hi):
                        base=1<<bits;digit=delta%base
                        if digit>base//2:digit-=base
                        if digit:
                            return False,{'output_register':offset+t,'input_register':source_first+col,
                                          'difference_numerator':str(digit),'denominator':str(D[offset+t]),'bounds':bounds}
                        delta=(delta-digit)//base
                    return False,{'undecoded_difference':True,'bounds':bounds}
    return True,bounds

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--source-root',required=True,type=Path,help='Existing pinned upstream source tree; read only, never downloaded')
    args=cli.parse_args()
    start=time.monotonic();params,defs,a,scatter,b,inputs=parse_data(args.source_root)
    v=params['v'];nr=2*v+params['R'];program=a+scatter+b
    print(json.dumps({'phase':'parsed','params':params,'adds_A':len(a),'adds_scatter':len(scatter),'adds_B':len(b)}),flush=True)
    xok,x=exact_columns(program,nr,v,0,[0,v]);assert xok,x
    print(json.dumps({'phase':'x_columns','status':'PASS','bounds':x}),flush=True)
    # Under the proven direction restrictions, only y-to-y B gates affect
    # y columns; the complete raw replay below also verifies that fact.
    yok,y=exact_columns(program,nr,v,v,[v]);assert yok,y
    assert all((not v<=s<2*v) or v<=t<2*v for t,s,n,d in program)
    print(json.dumps({'phase':'y_columns','status':'PASS','bounds':y}),flush=True)
    controls=[]
    for name,altered in [('omit_first_A',program[1:]),('flip_first_A',[(a[0][0],a[0][1],-a[0][2],a[0][3])]+program[1:])]:
        ok,witness=exact_columns(altered,nr,v,0,[0,v]);assert not ok,name
        controls.append({'name':name,'rejected':True,'witness':witness})
    # Serialization is data only, useful for inspecting a small prefix.
    digest=hashlib.sha256(json.dumps(program,separators=(',',':')).encode()).hexdigest()
    result={'status':'PASS_INDEPENDENT_EXACT_SCALAR_CHECK','upstream_pin':PIN,'parameters':params,
       'live_registers':nr,'retained_copies':len(defs['ret']),
       'adds':{'A':len(a),'scatter':len(scatter),'B':len(b),'total':len(program)},
       'normalized_program_sha256':digest,'all_x_columns':v,'all_y_columns':v,
       'x_column_bounds':x,'y_column_bounds':y,'negative_controls':controls,
       'five_identities':{'hAi':'distinct-register elementary additions; inverse reverses order and negates coefficients',
         'hBi':'same structural proof for phase B','hx':'all x-to-x columns checked; no non-x influence into x by direction closure',
         'hy':'all y-to-y columns checked; no y influence into non-y by direction closure',
         'hid':'every one of v squared target/source coefficients checked by exact bounded radix encoding'},
       'not_verified':['Lean P193 source elaboration','geometry','labels','cost','all-size compiler','E8 instance'],
       'elapsed_seconds':round(time.monotonic()-start,3)}
    result.pop('elapsed_seconds')
    expected=json.loads((HERE/'certificate.json').read_text())
    assert result==expected, ('certificate mismatch',result)
    print(json.dumps({'status':'PASS','source_files_hashed':len(inputs),'certificate_matches':True,'negative_controls':len(controls),'lean_certified':False}),flush=True)

if __name__=='__main__':main()
