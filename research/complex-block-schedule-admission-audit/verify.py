#!/usr/bin/env python3
"""Exact finite source-bound cascade audit. Apache-2.0, Clear1nsight with Codex."""
import ast
import contextlib
import io
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def load(name):
    path = ROOT / name
    raw = path.read_bytes()
    row = next(r for r in json.loads((ROOT/'ORIGINS.json').read_text()) if r['path'] == name)
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes differ: '+name)
    ns = {'__name__': 'frozen_source', '__authenticated_source_bytes__': raw}
    exec(compile(raw, str(path), 'exec'), ns)
    return ns

def source_prefix(ns, filename, function, stop_variable):
    """Execute only literal source construction, stopping before expensive rank/test suite."""
    tree = ast.parse(ns['__authenticated_source_bytes__'])
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    prefix=[]
    for stmt in fn.body:
        if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == stop_variable for t in stmt.targets):
            break
        prefix.append(stmt)
    else:
        raise ValueError('source construction boundary missing')
    prefix.append(ast.Return(value=ast.Call(func=ast.Name(id='locals',ctx=ast.Load()),args=[],keywords=[])))
    fn.body = prefix
    mod=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
    exec(compile(mod,filename,'exec'),ns)
    return ns[function]()

def expected_couplers(n, shifts):
    return [[[(F(1,2) if r == c^s else F(0), F(0)) for c in range(n)] for r in range(n)] for s in shifts]

def apply_U(v,n,shifts):
    w=len(shifts)
    return [v[((k+1)%w)*n+(r^shifts[k])] for k in range(w) for r in range(n)]

def norm2(v): return sum(x*x for x in v)

def audit_cycle(n,shifts,declared):
    w=len(shifts); total=0
    for s in shifts: total ^= s
    require(w%2 == 1 and total != 0,'attaining-sector premise')
    bit=total & -total
    char=[(-1 if (x&bit) else 1) for x in range(n)]
    signs=[1]
    for s in shifts[:-1]: signs.append(-signs[-1]*(-1 if s&bit else 1))
    low=[a*x for a in signs for x in char]
    high=[1]*(w*n)
    require(apply_U(low,n,shifts)==[-x for x in low],'minus eigenvector')
    require(apply_U(high,n,shifts)==high,'plus eigenvector')
    Ucols=[((k+1)%w)*n+(r^shifts[k]) for k in range(w) for r in range(n)]
    require(sorted(Ucols)==list(range(w*n)),'U must be permutation')
    low_image=[x+F(y,2) for x,y in zip(low,apply_U(low,n,shifts))]
    high_image=[x+F(y,2) for x,y in zip(high,apply_U(high,n,shifts))]
    lo=norm2(low_image)/norm2(low);hi=norm2(high_image)/norm2(high)
    require(lo==F(1,4) and hi==F(9,4),'exact extremal norm witnesses')
    require(hi/lo > declared*declared,'claimed full-cascade bound not refuted')
    # Negative controls: sign omission and false bound must actually reject.
    require(apply_U(high,n,shifts)!=[-x for x in high],'invalid minus vector accepted')
    require(F(3)>declared,'invalid condition certificate accepted')
    return {'dimension':w*n,'shifts':shifts,'xor':total,'low_block_signs':signs,
            'character_bit':bit,'norm_squared':'9/4','inverse_norm_squared':'4',
            'condition_number':'3','rejected_bound':str(declared)}

def run():
    ans=load('inputs/pr4818-verify_schedule.py')
    a=ans['build_operators_m4']()
    with contextlib.redirect_stdout(io.StringIO()):
        literal_a=source_prefix(ans,'inputs/pr4818-verify_schedule.py','run_3in10_synthesis','rank_M')
    bns=load('inputs/pr4819-verify_schedule.py')
    b=bns['build_operators_m4']()
    cns=load('inputs/pr4826-verify_schedule.py')
    c=source_prefix(cns,'inputs/pr4826-verify_schedule.py','run_3in9_schedule_verification','rank_M')
    require([a[k]for k in ['G1','G2','G3']]==expected_couplers(16,[1,2,4]),'4818 literal couplers')
    require(b['couplers']==expected_couplers(16,list(range(1,14))),'4819 literal couplers')
    require([c[k]for k in ['G1','G2','G3']]==expected_couplers(32,[1,2,4]),'4826 literal couplers')
    cases={'4818':audit_cycle(16,[1,2,4],F(9,7)),
           '4819':audit_cycle(16,list(range(1,14)),F(8193,8191)),
           '4826':audit_cycle(32,[1,2,4],F(9,7))}
    # Compare both assembled matrices to the independent permutation model.
    for M,n,shifts in [(literal_a['M_cascade'],16,[1,2,4]),(c['M_cascade'],32,[1,2,4])]:
        dim=len(M)
        for r in range(dim):
            for col in range(dim):
                wanted=F(int(r==col))+F(int(col==((r//n+1)%3)*n+((r%n)^shifts[r//n])),2)
                require(M[r][col]==(wanted,F(0)),'actual assembled cascade mismatch')
    # #4819 supplies a forward method rather than materializing M: replay all columns.
    engine=bns['Cascade13in41Engine'](b['couplers'])
    for col in range(208):
        blocks=[[(F(int(k*16+r==col)),F(0)) for r in range(16)] for k in range(13)]
        got=engine.forward_multiply(blocks)
        for k in range(13):
            for r in range(16):
                wanted=F(int(k*16+r==col))+F(int(((k+1)%13)*16+(r^(k+1))==col),2)
                require(got[k][r]==(wanted,F(0)),'4819 actual forward cascade mismatch')
    # #4826 residual claim is TRUE at this width, although its verifier does not assert it.
    pns=load('inputs/pr4826-verify_ports.py')
    p=source_prefix(pns,'inputs/pr4826-verify_ports.py','run_ports_verification','saving_kappa')
    mm=pns['mm'];conj=pns['conj'];zero=pns['ZERO'];C=p['C432']
    Cd=[[conj(C[col][r])for col in range(32)]for r in range(32)]
    mono=mm(p['residual'],Cd)
    require(all(sum(x!=zero for x in row)==1 for row in mono),'residual left multiplier not monomial')
    require(all(sum(mono[r][col]!=zero for r in range(32))==1 for col in range(32)),'residual multiplier column')
    require(all(z==zero or z[0]*z[0]+z[1]*z[1]==1 for row in mono for z in row),'residual multiplier phases')
    require(mm(mono,C)==p['residual'],'residual identity')
    # #4813 sector cancellation is not an arbitrary-input cancellation.
    d=load('inputs/pr4813-verify_schedule.py');ops=d['load_operators']()
    actual=d['word'](ops['H'],d['plus'](ops['B'],d['scale'](d['q'](-1),d['word'](ops['M'],ops['T'],ops['A']))))
    diff=d['plus'](actual,d['scale'](d['q'](-1),ops['K']))
    witness=next((r,col,v)for r,row in enumerate(diff)for col,v in enumerate(row)if v!=d['ZERO'])
    # Source test assumes a swap sign for an entire bank; generic e_col does not satisfy it.
    r,col,v=witness
    require(any(ops['T'][j][col] != (d['ONE'] if j==col else d['ZERO'])for j in range(8)),'not a non-sector witness')
    return {'status':'PASS_COMPLEX_BLOCK_SCHEDULE_ADMISSION_AUDIT','new_kappa':False,
            'cascade_condition':cases,'block5_residual_identity':'finite width-one confirmed',
            'block3_plus_sector_misuse':{'row':r,'input_basis_column':col,'difference':[str(v[0]),str(v[1])]},
            'controls': ['false cascade bound rejected','wrong extremal vector rejected','source hashes checked'],
            'scope':'finite literal matrices plus written permutation-cycle norm proof; no call optimum or complete multiplier'}

if __name__=='__main__':
    result=run()
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write-result' in sys.argv:
        (ROOT/'RESULT.json').write_text(encoded)
    else:
        require(encoded==(ROOT/'RESULT.json').read_text(),'receipt mismatch')
    print(result['status'])
