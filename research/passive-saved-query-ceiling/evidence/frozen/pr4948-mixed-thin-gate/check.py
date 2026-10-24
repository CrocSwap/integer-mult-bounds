#!/usr/bin/env python3
"""One read/derive mixed-thin policy; no emitter or placement search."""
import gzip
import hashlib
import json
import subprocess
import sys
import types
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PIN = '86e474038e05f99a76d41f71d81946ad2327e4a4'
BASE = 'research/native-involutive-dual/'

def need(ok, text):
    if not ok:
        raise ValueError(text)

def fetch(head, path):
    return subprocess.check_output(['git', '--no-replace-objects', 'show', head+':'+path])

def module(name, data):
    m = types.ModuleType(name)
    m.__file__ = str(HERE/(name+'.py'))
    sys.modules[name] = m
    exec(compile(data, m.__file__, 'exec'), m.__dict__)
    return m

names = ['clifford_exact.py', 'gauge.py', 'NORMALIZERS.json', 'INVOLUTIVE-WORD.json.gz']
raw = {name: fetch(PIN, BASE+name) for name in names}
ce = module('mixed_ce', raw['clifford_exact.py'])
g = module('mixed_gauge', raw['gauge.py'])
N = json.loads(raw['NORMALIZERS.json'])
F = json.loads(gzip.decompress(raw['INVOLUTIVE-WORD.json.gz']))['F']

def word(circ):
    out = ce.ident(9)
    for e in circ:
        if e[0] == 'P': step = ce.perm(9, e[1])
        elif e[0] == 'D': step = ce.diag(9, e[1], e[2])
        elif e[0] == 'X': step = ce.xgate(9, e[1])
        elif e[0] == 'phase': step = ce.Op(9, ce.identity(9), [('phase', e[1])])
        else: raise ValueError('Not a monomial source normalizer')
        out = out.then(step)
    return out

def grade(op):
    return ce.rank([x for x, z, p in op.tab[op.n:]])

K0, K1 = [word(N['ports'][i]['K_word']) for i in (0, 1)]
T = K1.then(K0.adjoint())  # K0^-1 K1, supported C_(0,1) block.
Q = ce.cgate(9, 1)
conjugated = Q.then(T).then(Q.adjoint())  # matrix Q^-1 T Q.
need(Fraction(F[1][0]) == Fraction(-1, 2), 'Actual transpose supported block')
need(grade(T) == 0, 'Actual T is free monomial')
need(grade(conjugated) > 0, 'Actual conjugated supported block leaves monomial subgroup')

def reduce(word):
    out = []
    for x in word:
        if abs(x) in (2, 3): x = abs(x)
        if out and (out[-1] == -x or (abs(x) in (2, 3) and out[-1] == x)):
            out.pop()
        else: out.append(x)
    return tuple(out)

g.reduce_word = reduce
a = g.Algebra(2)
q, c, e = [a.gen(i) for i in (1, 2, 3)]
qi = a.inv(q)
d, f = a.D(0), a.D(1)
need(a.mul(c, d, q) == a.mul(d, q, c), 'Own C commutes DQ')
need(a.mul(c, f) == a.mul(f, c), 'Other fresh D commutes C')
need(a.mul(c, d) != a.mul(d, c), 'No false own-D commutation')

# Incoming L(C Q^-1), then B=D U(-Q C), then outgoing L(Q^-1 C).
local = a.mm(a.L(a.mul(qi,c)), a.diag(d,d), a.U(a.neg(a.mul(q,c))), a.L(a.mul(c,qi)))
want = [[{}, a.neg(a.mul(d,q,c))], [a.mul(d,c,qi), {}]]
need(local == want, 'Mixed local identity with exact order')

def replay(c1, c3):
    rows = [[a.one if i == j else {} for j in range(4)] for i in range(4)]
    def plus(dst, src, z):
        rows[dst] = [a.add(x,a.mul(z,y)) for x,y in zip(rows[dst],rows[src])]
    def left(role,z): rows[role] = [a.mul(z,x) for x in rows[role]]
    def thin(pair,z): plus(2*pair+1,2*pair,z)
    def full(pair,z,D):
        plus(2*pair,2*pair+1,a.neg(a.mul(q,z)))
        left(2*pair,D); left(2*pair+1,D)
    def bridge(dst,src,sign):
        plus(2*dst,2*src,a.one if sign == 1 else a.neg(a.one))
        plus(2*src+1,2*dst+1,a.neg(a.one) if sign == 1 else a.one)
    rows[0][2] = a.neg(a.one); rows[3][1] = a.one
    thin(0,a.mul(c1,qi))        # One incoming assignment, dictated by local identity.
    full(0,c1,d)
    left(2,d); left(3,d)        # Retain the paid source IDLE.
    bridge(0,1,1)
    thin(0,a.mul(qi,c1))        # One outgoing assignment, no variants.
    bridge(0,1,-1)
    full(1,c3,f)
    thin(1,a.mul(qi,c3))
    bridge(1,0,1)
    for pair in range(2):
        x,y = 2*pair,2*pair+1
        rows[x],rows[y] = rows[y],[a.neg(v) for v in rows[x]]
    plus(0,2,a.one); plus(3,1,a.neg(a.one))
    return rows

rows = replay(c,e)
targets = [a.mul(d,qi),a.mul(d,q),a.mul(f,d,qi),a.mul(f,d,q)]
standard = [[targets[i] if i == j else {} for j in range(4)] for i in range(4)]
need(replay(a.one,a.one) == standard, 'Uncoded control')
need(rows != standard, 'Single mixed policy does not realize source standard targets')
diags = [a.mul(qi,c,d),a.mul(c,q,d),a.mul(qi,e,d,f),a.mul(e,q,d,f)]
leak = a.mul(a.add(a.mul(e,c),a.neg(a.one)),d,f)
need(rows == [[diags[i] if i == j else leak if (i,j)==(3,2) else {}
               for j in range(4)] for i in range(4)], 'Complete mixed matrix formula')
cleanup = a.mul(a.add(e,a.neg(a.mul(e,c,e))),q)
cleaned = [list(row) for row in rows]
cleaned[3] = [a.add(x,a.mul(cleanup,y)) for x,y in zip(rows[3],rows[2])]
need(cleaned == [[diags[i] if i == j else {} for j in range(4)] for i in range(4)],
     'Literal Q-bearing cleanup coefficient')
decoders = [a.mul(qi,c,q),c,a.mul(qi,e,q),e]
need([[a.mul(decoders[i],poly) for poly in row] for i,row in enumerate(cleaned)] == standard,
     'All four diagonal decoder obligations included')

def serial(poly):
    return [{'word':list(w),'fresh_powers':list(ds),'coefficient':str(v)}
            for (w,ds),v in sorted(poly.items())]

iv_head = '20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
iv_path = 'research/higher-moment-strictification/verify.py'
iv_raw = fetch(iv_head,iv_path)
iv = module('mixed_interval',iv_raw)
P = {1:4754,2:824,3:1020,4:254,5:80,8:224}
Tar = {4:56,7:14,8:94,9:876,17:224}
def margin(C):
    t = 1-Fraction(C)
    A,B = iv.moment(Tar,t),iv.moment(P,t)
    return iv.display((A[0]-B[1],A[1]-B[0]))

result = {
    'status':'STOP_ONE_MIXED_POLICY_STANDARD_BOUNDARY_ENDPOINT_FAILS',
    'physical_emission':False,'new_kappa':None,
    'policy':'p2 pattern I; stage0 C1 Q^-1; stage2 Q^-1 C1; stage4 Q^-1 C3; source IDLE/bridges/swaps/scalar boundaries retained',
    'local_identity_verified':True,
    'supported_actual_code_block':{'indices':[0,1],'coefficient':'-1/2',
        'T_grade':grade(T),'Q_inverse_T_Q_grade':grade(conjugated),
        'T_X0_image':T.tab[0], 'conjugated_tableau':conjugated.tab},
    'rows':[[serial(poly) for poly in row] for row in rows],
    'nonzero_offdiagonal_positions':[[i,j] for i in range(4) for j in range(4) if i!=j and rows[i][j]],
    'formal_post_cleanup_ADD_coefficient':serial(cleanup),
    'formal_diagonal_post_decoders':[serial(x) for x in decoders],
    'boundary_obligations':'The Q-bearing cleanup and both Q^-1 C_s Q negative-output decoders are not admitted free code operations. Positive C_s decoders are finite source code evaluations.',
    'optimistic_unrealized_invoice':{'paid':P,'targets_including_helpers_once':Tar,
        'margin_at_C4610':margin('0.0030217758'),'margin_at_C0034':margin('0.0034'),
        'finite_cost_qualification':'Existing FULL/wrapper/IDLE/bridge work retained. Free finite code and incoming/outgoing thin realizations require their actual COPY/ADD/CLEAR/normalizer/precision bill; none is admitted by this optimistic moment.'},
    'source_pins':[{'head':PIN,'path':BASE+name,'sha256':hashlib.sha256(raw[name]).hexdigest()} for name in names]
        +[{'head':iv_head,'path':iv_path,'sha256':hashlib.sha256(iv_raw).hexdigest()}],
    'limits':['Formal fresh-stage model rejection only; not an arbitrary code-dependent decoder theorem.',
        'A nonmonomial supported block rules out treating this Q conjugation as one monomial map; it does not prove an aggregate query lower bound.',
        'No implementation, all-width actual endpoint, compiler, or outer-caller admission.'],
}
print(json.dumps(result,indent=2,sort_keys=True))
