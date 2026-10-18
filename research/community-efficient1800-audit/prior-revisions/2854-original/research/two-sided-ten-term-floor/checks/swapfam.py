# Two-sided root-swap family: row swaps (j_a, r_a) and column swaps (j_b, r_b) + frame terms.
# Inside rank-one terms form a dual basis pair: row swap (x=c_ra, y=e_ja), col swap (x=e_jb, y=c_rb), frame terms x=e_i or y=e_i.
# Search min #bad (frame slots with neither side frame) over all choices; then build exactly, verify P Q^T = N0, cost.
import itertools, sys
from lib import *
import sympy as sp
roots_by=[ [t for t in range(n) if C[t][j]] for j in range(8)]
def feasible_search(kr,kc,want_all=False):
    best=(99,None)
    for Jr in itertools.combinations(range(8),kr):
        rest=[i for i in range(8) if i not in Jr]
        for Jc in itertools.combinations(rest,kc):
            if kr and Jr[0]!=0 and kc==0: continue  # symmetry trim (one-sided)
            J=set(Jr)|set(Jc); I=[i for i in range(8) if i not in J]
            rc=[[t for t in roots_by[j] if supp8(t)&set(Jr)=={j}] for j in Jr]
            cc=[[t for t in roots_by[j] if supp8(t)&set(Jc)=={j}] for j in Jc]
            # backtrack rows then cols with orthogonality row/col; minimise bad
            def rec_rows(a,chosen,U):
                nonlocal best
                if a==kr: return rec_cols(0,chosen,[],U,set())
                seen=set()
                for t in rc[a]:
                    key=(frozenset(supp8(t)),)
                    if t in chosen: continue
                    rec_rows(a+1,chosen+[t],U|supp8(t))
                    if best[0]==0: return
            def rec_cols(b,rows,cols,U,V):
                nonlocal best
                bad=len([i for i in I if i in U and i in V])
                if bad>=best[0]: return
                if b==kc:
                    best=(bad,(Jr,Jc,rows,cols)); return
                for t in cc[b]:
                    if t in cols: continue
                    if any(sum(C[t][i]*C[r][i] for i in range(8))!=0 for r in rows): continue
                    rec_cols(b+1,rows,cols+[t],U,V|supp8(t))
                    if best[0]==0: return
            rec_rows(0,[],set())
            if best[0]==0: return best
    return best
def build_family(Jr,Jc,rows,cols,verbose=True):
    kr,kc=len(Jr),len(Jc)
    J=set(Jr)|set(Jc); I=[i for i in range(8) if i not in J]
    U=set().union(*[supp8(t) for t in rows]) if rows else set()
    V=set().union(*[supp8(t) for t in cols]) if cols else set()
    terms=[]  # (xpres or None, ypres or None, kind)
    for j,t in zip(Jr,rows): terms.append((croot(t),e(j),('row',j,t)))
    for j,t in zip(Jc,cols): terms.append((e(j),croot(t),('col',j,t)))
    for i in I:
        if i not in V: terms.append((e(i),None,('fx',i)))
        elif i not in U: terms.append((None,e(i),('fy',i)))
        else: terms.append((None,None,('bad',i)))
    for k,tm in enumerate(terms):
        if tm[0] is not None and tm[1] is not None:
            ip=sum(a*b for a,b in zip(tm[0],tm[1])); assert ip!=0
            terms[k]=(tm[0],[v/ip for v in tm[1]],tm[2])
    PY=[k for k,tm in enumerate(terms) if tm[1] is not None]
    X=[None]*8
    for k,tm in enumerate(terms):
        if tm[0] is not None: X[k]=tm[0]
    # unknown x_l: <x_l,y_k>=delta_lk for k in PY; pick particular solution, generic in free part (deterministic)
    for l,tm in enumerate(terms):
        if X[l] is not None: continue
        xs=sp.symbols('x0:8'); eqs=[sum(xs[i]*terms[k][1][i] for i in range(8))-(1 if k==l else 0) for k in PY]
        sol=sp.solve(eqs,xs,dict=True)[0]
        free=[s for s in xs if s not in sol]
        vals={s:(l+2*idx+1) for idx,s in enumerate(free)}
        X[l]=[Fr(str(sp.sympify(sol.get(s,s)).subs(vals))) for s in xs]
    Xm=sp.Matrix([[sp.Rational(str(v)) for v in r] for r in X]); Ym=(Xm.inv()).T
    Y=[[Fr(str(Ym[k,i])) for i in range(8)] for k in range(8)]
    for k in PY: assert Y[k]==terms[k][1], ('dual mismatch',k)
    E=[delta(t) for t in rows]; F=[delta(t) for t in cols]
    Xh=[];Yh=[];names=[]
    for k,tm in enumerate(terms):
        kind=tm[2]
        if kind[0]=='row':
            a=Jr.index(kind[1]); t=kind[2]; z2=[Fr(0)]*kr; z2b=[Fr(0)]*kr; z2[a]=Fr(-2); z2b[a]=Fr(2)
            Xh+= [(X[k],z2),([Fr(0)]*8,z2b)]; Yh+=[(Y[k],[Fr(0)]*kc)]*2; names+=['row-swap p\'','row-swap delta']
        elif kind[0]=='col':
            b=Jc.index(kind[1]); t=kind[2]; z2=[Fr(0)]*kc; z2b=[Fr(0)]*kc; val=sum(Fr(C[t][i],2)*Y[k][i] for i in range(8)); z2[b]=-val; z2b[b]=val
            Yh+= [(Y[k],z2),([Fr(0)]*8,z2b)]; Xh+=[(X[k],[Fr(0)]*kr)]*2; names+=['col-swap q\'','col-swap delta']
        else:
            Xh.append((X[k],[Fr(0)]*kr)); Yh.append((Y[k],[Fr(0)]*kc)); names.append('frame '+kind[0])
    if not verbose: return Xh,Yh,E,F,names
    P,Q=build(Xh,Yh,E,F)
    bad=check(P,Q,masked=False); cs=costs(P,Q)
    if verbose:
        print(f'  kr={kr} kc={kc} Jr={Jr} Jc={Jc} rows={rows} cols={cols} m={len(P)} exact PQ^T=N0 mismatches={bad} cost={sum(cs)}')
        print('   ',list(zip(names,cs)))
    return bad,sum(cs)
if __name__=='__main__':
    for kr in range(0,5):
        for kc in range(kr,9-kr):
            if kr+kc==0 or kr+kc>8: continue
            b,ex=feasible_search(kr,kc)
            print(f'(k_r,k_c)=({kr},{kc}): min #both-nonframe frame slots = {b}' + ('' if ex else '  (no admissible config)'))
            if ex: build_family(*ex)
            sys.stdout.flush()
