"""Joint monomial run lowering. Apache-2.0, Codex assistance for @woklerx."""
from fractions import Fraction as Q
WORK=('W',0)

def rotation(events,i,end):
    if i+3>end:return None
    es=events[i:i+3]
    if any(e[0]!='scalar'or e[2]!=es[0][2]for e in es):return None
    ops=[e[1]for e in es]
    if any(o[0]!='add'for o in ops):return None
    a,b=tuple(ops[0][1]),tuple(ops[0][2]);q=Q(*ops[0][3:5])
    if a==b or a[0]!='L'or b[0]!='L'or q not in(-1,1):return None
    if tuple(ops[1][1])!=b or tuple(ops[1][2])!=a or Q(*ops[1][3:5])!=-q:return None
    if tuple(ops[2][1])!=a or tuple(ops[2][2])!=b or Q(*ops[2][3:5])!=q:return None
    return a,b,int(q)

def boundary(loc,sign,rotations=True):
    pending={r for r,s in loc.items()if r!=s};out=[];cycles=[];optimized=0
    while pending:
        a=min(pending);cyc=[a];b=loc[a]
        while b!=a:cyc.append(b);b=loc[b]
        copied=[('copy',WORK,a)]+[('copy',d,s)for d,s in zip(cyc,cyc[1:])]+[('copy',cyc[-1],WORK)]
        copied += [('negate',r)for r in cyc if sign.get(r,1)<0]
        chosen=copied
        if len(cyc)==2 and rotations:
            a,b=cyc
            for q in(1,-1):
                alt=[('add'if q==1 else'subtract',a,b),('subtract'if q==1 else'add',b,a),('add'if q==1 else'subtract',a,b)]
                if sign.get(a,1)!=q:alt.append(('negate',a))
                if sign.get(b,1)!=-q:alt.append(('negate',b))
                if len(alt)<len(chosen):chosen=alt
            optimized+=int(chosen!=copied)
        out+=chosen;cycles.append(cyc);pending.difference_update(cyc)
    out += [('negate',r)for r in sorted(sign)if loc.get(r,r)==r and sign[r]<0]
    return out,cycles,optimized

def compile_block(events,start,end,lower,rotations=True):
    loc={};sign={};out=[];found=[];i=start
    def init(r):loc.setdefault(r,r);sign.setdefault(r,1)
    while i<end:
        rot=rotation(events,i,end)
        if rot:
            a,b,q=rot;init(a);init(b)
            loc[a],loc[b]=loc[b],loc[a]
            sign[a],sign[b]=q*sign[b],-q*sign[a]
            found.append(i);i+=3;continue
        op=events[i][1];tag=op[0];d=tuple(op[1]);init(d)
        if tag=='scale':
            q=Q(*op[2:4]);sign[d]*=1 if q>0 else-1
            out.extend(lower(['scale',loc[d],abs(q.numerator),q.denominator],WORK))
        elif tag=='clear':
            out.append(('clear',loc[d]));sign[d]=1
        elif tag=='copy':
            s=tuple(op[2]);init(s);out.append(('copy',loc[d],loc[s]));sign[d]=sign[s]
        else:
            s=tuple(op[2]);init(s);q=Q(*op[3:5])*sign[s]*sign[d]
            out.extend(lower(['add',loc[d],loc[s],q.numerator,q.denominator],WORK))
        i+=1
    tail,cycles,n=boundary(loc,sign,rotations);out+=tail
    if found:out.append(('clear',WORK))
    return {'start':start,'end':end,'frame':events[start][2],'primitives':out,
            'rotations':found,'cycles':cycles,'optimized_two_cycles':n,
            'signed_permutation':[[r,loc[r],sign[r]]for r in sorted(loc)if loc[r]!=r or sign[r]<0]}
