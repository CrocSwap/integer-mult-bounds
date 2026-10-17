import csv,ast,itertools
from rrc import g,N
def fam(comp,j,extra=0):
    m=len(comp); cap=lambda S:sum(g[comp[i]] for i in S)+extra
    F=[]
    for M in itertools.combinations(range(m),j-1):
        rest=frozenset(i for i in range(m) if i not in M)
        c=cap(rest)
        if c<57: return 'IMM'
        if c<=77: F.append(rest)
    F.sort(key=cap); ch=[]
    for f in F:
        if all(cap(f&o)<=56 for o in ch): ch.append(f)
    return len(ch)
def dead_j(comp,j,extra=0):
    r=fam(tuple(sorted(comp,reverse=True)),j,extra)
    return (r=='IMM' or r>N[j]), r
def variants(ws,d,j):
    comp=ws[d-j:]; kmin=ws[d-j-1]
    yield 'base',comp,0
    yield '+line',comp,1
    for x in sorted(set(comp)):
        up=list(comp); up.remove(x); up.append(x+1)
        sw=list(comp); sw.remove(x); sw.append(kmin)
        yield 'x=%d'%x,(up,sw),0
if __name__=="__main__":
    rs=[r for r in csv.DictReader(open('../SC-B/residue.csv')) if sum(ast.literal_eval(r['weights']))-8*int(r['d'])==6]
    for r in rs:
        ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d'])
        print(ws)
        for tag in ['base','+line']+['x=%d'%x for x in sorted(set(ws[d-2:]))]:
            res=[]
            for j in (2,3,4):
                for t,c,ex in variants(ws,d,j):
                    if t!=tag: continue
                    if tag.startswith('x='):
                        up,sw=c
                        res.append((j,'up',dead_j(up,j)[0],'swap',dead_j(sw,j)[0]))
                    else: res.append((j,dead_j(c,j,ex)))
            print('  ',tag,res)
