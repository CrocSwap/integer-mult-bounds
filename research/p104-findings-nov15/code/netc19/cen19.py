import sys,collections,pickle
exec(open('../NETC18/gate18.py').read().split("res={}")[0])
nh,G,dim=census(W5+'NETC15/glob_p.json.gz')
cc=collections.Counter(g[1] for g in G)
top=cc.most_common(15)
for c,n in top:
    fr=set(g[2] for g in G if g[1]==c); hs=set(g[0] for g in G if g[1]==c); rs=set(g[4] for g in G if g[1]==c)
    print(n,'keys',len(c),sorted(c)[:3],'frames',len(fr),'helpers',len(hs),'recv',len(rs),flush=True)
pickle.dump((top,[g for g in G if g[1] in dict(top[:12])]),open('cen19.pkl','wb'))
