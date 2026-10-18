from rep import *
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
class FL:
    def __init__(s,d):
        s.fr=[basis(f) for f in d['frames']]
        s.id={f:i for i,f in enumerate(s.fr)}
        s.ss=[None]*len(s.fr)
    def add(s,f):
        f=basis(f)
        if f not in s.id: s.id[f]=len(s.fr);s.fr.append(f)
        return s.id[f]
    def join(s,a,b):
        if a==b: return a
        return s.add(s.fr[a]+s.fr[b])
    def sub(s,a,b): # frame a subset of b
        return basis(s.fr[a]+s.fr[b])==s.fr[b]
    def dim(s,a): return len(s.fr[a])
