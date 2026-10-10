"""phi of a shared-donor selection; trims to a total entrance rank divisible by 5 (width-100 bank tiling). Usage: trim5.py HELPERS.pkl SEL.json OUT.json
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import pickle,sys,json,math
d=pickle.load(open(sys.argv[1],'rb'));sel=json.load(open(sys.argv[2]))
ff=d['firstframe'];ft=d['ftab'];phi=lambda r:0.0 if r<=0 else r*math.log(100/r);dim=lambda s:ft[ff[s]]['dim']
rk=lambda e:len(e['basis']) if e.get('basis') else 1
def total(S):
    don={}
    for e in S:
        for m in e['donors']:don[m]=rk(e)
    return sum(phi(dim(e['pivot'])-rk(e))-phi(dim(e['pivot'])) for e in S)+sum(phi(r)+phi(dim(m)-r)-phi(dim(m)) for m,r in don.items())
S=list(sel);print('entries',len(S),'rank',sum(map(rk,S)),'phi %.3f'%total(S))
while sum(map(rk,S))%5:
    best=min(range(len(S)),key=lambda i:total(S[:i]+S[i+1:]))
    S=S[:best]+S[best+1:]
print('trimmed',len(S),'rank',sum(map(rk,S)),'phi %.3f'%total(S))
json.dump(S,open(sys.argv[3],'w'))
