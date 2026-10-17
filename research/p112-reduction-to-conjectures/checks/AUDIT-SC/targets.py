import pickle, numpy as np, p112 as p
reps=pickle.load(open('dirreps.pkl','rb'))
pos={g:i for i,g in enumerate(p.P)}   # global line index -> P112 index
def hexm(off):
    lo=sum(1<<pos[i] for i in off if pos[i]<64); hi=sum(1<<(pos[i]-64) for i in off if pos[i]>=64)
    return '%016x'%lo,'%016x'%hi
r0=p.P[0]
off_r=[i for i in p.P if p.IP[i,r0]!=0]
T=[('root',hexm(off_r),3,pos[r0])]
for k,(sz,osz,o,tags) in enumerate(reps): T.append(('non%02d_%d'%(k,sz),hexm(o),4,-1))
pickle.dump({'r0':r0,'off_r':off_r,'reps':reps},open('targets.pkl','wb'))
for name,(lo,hi),k,f in T: print(name,lo,hi,k,f)
