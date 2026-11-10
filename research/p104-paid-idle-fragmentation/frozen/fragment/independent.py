"""Independent exact caller audit, requiring only the standard library.

Binary suppliers and the dual-pair retirement method retain the authors
and credits recorded in source6702 and PR6545.  The paid fragmentation, changed root and their
literal word are independently checked here using a separately written
Fraction Laurent-ring engine.  No author constructor, replay, algebra,
native implementation, or saved mathematical result is imported.
OpenAI Codex assistance. Apache-2.0.

Every fresh stage remains a distinct formal variable; only q^4=1 is
imposed. This does not replace native absolute-phase or physical checks,
discharge framework assumptions, or establish scientific admission.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ZERO = F(0), F(0)
ONE = F(1), F(0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def plus(a, b, factor=ONE):
    out = dict(a)
    for monomial, coefficient in b.items():
        z = complex_product(coefficient, factor)
        old = out.get(monomial, ZERO)
        z = old[0] + z[0], old[1] + z[1]
        if z == ZERO:
            out.pop(monomial, None)
        else:
            out[monomial] = z
    return out


def scale(a, scalar):
    scalar = F(scalar)
    return {k: complex_product(v, (scalar, F(0))) for k, v in a.items()} if scalar else {}


def shift(a, q=0, stages=(), degree=1):
    out = {}
    for monomial, coefficient in a.items():
        key = list(monomial)
        key[0] = (key[0] + q) % 4
        for stage in stages:
            key[stage] += degree
        out = plus(out, {tuple(key): coefficient})
    return out


def lam(a, sign):
    need(sign in (-1, 1), 'Literal normalization sign')
    return plus(plus({}, a, (F(1, 2), F(sign, 2))),
                shift(a, q=2), (F(1, 2), F(-sign, 2)))


def normalized_central(a):
    return lam(shift(a, q=-1), 1)


def forward(vector, event):
    op = event[0]
    if op == 'ADD':
        vector[event[1]] = plus(vector[event[1]], vector[event[2]], (F(event[3]), F(0)))
    elif op == 'SWAP':
        vector[event[1]], vector[event[2]] = vector[event[2]], vector[event[1]]
    elif op == 'SCALE':
        vector[event[1]] = scale(vector[event[1]], event[2])
    elif op == 'LAMBDA':
        vector[event[1]] = lam(vector[event[1]], event[2])
    elif op == 'Q_POWER':
        vector[event[1]] = shift(vector[event[1]], q=event[2])
    elif op == 'QUERY':
        vector[event[1]] = plus(vector[event[1]], shift(vector[event[2]], q=event[3]))
    elif op == 'LOCAL':
        _, stage, src, dst = event
        vector[dst] = plus(vector[dst], shift(vector[src], q=-1))
        for owner in (src, dst):
            vector[owner] = shift(vector[owner], stages=[stage])
    elif op in ('IDLE', 'IDLE_ONE'):
        owners, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
        need(len(stages) == len(set(stages)), 'Distinct actual idle axes')
        for owner in owners:
            vector[owner] = shift(vector[owner], stages=stages)
    else:
        raise ValueError('Unknown event ' + op)


def right_action(row, event):
    """Right multiplication by a forward event; never an inverse oracle."""
    op = event[0]
    if op == 'ADD':
        row[event[2]] = plus(row[event[2]], row[event[1]], (F(event[3]), F(0)))
    elif op == 'SWAP':
        row[event[1]], row[event[2]] = row[event[2]], row[event[1]]
    elif op == 'SCALE':
        row[event[1]] = scale(row[event[1]], event[2])
    elif op == 'LAMBDA':
        row[event[1]] = lam(row[event[1]], event[2])
    elif op == 'Q_POWER':
        row[event[1]] = shift(row[event[1]], q=event[2])
    elif op == 'QUERY':
        row[event[2]] = plus(row[event[2]], shift(row[event[1]], q=event[3]))
    elif op == 'LOCAL':
        _, stage, src, dst = event
        for owner in (src, dst):
            row[owner] = shift(row[owner], stages=[stage])
        row[src] = plus(row[src], shift(row[dst], q=-1))
    elif op in ('IDLE', 'IDLE_ONE'):
        owners, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
        need(len(stages) == len(set(stages)), 'Distinct actual idle axes')
        for owner in owners:
            row[owner] = shift(row[owner], stages=stages)
    else:
        raise ValueError('Unknown event ' + op)


def vector(n, one, entries):
    out = [{} for _ in range(n)]
    for role, coefficient in entries.items():
        out[role] = scale(one, coefficient)
    return out


def dot(left, right):
    out = {}
    for a, b in zip(left, right):
        for monomial, coefficient in a.items():
            term = shift(b, q=monomial[0])
            for stage, degree in enumerate(monomial[1:], 1):
                if degree:
                    term = shift(term, stages=[stage], degree=degree)
            out = plus(out, term, coefficient)
    return out


def check_body_pair(base,witness):
    n=base['roles'];one={(0,)*(base['stages']+1):ONE}
    c=vector(n,one,{6:F(-1,8),7:F(45,16)})
    d=vector(n,one,{6:37,7:2})
    a=vector(n,one,{0:F(-1,16),2:1})
    b=vector(n,one,{1:-16,2:1})
    need(dot(d,c)==dot(b,a)==one,'Both exact dyadic dual pairings equal one')
    cut=witness['cut_after'];need(cut==122 and base['events'][cut]==['IDLE_ONE',2,[5,6]],'Actual paid B cut')
    col=deepcopy(c)
    for e in base['events'][:cut+1]:forward(col,e)
    need(col==[shift(p,stages=[5,6])for p in a],'Actual prefix P c = D_B a')
    row=deepcopy(b)
    for e in reversed(base['events'][:cut+1]):right_action(row,e)
    need(row==[shift(p,stages=[5,6])for p in d],'Actual prefix b P = D_B d')
    e6=vector(n,one,{6:1});col=deepcopy(e6)
    for e in witness['prefix_basis']:forward(col,e)
    need(col==c,'Literal input basis column')
    # Its inverse is checked by exact operations, with no odd inversions.
    inv=[]
    for e in reversed(witness['prefix_basis']):
        e=deepcopy(e)
        if e[0]=='ADD':e[-1]=str(-F(e[-1]))
        elif e[0]=='SCALE':e[-1]=str(1/F(e[-1]))
        inv.append(e)
    row=deepcopy(e6)
    for e in reversed(inv):right_action(row,e)
    need(row==d,'Literal input inverse row')
    col=deepcopy(a)
    for e in witness['cut_basis']:forward(col,e)
    need(col==e6,'Literal cut basis column')
    row=deepcopy(e6)
    for e in reversed(witness['cut_basis']):right_action(row,e)
    need(row==b,'Literal cut basis row')
    return{'cut_after':cut,'input_pairing':'1','cut_pairing':'1','column':'P c = D_B a','row':'b P = D_B d','ordinary_ring':'Z[1/2]','prefix_stages':[5,6],'suffix_stages':[7,8,9]}

def check_d_pair(body,witness):
    n=body['roles'];one={(0,)*(body['stages']+1):ONE}
    entries={'a':{1:1,20:-1,21:1},'b':{0:-2,2:2,20:-2,21:-1},'c':{20:1,4:-1},'d':{4:-1,21:-1}}
    a,b,c,d=[vector(n,one,entries[k])for k in('a','b','c','d')]
    need(dot(a,b)==dot(c,d)==one,'Retained D dual pairings')
    cut=witness['cut_after'];need(cut==374 and body['events'][cut]==['LAMBDA',20,1],'Actual retained D cut')
    col=deepcopy(d)
    for e in body['events'][:cut+1]:forward(col,e)
    need(col==[normalized_central(p)for p in b],'Retained P d = S b')
    row=deepcopy(a)
    for e in reversed(body['events'][:cut+1]):right_action(row,e)
    need(row==[normalized_central(p)for p in c],'Retained a P = S c')
    return{'cut_after':cut,'prefix_column':'P d = S b','prefix_row':'a P = S c'}

def check_word(word):
    n=word['roles'];one={(0,)*(word['stages']+1):ONE}
    need((n,word['stages'],len(word['events']))==(36,18,610),'Exact complete input and event census')
    need(all(t[1]==0 for t in word['diagonal']),'No untested stage zero')
    need(sorted(e[1]for e in word['events']if e[0]=='LOCAL')==list(range(1,19)),'Every fresh native stage once')
    for source in range(n):
        x=vector(n,one,{source:1})
        for e in word['events']:forward(x,e)
        d=word['diagonal'][source];expected=[{}for _ in range(n)];expected[source]={(d[0]%4,*d[2:]):ONE}
        need(x==expected,'Independent full forward column '+str(source))
    for target in range(n):
        row=vector(n,one,{target:1})
        for e in reversed(word['events']):right_action(row,e)
        d=word['diagonal'][target];expected=[{}for _ in range(n)];expected[target]={(d[0]%4,*d[2:]):ONE}
        need(row==expected,'Independent full reverse row '+str(target))
    return{'inputs':n,'forward_coefficients':n*n,'reverse_coefficients':n*n,'events':610,'independent_body_variables':18}

def rejected(f):
    try:f()
    except ValueError as e:return str(e)
    raise ValueError('Invalid control accepted')

def run():
    paths=[HERE/name for name in('CALLER-UNRETIRED.json','CALLER-BODY-RETIRED.json','CONTROLLER.json','RETIREMENT-WITNESSES.json')]
    base,body,word,witness=[json.loads(p.read_bytes())for p in paths]
    bpair=check_body_pair(base,witness[0]);dpair=check_d_pair(body,witness[1]);whole=check_word(word)
    controls={}
    for op in('LOCAL','QUERY','IDLE','IDLE_ONE','LAMBDA','ADD'):
        bad=deepcopy(word);j=next(i for i,e in enumerate(bad['events'])if e[0]==op);bad['events'][j]=['SCALE',0,'1']
        controls['omitted_'+op]=rejected(lambda bad=bad:check_word(bad))
    bad=deepcopy(base);bad['events'][122][-1]=[7,8,9]
    controls['wrong_fragment_axes']=rejected(lambda:check_body_pair(bad,witness[0]))
    for role in(6,34,35):
        bad=deepcopy(word);bad['diagonal'][role][0]=0 if role==34 else -1
        controls['unearned_head_'+str(role)]=rejected(lambda bad=bad:check_word(bad))
    for label,index in [('body_basis',3),('body_cut',witness[0]['handoff_after']+3),('D_cut',witness[1]['handoff_after']),('return',609)]:
        bad=deepcopy(word);bad['events'][index]=['SCALE',0,'1']
        controls[label]=rejected(lambda bad=bad:check_word(bad))
    return{'status':'PASS_INDEPENDENT_PAID_FRAGMENT_TWO_RETIREMENTS','word':whole,'body_pair':bpair,'D_pair':dpair,'negative_controls':controls,'inputs_sha256':{p.name:sha256(p.read_bytes()).hexdigest()for p in paths},'scope':'Independent exact all-input Laurent/Gaussian ring identities and literal dyadic basis witness; native physical, compiler, and framework scope checked separately.'}

if __name__=='__main__':
    r=run();raw=json.dumps(r,sort_keys=True,indent=2)+'\n'
    if sys.argv[1:]==['--write']:(HERE/'INDEPENDENT.json').write_text(raw)
    else:need((HERE/'INDEPENDENT.json').read_text()==raw,'Frozen independent audit receipt')
    print(r['status'])
