lam=lambda w:min(6,max(0,8-w))
S={(a,b):max(1,a+b-9)-(7-lam(a)-lam(b)) for a in range(1,10) for b in range(1,10)}
S0={(a,b):max(0,a+b-9)-(7-lam(a)-lam(b)) for a in range(1,10) for b in range(1,10)}
for a in range(1,10): print(a,'|',' '.join(str(S[a,b]) for b in range(1,10)))
print('min slack',min(S.values()),'| sound (no P0) slack<0 cells:',[k for k,v in S0.items() if v<0],[S0[k] for k in S0 if S0[k]<0])
# closed form check
cf=lambda a,b:(a==9)*(b>=2)+(b==9)*(a>=2)+(max(0,10-max(a,2)-max(b,2)) if a<=8 and b<=8 else 0)
print('closed form matches:',all(cf(a,b)==S[a,b] for a,b in S),[k for k in S if cf(*k)!=S[k]])
