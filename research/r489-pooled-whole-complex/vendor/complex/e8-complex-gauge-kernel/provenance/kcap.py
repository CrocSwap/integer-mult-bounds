from fractions import Fraction as Q
def kappa_of(s_in,eta=Q(1,10**18),beta=Q(1,10**18)):
    s=Q(s_in)-Q(1,10**24)
    a=Q(384599,10**10)
    for _ in range(6):a=(1-s)*s+s*a
    q=a*(1-2*eta);margin=(1-eta)*q/(1+q);grid=Q(1,10**18);ticks=margin/grid
    return grid*((ticks.numerator-1)//ticks.denominator)
def cap_from_b(b):return float(kappa_of((1-Q(1,10**18))*Q(b)))
if __name__=='__main__':
    c=Q('1239085165241180038597')/Q(10**24)
    print('check kappa(c bit)',float(kappa_of(c)),'expected 0.001237551733247294')
    for name,b in (('baseline cx hosted',1.267453159029119e-3),('kernel77',1.309121737234019e-3),('gauge70+kernel44 (model)',1.329163e-3)):
        print(name,'b',b,'kappa cap',cap_from_b(Q(b).limit_denominator(10**18)))
