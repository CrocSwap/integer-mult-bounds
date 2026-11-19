"""Independent all-input, bit-sliced gate replay, including full inverse tape restoration."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from tape import Layout, X,D,Q, initial, program, run, step, wire


def require(ok,detail):
    if not ok:
        raise ValueError(detail)


def parallel(gates,state,mask):
    # Each physical track is a Python bit-vector; lane i runs input i.
    # This oracle checks every intermediate gate against the nearest-neighbour condition.
    for g in gates:
        require(len(set(g))==len(g) and max(g)//8-min(g)//8<=1, "nonlocal gate")
        update=mask
        for w in g[:-1]:
            update &= state[w]
        state[g[-1]] ^= update


def slice_rows(rows):
    return [sum(x<<i for i,x in enumerate(bits)) for bits in zip(*rows,strict=True)]


def readouts(layout,Dval,n,nearest):
    scaled = Fraction(n,1)*2**layout.p / (Dval*2**layout.e)
    den = Dval << layout.s
    num = n << max(layout.p-layout.e,0)
    floor,res=divmod(num,den)
    answer = round(scaled) if nearest else floor
    return answer,res,int(answer!=floor)


def expected(layout,d,n,nearest):
    q,r,flag=readouts(layout,d,n,nearest)
    state=initial(layout,d,0)
    bits = layout.m+layout.k+layout.s
    final_data=(q << (layout.k+layout.s))|r
    for i in range(bits):
        state[wire(i,X)] = (final_data >> (bits-1-i))&1
    state[wire(layout.m,Q)]=flag
    return state


def small():
    cases=0
    for d in range(1,32,2):
        for e,p in [(0,0),(0,3),(4,0),(5,1),(1,0),(2,1),(3,5)]:
            layout=Layout(8,d.bit_length(),e,p)
            initial_state=slice_rows(initial(layout,d,n) for n in range(256))
            for nearest in (False,True):
                tape=initial_state.copy()
                gates=list(program(layout,nearest))
                parallel(gates,tape,(1<<256)-1)
                require(tape==slice_rows(expected(layout,d,n,nearest) for n in range(256)),
                        ("published program",d,e,p,nearest))
                parallel(reversed(gates),tape,(1<<256)-1)
                require(tape==initial_state,"inverse restoration")
                cases+=256
    print("PASS",cases,"forward gate outputs plus exact inverse closures, including all rounding boundaries.")


def all_states(d):
    # Test every accepted residue and both next digits independently of reachability traces.
    k=d.bit_length()
    layout=Layout(2,k,0,0)
    valid=[]
    predicted=[]
    for r in range(d):
        for b in (0,1):
            w=2*r+b
            q,nxt=divmod(w,d)
            base=initial(layout,d,0)
            for j in range(k+1):
                base[wire(j,X)] = (w>>(k-j))&1
            valid.append(base)
            result=[0]*len(base)
            for j in range(k+1):
                result[wire(j,X)] = ((q<<k)|nxt)>>(k-j)&1
            for j in range(k):
                result[wire(2+j,D)] = (d>>(k-1-j))&1
            predicted.append(result)
    state=slice_rows(valid)
    gates=list(step(0,k))
    parallel(gates,state,(1<<(2*d))-1)
    require(state==slice_rows(predicted),"state map")
    require(len(gates)==29*(k+1)+3,"per digit gate invoice")
    return 2*d



def invoices():
    from convert import convert
    for s in (0,1,2,5):
        for k in (1,3,7):
            for p in (0,4):
                a=Layout(9,k,s+p,p)
                n=a.m
                w=k+1
                # Per digit plus the final return of the modulus track.
                base={1:n*(8*w+2),2:n*(10*w+1),3:n*(14*w)}
                nearest={1:4*w+2*n,2:n+3,3:6*w+2*n}
                if s:
                    nearest[2]+=2*w+4*s+2
                    nearest[3]+=2*s
                for use in (False,True):
                    result=run(program(a,use),initial(a,(1<<k)-1,0))
                    require(all(result[i]==base[i]+(nearest[i] if use else 0) for i in (1,2,3)),
                            "gate invoice")
                    require(result["moves"] <= n*(12*k+10)+20*a.sites,"head movement")
    for n in range(-9,10):
        for d,e,p in [(1,1,0),(3,1,0),(5,0,3),(7,3,1)]:
            y=convert(n,d,e,p)
            require(y["grid_integer"]==round(Fraction(n<<p,d<<e)),"signed tie / nearest")
            require(abs(n)<<max(p-e,0)==(d<<max(e-p,0))*(abs(y["grid_integer"])-y["increment"])+y["exact_residue"],"recover exact input")
    print("PASS exact primitive gate invoices, head travel bounds, signed ties and input reconstruction.")

if __name__=="__main__":
    invoices()
    small()
    print("PASS",sum(all_states(d) for d in range(1,128,2)),"reachable transitions at odd D < 128.")
