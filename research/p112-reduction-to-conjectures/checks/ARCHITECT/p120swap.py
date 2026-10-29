# P120: (i) max #lines of Off(c_v) in a 7-dim label subspace (need < 57-13 = 44 so a swap row keeps w >= 8);
# (ii) every hyperplane z^perp misses how many lines of Off(c_v) (frame-type analogue not needed on P120).
exec(open('p120cat.py').read().split("# (a)")[0])
v0=0; Off=frozenset(t for t in range(v) if G[v0,t]!=0)
print('|Off(c_v)|',len(Off))
best7=0
keys=list(O.keys())
for i,a in enumerate(keys):
    for b in keys[i+1:]:
        cnt=len(Off-(O[a]|O[b]))
        best7=max(best7,cnt)
print('(i) max |Off ∩ 7-dim label subspace| =',best7,'(need < 44)')
print('(ii) max |Off ∩ hyperplane| =',max(len(Off-O[a]) for a in keys))
