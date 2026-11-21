"""BILINEAR bl6: VALID COVER bound = max over a cell partition of tau-profiles (bl5 LP per cell).  Thresholds LS (env; default 3,k/4,k/2).
Cells per threshold: [0,0],[1,k/4],[k/4+1,k/2],[k/2+1,3k/4],[3k/4+1,k]; row uses the cell's lower end, U uses its upper end (relaxation => valid).
usage: bl6.py k..."""
import os,sys,signal,itertools
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bl5
if __name__=='__main__':
    signal.alarm(6000)
    for k in [int(a) for a in sys.argv[1:]]:
        ls=[int(a) for a in os.environ['LS'].split(',')] if os.environ.get('LS') else sorted(set([3,max(3,k//4),max(3,k//2)]))
        ls=[l for l in ls if l<=k-2]
        g=[0,k//4,k//2,3*k//4,k];cells=[(0,0)]+[(g[i]+1,g[i+1]) for i in range(4)]
        best=None
        for cc in itertools.product(cells,repeat=len(ls)):
            r=bl5.LP(k,ls,[c[0] for c in cc],[c[1] for c in cc]).solve()
            if r is None:continue
            v=104*r[0]/k
            if best is None or v>best[0]:best=(v,cc,r[2])
        print('COVER-valid k',k,'LS',ls,'BOUND %.3f'%best[0],'argcell',best[1],best[2] if os.environ.get('SUP') else '',flush=True)
