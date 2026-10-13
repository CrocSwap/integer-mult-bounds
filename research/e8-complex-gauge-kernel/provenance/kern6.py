from kern5 import *
def asg_to_groups(C,asg):
    cls={}
    for h,E in asg.items():cls.setdefault(E,[]).append(h)
    groups=[]
    for E,G in cls.items():
        G=sorted(G);donors=[];rows=np.zeros((v,0))
        for h in G:
            c=C[:,h:h+1]
            if np.linalg.matrix_rank(np.hstack([rows,c]),tol=1e-8)>rows.shape[1]:rows=np.hstack([rows,c]);donors.append(h)
        pivots=[h for h in G if h not in donors]
        if pivots:groups.append((E,donors,pivots))
    return groups
if __name__=='__main__':
    w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    best,asg=pickle.load(open('kern5_best.pkl','rb'))
    groups=asg_to_groups(C,asg)
    print([(E[0],len(d),len(p)) for E,d,p in groups])
    pre,start,eps=groups_to_pre(col,groups)
    print('pre ops',len(pre),'eps',eps)
    rep,edges=check(w,pre=pre,start=start)
    print('exact',rep['exact_arbitrary_dirt'],rep['exact_inverse_transpose'],rep['local_profile'],'sumwidth',sum(rep['widths']),'newedges',len(edges))
    r=HM.evaluate(rep['local_profile'],rep['widths'],exact=True)
    r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560,exact=True)
    print('b',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),'W',r['W'],r['banks'],'hosted',r['hosted'])
    pickle.dump((pre,start),open('kern6_word.pkl','wb'))
