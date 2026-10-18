import sys,json,importlib.util,time
from fractions import Fraction as Q
S='/Users/joelpulikkan/imb-src/pr568/research/complex-multicold'
s=importlib.util.spec_from_file_location('moment',S+'/engines/moment.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
def price(H,live=7168):return Q(M.certify({int(k):v for k,v in H.items()},73,live,False)['lower'])
if __name__=='__main__':
    H=json.loads(sys.argv[1]);t=time.time();b=price(H);print(float(b),b,time.time()-t)
