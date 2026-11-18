import sys,os,time,pickle
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from bank import *
def exact_values(net, order=None):
    order = order or schedule(net); V = {}
    for k in order:
        v = {}
        for d,c in net.forms[k].items():
            if d < 0: axpy(v, {~d: Q(1)}, c)
            else: axpy(v, V[d], c)
        V[k] = v
    return V
if __name__=='__main__':
    t=time.time(); W=load(sys.argv[1]); net=fold(W); V=exact_values(net)
    print('t',time.time()-t,'avg support',sum(len(v) for v in V.values())/len(V))
    n7674=pickle.load(open('net7674.pkl','rb')); V2=exact_values(n7674)
    print('terminals exact equal:', all(V[net.first+r]==V2[net.first+r] for r in range(len(net.init))), time.time()-t)
