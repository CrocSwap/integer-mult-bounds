# HALVPAY getrun.py: regenerate the FANOUT56 main program + init (own lane code build.py); 'nomix' = positive-control variant
import sys, pickle, os
OUT='code/halvpay/f56run%s.pkl'%('_nomix' if 'nomix' in sys.argv else '')
os.chdir('<research-tree>/cards/WILD/FANOUT56'); sys.path.insert(0,'.')
import build
dz=pickle.load(open('design_40k.pkl','rb'))
prog,init,targets,helpers,meta=build.plan(dz['dep'],dz['gat'],ctl=dict(nomix=('nomix' in sys.argv)))
R=build.run(prog,init,targets,helpers)
print(len(R['bad']),len(R['miss']),R['ops'],R['mass'])
pickle.dump(dict(prog=R['prog'],init=init,targets=targets,helpers=helpers,P=build.P,n=build.n),open(OUT,'wb'))
