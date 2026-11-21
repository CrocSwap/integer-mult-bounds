import sys,re; sys.set_int_max_str_digits(0)
exec(open('chk.py').read().split("import functools")[0])
i=src.index('def certs0 : List (List Nat) := [')
line=src[i:].split('\n')[1]
u1,u2,p0=[int(x) for x in line.strip('[').split(',')[:3]]
print(u1,u2,p0)
L=[t for t,l in enumerate(lab) if par(u1&l)==0 and par(u2&l)==0]
print(len(L),L, p0 in L)
rows=[];ports=[]
def reduce(v,rows):
    for r in rows: v=min(v,v^r)
    return v
for t in L:
    v=reduce(lab[t],rows)
    if v: rows.append(v); ports.append(t)
print(ports,[lab[t] for t in ports])
