import os,sys,json,ast
os.environ['E8COORD']='ham'
import e8lib as E, frames as Fm, ham2, compile2 as C2, compile as C
Pd={ast.literal_eval(k):v for k,v in json.load(open(sys.argv[1]))}
ham2.P.clear(); ham2.P.update(Pd)
for mode in ['allA','src']:
    C2.PHASEMODE[0]=mode
    h=ham2.build(0,True); W=C2.compile2(h)
    print(mode,W.stats,'f2bad',[len(z) for z in C.f2_check(W)])
