import os,sys,pickle,cProfile,pstats,json,ast
os.environ['E8COORD']='ham'
sys.path.insert(0,'../reg/code/reuse')
import hx, fullword, reuse as RU
h,atoms=hx.load()
W=hx.C2.compile2(h); raw=fullword.build(W)
RU.reuse(raw)   # warm closure cache
pr=cProfile.Profile(); pr.enable(); re_,n=RU.reuse(raw); pr.disable()
pstats.Stats(pr).sort_stats('cumulative').print_stats(12)
