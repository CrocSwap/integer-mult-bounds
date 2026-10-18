import sys,json,gzip;sys.path.insert(0,'/tmp/don');from slot import *
# spec: list of moves {E,X,assign:{"t:src":newsrc},dons:[[t,src_orig,H]]}
def locate(w,mv):
    B=w['B'];E,X=mv['E'],mv['X']
    ci=[i for i,g in enumerate(B) if g[0]=='add' and g[1]==E and g[2]==X and g[3]==1 and g[4]==1]
    assert len(ci)==1,(E,X,ci); ci=ci[0]
    _,_,reads,pre=slot_info(w,ci)
    key={'%d:%d'%(t,s):i for (i,t,s,c) in reads}
    assert len(key)==len(reads)
    a={key[k]:v for k,v in mv['assign'].items()}
    for (i,t,s,c) in reads: a.setdefault(i,s)
    dons=[]
    for t,s,H in mv['dons']:
        i=key['%d:%d'%(t,s)]
        iH=[j for j,g in enumerate(B) if g[0]=='add' and g[1]==t and g[2]==H and j>ci]
        assert len(iH)==1; dons.append((i,H,iH[0]))
    return ci,a,dons
def compose(w,moves):
    from frameopt import optimise
    for mv in moves:
        ci,a,dons=locate(w,mv)
        w=build(w,ci,a,dons)
        w,info=optimise(w)
        assert w is not None
    for i,U in w['early_cleanup']: w['cleanup'][i]=w['cleanup'][i][:-1]+[list(U)]
    P=profile(w);w['report']['local_profile']={str(k):v for k,v in P.items()}
    return w,P
if __name__=='__main__':
    w=L(sys.argv[1]);moves=json.load(open(sys.argv[2]))
    w,P=compose(w,moves);print(P)
    open(sys.argv[3],'wb').write(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
