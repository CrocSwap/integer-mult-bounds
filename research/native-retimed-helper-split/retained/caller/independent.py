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


def check_pair(base,witness,second=False):
    n=base['roles'];one={(0,)*(base['stages']+1):ONE};pivot=4 if second else 6
    entries=({'c':{4:-1,5:2},'d':{4:-1},'a':{1:-1,2:1},'b':{0:-1,2:1}}if second else{'c':{6:-2,7:1},'d':{7:1},'a':{0:-1,2:1},'b':{1:-1,2:1}})
    c,d,a,b=[vector(n,one,entries[k])for k in('c','d','a','b')]
    need(dot(d,c)==dot(b,a)==one,'Both dyadic dual pairings')
    cut=witness['cut_after'];stages=[10]if second else[5,6,7,8]
    need(cut==(394 if second else 158)and base['events'][cut]==['IDLE_ONE',2,stages],'Actual paid-fragment cut')
    def factor(p):
        p=shift(p,stages=stages)
        return normalized_central(p)if second else p
    col=deepcopy(c)
    for e in base['events'][:cut+1]:forward(col,e)
    need(col==[factor(p)for p in a],'Actual prefix column, including its normalized central phase')
    row=deepcopy(b)
    for e in reversed(base['events'][:cut+1]):right_action(row,e)
    need(row==[factor(p)for p in d],'Actual prefix row, with no inverse inference')
    unit=vector(n,one,{pivot:1});col=deepcopy(unit)
    for e in witness['input_basis']:forward(col,e)
    need(col==c,'Input basis literal column')
    inv=[]
    for e in reversed(witness['input_basis']):
        e=deepcopy(e)
        if e[0]=='ADD':e[-1]=str(-F(e[-1]))
        elif e[0]=='SCALE':e[-1]=str(1/F(e[-1]))
        inv.append(e)
    row=deepcopy(unit)
    for e in reversed(inv):right_action(row,e)
    need(row==d,'Input basis inverse literal row')
    cut_basis=witness['cut_basis'][:-1]if second else witness['cut_basis']
    col=deepcopy(a)
    for e in cut_basis:forward(col,e)
    need(col==unit,'Cut basis literal column')
    row=deepcopy(unit)
    for e in reversed(cut_basis):right_action(row,e)
    need(row==b,'Cut basis literal row')
    if second:need(witness['cut_basis'][-1]==['LAMBDA',4,-1],'Ordinary normalization of S D into q^-1 D')
    return{'cut_after':cut,'pivot':pivot,'head':int(second),'prefix_stages':stages,'dual_pairings':'1','all_coefficients':'exact Laurent/Gaussian','odd_denominators':False}

def check_word(word):
    n=word['roles'];one={(0,)*(word['stages']+1):ONE}
    need((n,word['stages'],len(word['events']))==(34,18,606),'Complete independent-input census')
    need(all(t[1]==0 for t in word['diagonal']),'No untested old stage')
    need(sorted(e[1]for e in word['events']if e[0]=='LOCAL')==list(range(1,19)),'All distinct stages exactly once')
    for j in range(n):
        v=vector(n,one,{j:1})
        for e in word['events']:forward(v,e)
        d=word['diagonal'][j];expected=[{}for _ in range(n)];expected[j]={(d[0]%4,*d[2:]):ONE}
        need(v==expected,'Independent forward column '+str(j))
        v=vector(n,one,{j:1})
        for e in reversed(word['events']):right_action(v,e)
        need(v==expected,'Independent reverse row '+str(j))
    return{'inputs':n,'forward_coefficients':n*n,'reverse_coefficients':n*n,'events':606,'independent_body_variables':18}

def rejected(f):
    try:f()
    except ValueError as e:return str(e)
    raise ValueError('Invalid control accepted')

def run():
    paths=[HERE/n for n in('CALLER-UNRETIRED.json','CALLER-ONE-RETIRED.json','CONTROLLER.json','RETIREMENT-WITNESSES.json')]
    base,one,word,witness=[json.loads(p.read_bytes())for p in paths]
    pairs=[check_pair(base,witness[0]),check_pair(one,witness[1],True)];whole=check_word(word);controls={}
    for op in('LOCAL','QUERY','IDLE','IDLE_ONE','LAMBDA','ADD'):
        bad=deepcopy(word);j=next(i for i,e in enumerate(bad['events'])if e[0]==op);bad['events'][j]=['SCALE',0,'1']
        controls['omitted_'+op]=rejected(lambda bad=bad:check_word(bad))
    for label,index in [('first_input',3),('first_handoff',witness[0]['handoff_after']+3),('second_handoff',witness[1]['handoff_after']),('final_return',605)]:
        bad=deepcopy(word);bad['events'][index]=['SCALE',0,'1']
        controls[label]=rejected(lambda bad=bad:check_word(bad))
    for role in(6,32,33):
        bad=deepcopy(word);bad['diagonal'][role][0]=0 if role==32 else -1
        controls['unearned_head_'+str(role)]=rejected(lambda bad=bad:check_word(bad))
    bad=deepcopy(word);bad['events'][witness[1]['handoff_after']][-1]=1
    controls['wrong_cut_normalizer']=rejected(lambda:check_word(bad))
    return{'status':'PASS_INDEPENDENT_TWO_PAID_FRAGMENTS','pairs':pairs,'word':whole,'negative_controls':controls,'inputs_sha256':{p.name:sha256(p.read_bytes()).hexdigest()for p in paths},'scope':'Exact all-input caller algebra and dyadic witnesses. Physical/native/finite/outer assumptions are separate.'}

if __name__=='__main__':
    r=run();raw=json.dumps(r,sort_keys=True,indent=2)+'\n'
    if sys.argv[1:]==['--write']:(HERE/'INDEPENDENT.json').write_text(raw)
    else:need((HERE/'INDEPENDENT.json').read_text()==raw,'Frozen independent audit')
    print(r['status'])
