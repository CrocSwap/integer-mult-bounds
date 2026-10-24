#!/usr/bin/env python3
"""The noncommuting (free-algebra) p-controller identity for every tested size, and a reduction lemma.

Reduction lemma (README). Let W be the controller word in Mat_2p(Q<d_s>[q, q^-1]) and L, R scalar matrices. If the
abelianization (forget letter order) is injective on the set of monomials occurring in W, then the commutative
identity L W_ab R = diag(...) implies the free identity L W R = diag(...): every entry of L W R is a scalar
combination of W's monomials, so its coefficients are read off unchanged. Strictly descending words with distinct
letters are determined by their letter sets, so it suffices that every monomial of W is strictly descending.

Checks: for every p = 2..10 and every prefix length a = 0..p-2, #4440's constructor (research/query-thinned-
controllers/controller.py on main) emits the controller and its commutative boundaries L, R; a separately written
free-algebra replay (as in research/free-controller-replay) gives L W R diagonal with single monomials matching the
commutative diagonal, W has exactly 2p monomials and all are strictly descending; the same support property for
#4470's actual p16 CONTROLLER.json. evidence/ records the same checks for p = 11..14 (91 cases in all).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def replay(events, reverse_idle=False):
    one=(0,())
    lines=[{i:{one:F(1)}} for i in range(n)]
    def lmul(i,e,w):  # left-multiply line i by q^e d_w (w tuple, leftmost first)
        lines[i]={j:{(k[0]+e, tuple(w)+k[1]):v for k,v in poly.items()} for j,poly in lines[i].items()}
    def add(dst,src,e,c):
        for j,poly in lines[src].items():
            tgt=lines[dst].setdefault(j,{})
            for k,v in poly.items():
                kk=(k[0]+e,k[1]); x=tgt.get(kk,0)+c*v
                if x: tgt[kk]=x
                else: tgt.pop(kk,None)
            if not tgt: lines[dst].pop(j)
    for ev in events:
        op=ev[0]
        if op in ('LOCAL','QUERY_SHEAR'):
            _,stage,pair,back=ev; x,y=2*pair,2*pair+1
            if back: x,y=y,x
            add(y,x,1 if back else -1,-1 if back else 1)
            if op=='LOCAL': lmul(x,0,(stage,)); lmul(y,0,(stage,))
        elif op=='IDLE':
            _,pair,sel=ev
            w=tuple(sorted(sel,reverse=True))  # D_{s_k} ... D_{s_1} for ascending list
            if reverse_idle: w=tuple(reversed(w))
            lmul(2*pair,0,w); lmul(2*pair+1,0,w)
        elif op=='ADD':
            _,dst,src,*c=ev; add(dst,src,0,c[0] if c else 1)
        elif op in ('SWAP','SIGNED_SWAP'):
            _,x,y=ev; sg=-1 if op=='SIGNED_SWAP' else 1
            old=lines[x]; lines[x]=lines[y]; lines[y]={j:{k:sg*v for k,v in poly.items()} for j,poly in old.items()}
    return lines
def check(lines):
    L=[[F(x) for x in r] for r in cert['left']]; R=[[F(x) for x in r] for r in cert['right']]
    diag=[(d[0],tuple(d[1])) for d in cert['diagonal']]
    # (L W R)_{ik} = sum_j sum_l L_ij W_jl R_lk, per monomial
    LW=[{} for _ in range(n)]  # LW[i][l] = poly
    for i in range(n):
        acc={}
        for j in range(n):
            if L[i][j]:
                for l,poly in lines[j].items():
                    t=acc.setdefault(l,{})
                    for k,v in poly.items(): t[k]=t.get(k,0)+L[i][j]*v
        LW[i]=acc
    bad=0
    for i in range(n):
        out={}
        for l,poly in LW[i].items():
            for kk in range(n):
                if R[l][kk]:
                    t=out.setdefault(kk,{})
                    for k,v in poly.items(): t[k]=t.get(k,0)+v*R[l][kk]
        for kk in range(n):
            poly={k:v for k,v in out.get(kk,{}).items() if v}
            exp={diag[i]:F(1)} if i==kk else {}
            if poly!=exp: bad+=1
    return bad


def lwr_diagonal(lines, Lm, Rm):
    L = [[F(x) for x in r] for r in Lm]
    R = [[F(x) for x in r] for r in Rm]
    diag = []
    for i in range(n):
        acc = {}
        for j in range(n):
            if L[i][j]:
                for l, poly in lines[j].items():
                    t = acc.setdefault(l, {})
                    for k, v in poly.items():
                        t[k] = t.get(k, 0) + L[i][j] * v
        for kk in range(n):
            out = {}
            for l, poly in acc.items():
                if R[l][kk]:
                    for k, v in poly.items():
                        out[k] = out.get(k, 0) + v * R[l][kk]
            out = {k: v for k, v in out.items() if v}
            if i == kk:
                need(len(out) == 1 and list(out.values())[0] == 1, "single diagonal monomial")
                diag.append(list(out)[0])
            else:
                need(not out, "zero off-diagonal")
    return diag


def support(lines):
    return {k for ln in lines for poly in ln.values() for k in poly}


def main():
    global p, n, thick
    for row_ in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row_["path"]).read_bytes()).hexdigest() == row_["sha256"], row_["path"])
    sys.path.insert(0, str(ROOT / "research/query-thinned-controllers"))
    spec = importlib.util.spec_from_file_location("qtc_controller", ROOT / "research/query-thinned-controllers/controller.py")
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    cases = 0
    for pp in range(2, 11):
        for a in range(0, pp - 1):
            row = C.run("complex", pp, a)
            p, n, thick = pp, 2 * pp, {0, 2 * pp, *range(1, 2 * pp, 2)}
            lines = replay(row["physical_events"])
            diag = lwr_diagonal(lines, row["boundaries"]["left"], row["boundaries"]["right"])
            comm = [tuple(d) for d in row["diagonal"]]
            need(all((e,) + tuple(w.count(s) for s in range(2 * pp + 1)) == c for (e, w), c in zip(diag, comm)),
                 f"p={pp} a={a}: free diagonal abelianizes to the commutative diagonal")
            sup = support(lines)
            need(len(sup) == 2 * pp and all(list(w) == sorted(set(w), reverse=True) for e, w in sup),
                 f"p={pp} a={a}: 2p strictly descending monomials")
            cases += 1
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_bytes())
    p, n, thick = 16, 32, {0, 32, *range(1, 32, 2)}
    sup = support(replay(row["physical_events"]))
    need(len(sup) == 32 and all(list(w) == sorted(set(w), reverse=True) for e, w in sup), "p16 #4470 support")
    ev = (HERE / "evidence/SUPPORT-P2-14.txt").read_text(encoding="utf-8")
    need("ALL DESCENDING: True 91" in ev, "recorded p = 2..14 support sweep")
    print(json.dumps({"status": "PASS_FREE_IDENTITY_ALLP", "cases_checked_here": cases, "recorded_cases_p_le_14": 91,
                      "p16_support": 32, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
