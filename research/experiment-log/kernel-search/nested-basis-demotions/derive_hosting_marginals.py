"""Compute floating LP width marginals for discovery, with exact reconstructed primal counts.
The dual is a search guide, not a certified optimum or bound. Final candidates require exact repricing.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import sys,json,math,types
r=Path.cwd();out=r/'basis139-hosting-marginals';assert not out.exists();out.mkdir();sys.path[:0]=[str(r/'complex447-search'),str(r/'source450-review/code')];import hosting_core as HC
s=(r/'source450-review/code/hosting_k.py').read_text().split('\ndef solve_tape',1)[0];s=s.replace('if avail.get((s, w), 0):','if host_all or avail.get((s, w), 0):');start=s.index('    res = milp(c,');end=s.index('    assert res.x',start)
s=s[:start]+'''    from scipy.optimize import linprog
    assert lo==hi, 'this marginal screen requires only equalities'
    A=np.array(rows);res=linprog(c,A_eq=A,b_eq=np.array(lo),bounds=[(0,None)]*n,method='highs')
    assert res.success,res.message
    global LAST_DUAL
    LAST_DUAL=dict(rows=len(rows),columns=n,objective=float(res.fun),primal_residual=float(np.max(np.abs(A@res.x-np.array(lo)))),dual_slack_min=float(np.min(c-A.T@res.eqlin.marginals)),prices=[(list(key),float(price)) for key,price in zip(avail,res.eqlin.marginals[-len(avail):])])
'''+s[end:];s=s.replace('x = [int(round(t)) for t in res.x]','x = [Q(float(t)).limit_denominator(1000000) for t in res.x]');HK=types.ModuleType('hosting_marginal');HK.__file__=str(r/'source450-review/code/hosting_k.py');HK.Q=Q;exec(s,HK.__dict__)
local=json.loads((r/'nested-basis-exchange-pricing/current110-0-LOCAL.json').read_text());counts=Counter(local['widths']);ns={};text=(r/'screen_whole454_complex.py').read_text();exec(('def schedule(K):'+text.split('def schedule(K):',1)[1].split('\nfor L,T in',1)[0]).replace('rank=8*','rank=7*'),ns);sc=ns['schedule'](5);win={i:x for i,x in HC.windows(sc).items() if x[1] and x[2]};c=float(Q(json.loads((r/'basis-exchange84-strong-RESULT.json').read_text())['bit_lower']));cost=lambda k:k*math.expm1(c*math.log(78/k))/c+32*78*78*math.exp(c*math.log(78))/(10**16*c) if k else 0;HK.cost=lambda k,m:cost(k);avail={(s,w):counts[w] for s in range(11) for w in range(4,9)};y,z,_=HK.solve(win,240,avail,78,host_all=True,maxk=14)
for i in win:
 assert sum(n for (ii,pat),n in y.items() if ii==i)==240
 for w in range(4,9):assert sum(n*pat.count(w) for (ii,pat),n in y.items() if ii==i)==sum(n for (ii,ww,s),n in z.items() if ii==i and ww==w)
for (s,w),n in avail.items():assert sum(k for (i,ww,ss),k in z.items() if ss==s and ww==w)==n
prices={w:sum(price for (s,ww),price in HK.LAST_DUAL['prices'] if ww==w)/11 for w in range(4,9)};result=dict(status='PASS_EXACT_PRIMAL_COUNTS_FLOAT_DUAL_GUIDE_ONLY',bit_c=c,widths=dict(counts),average_stage_width_prices=prices,diagnostics=HK.LAST_DUAL,scope='Float LP marginal discovery guide, not a rational dual optimum certificate. Exact packing and moments must be independently replayed for every retained candidate.');(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
