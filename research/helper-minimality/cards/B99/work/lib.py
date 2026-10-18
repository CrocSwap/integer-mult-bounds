import gzip,json
from collections import Counter,defaultdict
from fractions import Fraction as Q
CW=(__import__('os').environ['HM_ROOT']+'/inputs/words/656-CANONICAL-WORD.json.gz')
def load(): return json.load(gzip.open(CW))
def climbs(d,A=None,B=None,tail=None,start=None,final=None):
    A=d['A'] if A is None else A; B=d['B'] if B is None else B; tail=d['tail'] if tail is None else tail
    start=d['start'] if start is None else start; final=d['final'] if final is None else final
    fr=d['frames'];cur=list(start);out=[]
    L=lambda f:len(fr[f])
    def climb(r,f,tag):
        if cur[r]==f:return
        out.append((r,L(f)-L(cur[r]),tag));cur[r]=f
    for part in ('A','centers','B','tail','final'):
        if part in('A','B','tail'):
            ops={'A':A,'B':B,'tail':tail}[part]
            for i,e in enumerate(ops):
                for r in [e[1]]+([e[2]] if e[0]=='add' else []):climb(r,e[-1],part)
        elif part=='centers':
            for k,r in enumerate(d['centers']):
                cf=d['center_frames'][k]
                terms=[e for e in d['cut'] if e[2]==r]
                path=[cf]+sorted({0 for e in terms}-{cf},key=lambda x:-L(x))
                for a in range(1,len(path)):out.append((r,L(path[a-1])-L(path[a]),'cen'))
        else:
            for r,f in enumerate(final):climb(r,f,'final')
    return out
