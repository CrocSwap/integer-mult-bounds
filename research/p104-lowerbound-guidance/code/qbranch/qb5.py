import sys
exec(open('qb1.py').read().split("if __name__")[0])
def test(k):
    ells=list(range(3,k+1)); wm=1-(9**s-8**s)
    ev=(k%2==0)
    P=tuple([2]*(k//2)+[1]*(k%2)); vh=val(k,P); m=k%2
    # T from hub tight: vh-1+wm*m+T*rho=0, rho=sum_{L<l}L(k-L)/(k-1) (l>=3) for hub pieces 1,2
    rho=(P.count(2)*2*(k-2)+P.count(1)*(k-1))/(k-1)
    T=(1-vh-wm*m)/rho
    res=[]
    for l in [3,4,k//2,k-1,k]:
        w=np.zeros(1+len(ells)); w[0]=wm; w[1+ells.index(l)]=T
        pr=price(k,w,0,ells,1,k,0); mx=max((sc-1,D,P_) for sc,D,P_ in pr)
        res.append((l,round(mx[0],9),mx[1],mx[2] if len(mx[2])<8 else '...'))
    return T,res
for k in map(int,sys.argv[1:]): print(k,test(k))
