import sys,os,json,gzip
os.environ['E8COORD']='ham'
sys.path.insert(0,'code/bit/producer'); sys.path.insert(0,'code/reuse')
w=json.load(gzip.open(sys.argv[1]))
v=120; R=w['R']
gates=[('A',g) for g in w['A']]+[('B',g) for g in w['B']]
first={};last={}
for k,(ph,(f,d,srcs)) in enumerate(gates):
    for r in [d]+srcs:
        if r>=2*v:
            first.setdefault(r,k); last[r]=k
ret=set(w['ret'])
# live count at each gate index
ev=[0]*(len(gates)+2)
for r in first:
    ev[first[r]]+=1; ev[last[r]+1]-=1
cur=0; prof=[]
for k in range(len(gates)):
    cur+=ev[k]; prof.append(cur)
mx=max(prof); print('R',R,'peak live (A/B gates only)',mx,'at',prof.index(mx),'of',len(gates),'nA',len(w['A']))
# sample
import numpy as np
for i in range(0,len(gates),max(1,len(gates)//30)): print(i,gates[i][0],prof[i])
