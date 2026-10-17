from cell771 import *
def analyse_q(q):
    gens=[list(C[r0])]
    for phi in range(1,512):
        L=[t for t in Opar[phi] if t!=r0]
        rows=[C[t]+[q[t]] for t in L]
        for v in nullspace(rows,9): gens.append(v[:8])
    R,_=rref(gens,8); return len(R)
z=[Fr(0)]*n
print('q=0 :',analyse_q(z))
u=[t for t in range(n) if t!=r0 and ip(lines[r0],lines[t])!=0][0]
q=z[:]; q[u]=Fr(1); print('q=delta_u (u~r):',analyse_q(q))
u2=[t for t in range(n) if t!=r0 and ip(lines[r0],lines[t])==0][0]
q=z[:]; q[u2]=Fr(1); print('q=delta_u (u perp r):',analyse_q(q))
# q = 2-piece on a pair of lines: p_r-line... q = p_r restricted to one flat of the first pair
Ma,Mb=pairs[0]
q=[ (ip8(lines[r0],lines[t]) if Ma>>t&1 else Fr(0)) for t in range(n)]
print('pair0 support sizes',sum(1 for x in q if x), bin(Ma).count('1'), bin(Mb).count('1'), 'r0 in Va?',bool(Ma>>r0&1),bool(Mb>>r0&1))
print('pair0 dimV',analyse_q(q))
