#!/usr/bin/env python3
"""Independent free-algebra replay of #4534's noncommuting-stage identity for #4470's p16 controller.

Reads #4470's CONTROLLER.json (on main) and #4534's FREE-CERTIFICATE.json (vendored, sha256 pinned to head 90505ab1).
Each of the 32 lines is a combination of the initial lines with coefficients in the free algebra Q<d_s>[q, q^-1]
(q central): a monomial is (q exponent, ordered tuple of stage letters, leftmost first), and an operator applied
later is prepended. Events: LOCAL/QUERY_SHEAR as in my #4516 (shear y += Q^-1 x forward, y -= Q x backward; LOCAL
then left-multiplies both lines by d_stage); IDLE on ascending stages s_1..s_k left-multiplies by d_(s_k)...d_(s_1);
ADD and SIGNED_SWAP literally. Checks: L W R = diag(q^e d_w) in every one of the 1,024 entries, coefficient by
coefficient over ordered words; reversing every idle word breaks it; the 16/16 central exponents; every non-maximal
stage word is a contiguous prefix or suffix of G = (32, 31, 29, ..., 1, 0); L and R are invertible and they and
their inverses have dyadic entries.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT_SHA = "12c732f840c2e9f375a73b941089bde5319b420688401276b7ac270cdd278350"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    for row_ in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row_["path"]).read_bytes()).hexdigest() == row_["sha256"], row_["path"])
    raw = (HERE / "FREE-CERTIFICATE-4534.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CERT_SHA, "#4534 FREE-CERTIFICATE bytes")
    global row, cert, p, n, thick
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_bytes())
    cert = json.loads(raw)
    p = row["pairs"]
    n = 2 * p
    thick = {0, 2 * p, *range(1, 2 * p, 2)}
    need(check(replay(row["physical_events"])) == 0, "L W R = diag(q^e d_w) in all 1,024 entries")
    broken = check(replay(row["physical_events"], reverse_idle=True))
    need(broken > 0, "reversed idle words are rejected")
    diag = [(d[0], tuple(d[1])) for d in cert["diagonal"]]
    need(Counter(e for e, w in diag) == Counter({1: 16, -1: 16}), "central exponents")
    G = max((w for e, w in diag), key=len)
    need(G == (32, 31, 29, 27, 25, 23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1, 0), "longest word G")
    words = {w for e, w in diag if w and w != G}
    need(len(words) == 15 and all(G[:len(w)] == w or G[-len(w):] == w for w in words), "contiguous prefix/suffix words")
    for name in ("left", "right"):
        M = [[F(x) for x in r] for r in cert[name]]
        need(det_nonzero(M), name + " invertible")
        Mi = inverse(M)
        need(all((x.denominator & (x.denominator - 1)) == 0 for r in M + Mi for x in r), name + " and inverse dyadic")
    print(json.dumps({"status": "PASS_FREE_CONTROLLER_REPLAY", "entries_checked": n * n, "reversed_idle_mismatches": broken,
                      "words": len(words) + 1, "new_kappa_claimed": False}, indent=1))


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
def det_nonzero(M):
    M=[r[:] for r in M]; m=len(M)
    for c in range(m):
        piv=next((r for r in range(c,m) if M[r][c]),None)
        if piv is None: return False
        M[c],M[piv]=M[piv],M[c]
        for r in range(c+1,m):
            if M[r][c]:
                f=M[r][c]/M[c][c]; M[r]=[a-f*b for a,b in zip(M[r],M[c])]
    return True
def inverse(M):
    m=len(M); A=[r[:]+[F(int(i==j)) for j in range(m)] for i,r in enumerate(M)]
    for c in range(m):
        piv=next(r for r in range(c,m) if A[r][c]); A[c],A[piv]=A[piv],A[c]
        pv=A[c][c]; A[c]=[x/pv for x in A[c]]
        for r in range(m):
            if r!=c and A[r][c]:
                f=A[r][c]; A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return [r[m:] for r in A]
dy=lambda M: all((x.denominator & (x.denominator-1))==0 for r in M for x in r)


if __name__ == "__main__":
    sys.exit(main())
