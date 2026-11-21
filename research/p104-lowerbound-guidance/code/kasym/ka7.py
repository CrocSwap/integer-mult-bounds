"""KASYM ka7: built Q=0 frames (C1, c33 from callercut cc0 definitions) -- role-piece c^ vs HP(k)."""
import sys;sys.path.insert(0,'code/callercut')
import cc0,mpmath as mp
S=mp.mpf(99)/100;v2p=mp.mpf(17)**S-mp.mpf(16)**S;e8=mp.mpf(8)**S
HP=lambda k:208*((k-2)*v2p+(8*k+1)**S-k*e8)/k
for name,k,R in [('C1',3,cc0.C1),('c33',6,cc0.C33)]:
    tot=0
    for M,d in cc0.pieces(R):
        ps={p for p in d.values()};tot+=(8*len(M)+1)**S-sum((8*len(p))**S for p in ps)
    print(name,'k',k,'roles',len(R),'(2k-2=%d)'%(2*k-2),'c^ %s  HP(k) %s'%(mp.nstr(104*tot/k,9),mp.nstr(HP(k),9)))
