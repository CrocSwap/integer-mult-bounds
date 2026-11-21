"""KASYM ka6: (a) sympy check of r'' bracket; (b) mpmath discrete checks dq>0, d2q<0 for D=2..N; HP monotone/crossing."""
import sympy as sp, mpmath as mp,sys
D,s,v=sp.symbols('D s v',positive=True);u=8*D+1
r=(u**s-v)/D
lhs=sp.simplify(sp.diff(r,D,2)*D**3)
rhs=u**(s-2)*(64*(1-s)*(2-s)*D**2+16*(2-s)*D+2)-2*v
print('r\'\' bracket identity:',sp.simplify(sp.expand(lhs-rhs))==0 or sp.simplify(sp.powsimp(sp.expand(lhs-rhs),force=True)))
print('N identity:',sp.simplify(sp.diff(r,D)*D**2-(v-u**(s-1)*((1-s)*8*D+1))))
mp.mp.dps=40;S=mp.mpf(99)/100;v2p=mp.mpf(17)**S-mp.mpf(16)**S;e8=mp.mpf(8)**S
q=lambda D:(v2p-(8*D+1)**S+e8*D)/D
N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
mind=min(q(d+1)-q(d) for d in range(2,N));maxd2=max(q(d+1)-2*q(d)+q(d-1) for d in range(3,N))
print('D=2..%d: min dq %s  max d2q %s'%(N,mp.nstr(mind,5),mp.nstr(maxd2,5)))
HP=lambda k:208*((k-2)*v2p+(8*k+1)**S-k*e8)/k
print('HP 12,13,14:',[mp.nstr(HP(k),10) for k in (12,13,14)],' HP73',mp.nstr(HP(73),10),' HP74',mp.nstr(HP(74),10))
print('m(12),m(13) vs 2v2p:',[mp.nstr((8*k+1)**(S-1)*(8*(1-S)*k+1),8) for k in (12,13)],mp.nstr(2*v2p,8))
print('limit 208(v2p-8^s)=',mp.nstr(208*(v2p-e8),8),' HP(1e3),HP(1e4),HP(1e6)',[mp.nstr(HP(mp.mpf(k)),7) for k in (1000,10000,10**6)])
