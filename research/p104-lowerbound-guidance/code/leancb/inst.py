import json,re
d=json.load(open('<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/e8base.json'))
C=d['C'][:104]; G=d['Gb']
src=open('<research-tree>/lean/decoder-duality/Nov15/LinP104Base.lean').read()
def lst(name):
    m=re.search(r'def '+name+r' : List Nat := \[([^\]]*)\]',src); return [int(x) for x in m.group(1).split(',')]
X=lst('xMasks'); LM=lst('labMasks')
ok=all(all(((C[t][i])%2)==((X[t]>>i)&1) for i in range(8)) for t in range(104))
print('mod2 labels match',ok)
def Q(t,s): return bin(LM[t]&LM[s]&511).count('1')%2
bad=0
for t in range(104):
    for s in range(104):
        ip=sum(C[t][i]*G[i][j]*C[s][j] for i in range(8) for j in range(8))
        if ip*Q(t,s)!=(2 if t==s else 0): bad+=1
print('bad cells',bad)
json.dump(C,open('ct.json','w'))
