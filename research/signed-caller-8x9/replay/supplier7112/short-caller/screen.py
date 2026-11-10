import hashlib,json,sys
from fractions import Fraction
from pathlib import Path

P=97
N=38

def mod(x):
    f=Fraction(x);return f.numerator*pow(f.denominator,-1,P)%P

def eye():return [[int(i==j) for j in range(N)] for i in range(N)]

def screen(caller,phase,body,hosts=None):
    F=eye();I=eye();out={}
    def scale(r,c):
        F[r]=[x*c%P for x in F[r]];d=pow(c,-1,P)
        for row in I:row[r]=row[r]*d%P
    def add(r,s,c):
        F[r]=[(x+c*y)%P for x,y in zip(F[r],F[s])]
        for row in I:row[s]=(row[s]-c*row[r])%P
    def mul2(r,s,a,b,c,d):
        X,Y=F[r],F[s]
        F[r]=[(a*x+b*y)%P for x,y in zip(X,Y)]
        F[s]=[(c*x+d*y)%P for x,y in zip(X,Y)]
        t=pow((a*d-b*c)%P,-1,P)
        for row in I:
            x,y=row[r],row[s]
            row[r]=(d*x-c*y)*t%P;row[s]=(-b*x+a*y)*t%P
    for idx,event in enumerate(caller['events']):
        ty=event[0]
        if ty=='J':
            j=event[1];u,v,alpha,beta=event[3];a,b=mod(alpha),mod(beta);t=body[j-1]
            if hosts is not None:
                hosts[j]=[(list(row[r] for row in I),F[r][:]) for r in (u-38,v-38)]
            mul2(u-38,v-38,t,t*a*phase%P,t*b*pow(phase,-1,P)%P,t*(1+a*b)%P)
        elif ty=='B':
            op=event[1];r=event[2]-38
            if op=='ADD':add(r,event[3]-38,mod(event[4]))
            elif op=='QUERY':add(r,event[3]-38,pow(phase,event[4],P))
            elif op=='SCALE':scale(r,mod(event[3]))
            elif op=='SWAP':
                s=event[3]-38;F[r],F[s]=F[s],F[r]
                for row in I:row[r],row[s]=row[s],row[r]
            elif op=='LAMBDA':
                i=22*event[3];scale(r,((1+i)+(1-i)*phase**2)*pow(2,-1,P)%P)
            elif op=='IDLE_ONE':
                col=[row[r] for row in I];row=F[r][:]
                out[idx]=(col,row)
                m=1
                for k in event[3]:m=m*body[k-1]%P
                scale(r,m)
            else:raise ValueError(event)
    for r,(q,_,*mask) in enumerate(caller['types']['B']['diagonal']):
        c=pow(phase,q,P)
        for k,v in enumerate(mask):
            if v:c=c*body[k]%P
        assert F[r]==[c*int(r==s) for s in range(N)]
    return out

def identify(proj):
    c,r=proj;cx=[i for i,x in enumerate(c) if x];rx=[i for i,x in enumerate(r) if x]
    return cx[0] if len(cx)==1 and cx==rx else None

def main(path):
    raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=='3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e'
    caller=json.loads(raw)
    results=[screen(caller,phase,body) for phase in (1,96,22,75) for body in ([1]*18,list(range(2,20)))]
    exact_candidates=[];profiles=[]
    for idx in results[0]:
        ids=[identify(v[idx]) for v in results]
        profiles.append({'event':idx,'op':caller['events'][idx],'diagonal_row_per_probe':ids})
        if ids[0] is not None and len(set(ids))==1:exact_candidates.append([idx,ids[0]+38])
    print(json.dumps(dict(caller_sha256=h,finite_field=P,probes=len(results),candidates=exact_candidates,profiles=profiles),indent=2))

if __name__=='__main__':main(Path(sys.argv[1]))
