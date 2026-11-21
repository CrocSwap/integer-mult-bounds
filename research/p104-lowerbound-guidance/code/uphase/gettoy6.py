"""UPHASE gettoy6.py: rebuild RELAYTREE toy6 (seed 1; our own lane code, run unchanged up to its CHECK) and dump the word."""
import sys, pickle, os
HERE=os.path.dirname(os.path.abspath(__file__)); RT=os.path.normpath(os.path.join(HERE,'../../RELAYTREE'))
os.chdir(RT); sys.path.insert(0, RT); sys.argv = ['toy6.py', '1']
src = open('toy6.py').read().split('# controls')[0]
g = {'__name__': 'toy6run'}
exec(compile(src, 'toy6.py', 'exec'), g)
D = g['D']; W, X, Y, H = D.word()
pickle.dump(dict(W=W, X=X, Y=Y, H=H, ports=D.ports, N=D.N, Z=D.Z), open(os.path.join(HERE,'toy6_word.pkl'), 'wb'))
print('keys', list(W.keys())); print(W['program'][:6])
