import sys; sys.argv=[sys.argv[0]]
exec(open('qb1.py').read().split("if __name__")[0])
import sys as _s
for k in [10,13,16,24,32,48,72,128]:
    c1,s1=solve(k,False); print(k,'HP',round(HP(k),3),'Qge1',round(c1,3),[t for t in s1 if t[0]>0.5][:8],flush=True)
