from lawler799 import *
import sys
P0=sys.argv[1] if len(sys.argv)>1 else (__import__('os').environ['HM_ROOT']+'/inputs/words/799-X4-CANONICAL-WORD.json.gz')
d,v,SEQ,Lpre,copies,P=run(P0)
cnt=collections.Counter();sizes=[]
for kind,a,b,k in copies:
    base=Lpre[k][1];sink={a,b};V=[];chain=[]
    for x in (a,b):
        for kk in range(k+1,len(SEQ)):
            t,s=SEQ[kk]
            if x not in (t,s):continue
            qq=s if t==x else t
            g=Lpre[kk][1] if t==x else Lpre[kk][0]
            V.append((g,[P[w] for w in taint_from(SEQ,v,P,qq,kk,sink)]));chain.append(x)
    conf=[(i,j) for i in range(len(V)) for j in range(i+1,len(V)) if chain[i]!=chain[j] and lawler([V[i],V[j]],base)[0] is None]
    cnt[(kind,'pair-conflict' if conf else 'no-pair-conflict')]+=1
print(cnt)
