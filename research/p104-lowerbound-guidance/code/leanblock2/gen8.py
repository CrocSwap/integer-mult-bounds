import sys; sys.set_int_max_str_digits(0)
exec(open('chk.py').read().split("import functools")[0])
def lam1(a):
    m=0
    for t,l in enumerate(lab):
        if par(a&l)==0: m|=1<<t
    return m
L8=[];W=[0]*512
for a in range(1,512):
    L=lam1(a)
    w=next((i for i,f in enumerate(frames) if f&L==0),None)
    if w is None: L8.append(a); W[a]=759
    else: W[a]=w
print(len(L8))
# 8-dim blocking containing a listed 7-dim? 
packed=sum(W[a]<<(12*a) for a in range(512))
bm=0
for a in L8: bm|=1<<a
with open('data8.lean','w') as f:
    f.write("def L8 : List Nat := %s\n"%L8)
    f.write("def tab8 : Nat := %d\n"%packed)
    f.write("def bm8 : Nat := %d\n"%bm)
