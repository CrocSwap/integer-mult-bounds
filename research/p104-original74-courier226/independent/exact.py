"""Independent exact row and provider-bank primitives; no source is loaded here."""
from fractions import Fraction as Q

class Reject(Exception):
    def __init__(self, code, **detail):
        self.code, self.detail = code, detail
        super().__init__(code)

def require(ok, code, **detail):
    if not ok: raise Reject(code, **detail)

def add(a, b, q=Q(1)):
    out = a.copy()
    for k,v in b.items():
        v = out.get(k,Q(0)) + q*v
        if v: out[k] = v
        else: out.pop(k,None)
    return out

def diff(a,b):
    d=add(a,b,Q(-1))
    return None if not d else {'input_column':min(d),'difference':str(d[min(d)])}

def reconstruct(target, providers):
    """Solve target from an ordered, explicitly bounded provider bank over Q.

    A nonzero remainder excludes this bank only. Coefficients are independently
    substituted before return. Provider chart and liveness must be checked by caller.
    """
    require(len({r for r,_ in providers})==len(providers),'duplicate_provider')
    basis={}
    for role,row in providers:
        v=row.copy(); combo={role:Q(1)}
        while v:
            p=min(v)
            if p not in basis:
                factor=v[p]
                basis[p]=({k:x/factor for k,x in v.items()},
                          {k:x/factor for k,x in combo.items()})
                break
            b,c=basis[p]; q=v[p]; v=add(v,b,-q); combo=add(combo,c,-q)
    rem=target.copy(); result={}
    while rem:
        p=min(rem)
        if p not in basis:
            return {'status':'bank_excluded','rank':len(basis),'residual_column':p,
                    'residual_coefficient':str(rem[p])}
        b,c=basis[p]; q=rem[p]; rem=add(rem,b,-q); result=add(result,c,q)
    actual={}; lookup=dict(providers)
    for role,q in result.items(): actual=add(actual,lookup[role],q)
    require(actual==target,'internal_span_substitution_failure')
    return {'status':'exact_bank_span','rank':len(basis),
            'coefficients':{str(k):str(v) for k,v in sorted(result.items())}}

def spans(frames):
    result=[]
    for f in frames:
        span={0}
        for x in f:
            require(type(x) is int and x>0 and x not in span,'invalid_frame')
            span |= {x ^ y for y in tuple(span)}
        result.append(frozenset(span))
    return result

class Interpreter:
    def __init__(self, word):
        self.w=word; self.n=word['public']; self.N=self.n+word['owned_fields']
        self.sp=spans(word['frames']); self.rows=[{r:Q(1)} if r<self.n else {} for r in range(self.N)]
        self.chart=list(word['initial'])+[None]*(self.N-self.n)
        self.live=set(range(self.n)); self.peak=0; self.birth={}; self.lifetimes=[]

    def snapshot(self, roles):
        return {r:(r in self.live,self.chart[r],self.rows[r].copy()) for r in roles}

    def witness(self,clock,cert):
        e=self.w['program'][clock]; r=e[1]
        require(e[0]=='CLEAR' and r in self.live and self.chart[r]==e[2], 'clear_chart',clock=clock,role=r)
        v={}; charts={}
        for key,q in cert.items():
            role=int(key); require(role in self.live and role!=r,'provider_not_live',clock=clock,role=role)
            charts[role]=self.chart[role]; v=add(v,self.rows[role],Q(q))
        require(v==self.rows[r],'clear_relation',clock=clock,role=r,difference=diff(v,self.rows[r]))
        return charts

    def step(self, clock):
        e=self.w['program'][clock]; op,r=e[:2]
        require(type(r) is int and 0<=r<self.N,'bad_role',clock=clock)
        if op=='INIT':
            require(r>=self.n and r not in self.live and self.chart[r] is None,'bad_init',clock=clock,role=r)
            self.live.add(r); self.chart[r]=e[2]; self.rows[r]={}; self.birth[r]=(clock,e[2]); self.peak=max(self.peak,len(self.live)-self.n)
        elif op=='CLEAR':
            require(r>=self.n and r in self.live and self.chart[r]==e[2],'bad_clear',clock=clock,role=r)
            self.lifetimes.append((r,self.birth.pop(r),clock,e[2])); self.live.remove(r); self.chart[r]=None; self.rows[r]={}
        elif op=='MOVE':
            a,b,owned=e[2:]
            require(r in self.live and self.chart[r]==a and type(owned) is bool and owned==(r>=self.n),'bad_move',clock=clock,role=r)
            require(self.sp[a]<self.sp[b] or (owned and self.sp[b]<self.sp[a]),'move_not_nested',clock=clock,role=r)
            self.chart[r]=b
        elif op=='SCALE':
            q=Q(e[2]); require(r in self.live and self.chart[r]==e[3] and q!=0,'bad_scale',clock=clock,role=r)
            self.rows[r]={k:q*v for k,v in self.rows[r].items()}
        elif op in ('ADD','COPY'):
            s,q,f=e[2],Q(e[3]),e[4]
            require(s!=r and r in self.live and s in self.live and self.chart[r]==self.chart[s]==f and q!=0,'bad_scalar',clock=clock,role=r)
            if op=='COPY': require(not self.rows[r],'copy_nonzero',clock=clock,role=r)
            self.rows[r]=add(self.rows[r],self.rows[s],q)
        else: raise Reject('unknown_op',clock=clock,op=op)

    def end(self):
        require(self.live==set(range(self.n)) and self.chart[:self.n]==self.w['final'],'bad_final_boundary')
