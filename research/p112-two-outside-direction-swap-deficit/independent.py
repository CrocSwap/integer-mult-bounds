from pathlib import Path
from itertools import product,combinations
import json
P=Path(__file__).resolve().parent
R=P.parents[1]
def need(x,msg):
    if not x:raise ValueError(msg)
def main():
    report=json.loads((P/'RESULT.json').read_text());counts={}
    edges=list(combinations(range(4),2))
    for q in (2,3):
        # Separate exhaustive solver: quantify all nonzero functionals and all colors.
        pts=[(0,1)]+[(1,t) for t in range(q)]
        fs=[(a,b) for a in range(q) for b in range(q) if a or b]
        count=0
        for points in product(pts,repeat=4):
            for mask in range(64):
                graph=[(a,b) for k,(a,b) in enumerate(edges) if mask&(1<<k)]
                def evalf(f,i):return (f[0]*points[i][0]+f[1]*points[i][1])%q
                def sep(i):
                    neighbors=[b if a==i else a for a,b in graph if a==i or b==i]
                    return any(evalf(f,i) and all(evalf(f,j)==0 for j in neighbors) for f in fs)
                if not all(sep(i) for i in range(4)):continue
                count+=1
                need(any(all(points[i][color[i]] for i in range(4)) and all(color[a]!=color[b] for a,b in graph) for color in product((0,1),repeat=4)), 'separator without list coloring')
        counts[str(q)]=count
    need(counts==report['census_admissible'],'independent census')
    data=json.loads((R/'research/p112-single-lift/reference-geometry.json').read_text())
    fixture=report['fixture'];ids=fixture['indices'];colors=fixture['colors']
    for color in (0,1):
        group=[i for i,c in zip(ids,colors) if c==color]
        for i in group:
            for j in group:
                need((data['duals'][i]&data['labels'][j]).bit_count()%2==int(i==j),'colored Gram identity')
        # All binary subset sums, independent of Gaussian-elimination code.
        sums={0}
        for i in group:sums|={x^data['labels'][i] for x in tuple(sums)}
        need(len(sums)==2**len(group),'independent labels')
    # Whole-class coloring really fails on the three-class triangle.
    classes=[0,1,1,2,2,0];es=[(0,1),(2,3),(4,5)]
    need(not any(all(c[classes[i]]!=c[classes[j]] for i,j in es) for c in product((0,1),repeat=3)),'global class obstruction')
    print('PASS_INDEPENDENT_SEPARATOR_AND_LIST_CENSUS',counts)
if __name__=='__main__':main()
