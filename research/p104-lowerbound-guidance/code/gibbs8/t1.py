import sys,glob; from g8lib import *
Qs={'HS64':Q_std(std_set('HS64')),'E7s':Q_std(std_set('E7s'))}
for f in sorted(glob.glob('../mergerows/*.pkl')):
    sn='HS64' if ('HS64' in f or 'hs_' in f) else 'E7s'
    try:
        rows=pickle.load(open(f,'rb')); 
        if not isinstance(rows,list) or not isinstance(rows[0],tuple): continue
        Q=Qs[sn]; e,W,V,pr,_,_=normalise(rows,Q); print(f.split('/')[-1],sn,'e',e,'m',len(rows),'C',sum(pr))
    except Exception as ex: print(f,'ERR',ex)
