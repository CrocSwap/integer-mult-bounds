import sys,math
s=.99
v2p=17**s-16**s;v11=17**s-2*8**s
def D2(k):return 104/k*((k-4)*v2p+k*v11+2*((8*k+1)**s-(k/2)*16**s))
def HP(k):return 104/k*2*((k-2)*v2p+(8*k+1)**s-k*8**s)
for k in [int(a) for a in sys.argv[1:]]:print(k,'%.4f %.4f'%(D2(k),HP(k)))
