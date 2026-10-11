import os,sys,json,ast,time
os.environ['E8COORD']='ham'
import ham2, compile2 as C2, compile as C
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r865.json'))}
ham2.P.clear(); ham2.P.update(Pd)
t=time.time()
h=ham2.build(0,True); print('build',time.time()-t)
t=time.time()
W=C2.compile2(h); print('compile',time.time()-t)
print(W.stats)
print(C.f2_check(W)[0][:3],C.f2_check(W)[1][:3])
s,deficit,D,steps=C.evaluate(W)
print('R',W.nh,'saving %.6e'%s,'deficit',deficit,'D %.0f'%D,sorted(steps.items()))
