import os,sys,time,json,ast
os.environ['E8COORD']='ham'
sys.path.insert(0,'code/bit/producer'); sys.path.insert(0,'code/reuse')
import compile2 as C2, fullword, ham2, reuse as RU, retime as RT, compile as C
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r740.json'))}
ham2.P.clear(); ham2.P.update(Pd)
t=time.time(); h=ham2.build(0,True); print('build',time.time()-t)
t=time.time(); W=C2.compile2(h); print('compile',time.time()-t, W.nh)
t=time.time(); raw=fullword.build(W); print('fullword',time.time()-t)
t=time.time(); re_,nre=RU.reuse(raw); print('reuse',time.time()-t, re_['R'])
t=time.time(); fin,mv=RT.retime(re_,sweeps=6,M=64); print('retime',time.time()-t, fin['R'])
