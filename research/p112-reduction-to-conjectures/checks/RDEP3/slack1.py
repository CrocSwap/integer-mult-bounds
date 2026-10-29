# impl 1: slack(wR,wA) = max(1,wR+wA-9) - (7 - lam(wR) - lam(wA)), lam(w)=min(6,(8-w)^+)
lam=lambda w: min(6,max(0,8-w))
S={(a,b): max(1,a+b-9)-(7-lam(a)-lam(b)) for a in range(1,10) for b in range(1,10)}
assert min(S.values())>=0
print('   '+' '.join(str(b) for b in range(1,10)))
for a in range(1,10): print(a,'|',' '.join(str(S[a,b]) for b in range(1,10)))
print('zero-slack pairs:',sorted(k for k,v in S.items() if v==0 and k[0]<=k[1]))
