#!/usr/bin/env python3
"""Root-executed literal v14 three-factor/cache discriminator.

Four main banks have owner dimensions (112,8,112,8). The two retained
cache banks each have eight owners. No terminal decoder is presumed.
"""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
CALLER=HERE.parent/'caller'
STAGES=3
EXPECTED={
 'PARAMETRIC-BACKWARD-v14.json':'46d03d354dde49392f1f084c048906b83e78b59c6b8305e3c7f5944cc732fe43',
 'PARAMETRIC-INVERSE-v14.json':'14ded744373f64a2fa81b9602c24e4cb38583109cbc828b551762e30bb163543',
 'PARAMETRIC-FORWARD-v14.json':'f52bed333ac9f4e73d8000cdf4281adb844229593d863bdbc1a1f2f156c90dd6',
 'PARAMETRIC-HCODE-v14.json':'d065d98d97fc772e567a0f2bf3e3f308e0d9372c6a8c0ffd6368c05a6ea1a90a',
 'PARAMETRIC-HCODE-INVERSE-v14.json':'8843dc8bb5b69c1246ff595d97f2583d256fbd829f6d7a1cfc629dc8dc8a4f35'}

def need(ok,msg):
    if not ok: raise ValueError(msg)

@lru_cache(None)
def word_normal(word):
    out=[]; coefficient=F(1)
    for item in word:
        if item[0]=='q':
            e=item[1]%4
            if not e:continue
            if out and out[-1][0]=='q':
                e=(out.pop()[1]+e)%4
                if e:out.append(('q',e))
            else:out.append(('q',e))
        elif item[0]=='w' and out and out[-1]==('z',item[1]):
            out.pop();coefficient*=14
        else:out.append(item)
    return tuple(out),coefficient

def action(d,word):
    out=[]
    for token in word:
        if token[0] in ('w','z'):
            k=d[token[1]]
            out.extend((('q',-k),token,('q',k)))
        else:out.append(token)
    return tuple(out)

class R:
    def term(self,w=(),d=(0,0,0),c=1):
        w,b=word_normal(tuple(w));c=F(c)*b
        return {(w,tuple(d)):c} if c else {}
    @property
    def one(self):return self.term()
    def add(self,*items):
        out=defaultdict(F)
        for item in items:
            for key,c in item.items():out[key]+=c
        return {k:c for k,c in out.items() if c}
    def scale(self,a,c):return {k:v*F(c) for k,v in a.items() if v*F(c)}
    def mul(self,*items):
        out=self.one
        for item in items:
            fresh=defaultdict(F)
            for (w,d),c in out.items():
                for (v,e),b in item.items():
                    u,k=word_normal(w+action(d,v))
                    fresh[u,tuple(x+y for x,y in zip(d,e))]+=c*b*k
            out={k:c for k,c in fresh.items() if c}
        return out
    def q(self,e=1):return self.term((('q',e),))
    def w(self,s):return self.term((('w',s),))
    def z(self,s):return self.term((('z',s),))
    def d(self,s,e=1):
        d=[0]*3;d[s]=e;return self.term(d=d)
    def neg(self,a):return self.scale(a,-1)
    def I(self,n):return [[self.one if i==j else {} for j in range(n)] for i in range(n)]
    def mm(self,a,b):
        return [[self.add(*(self.mul(a[i][k],b[k][j]) for k in range(len(b))))
                 for j in range(len(b[0]))] for i in range(len(a))]

r=R()

def code(s,inverse=False):
    w,z=r.w(s),r.z(s)
    return [[r.one,w],[r.neg(z),r.term(c=-13)]] if inverse else [
        [r.add(r.one,r.neg(r.mul(w,z))),r.neg(w)],[z,r.one]]

def bank_code(s,bank,inverse=False):
    out=r.I(4);a=code(s,inverse)
    for i in range(2):
        for j in range(2):out[2*bank+i][2*bank+j]=a[i][j]
    return out

def diag_operator(t):return [[t if i==j else {} for j in range(4)] for i in range(4)]
def source_q2():
    out=r.I(4);out[0][0]=out[1][1]=r.q(2);return out

def native_b(s):
    out=r.I(4);a=code(s)
    for i in range(2):
        for j in range(2):out[i][j+2]=r.neg(r.mul(r.q(),a[i][j]))
    return r.mm(diag_operator(r.d(s)),out)

def proper_f(s):
    out=r.I(4);a=code(s)
    for i in range(2):
        for j in range(2):out[i+2][j]=r.mul(a[i][j],r.q(-1))
    return r.mm(diag_operator(r.d(s)),out)

def native_query(s,rows):
    # Native B prefeed t=q*(Z*y+h), before h+=Z*y.
    return [r.mul(r.q(),r.add(r.mul(r.z(s),rows[2][j]),rows[3][j])) for j in range(4)]

def encode(poly):
    return [{'coefficient':str(c),'word':[[t[0],t[1]] for t in w],'D_exponents':list(d)}
            for (w,d),c in sorted(poly.items(),key=lambda x:str(x[0]))]
def encode_rows(rows):return [[encode(p) for p in row] for row in rows]

def check_types(poly,output_type,input_type):
    for (word,d),coefficient in poly.items():
        typ=input_type
        for kind,s in reversed(word):
            if kind=='w':need(typ=='h','W domain');typ='p'
            elif kind=='z':need(typ=='p','Z domain');typ='h'
            else:need(kind=='q','known token')
        need(typ==output_type,'typed field map')

def main():
    pins={}
    for name in ('PARAMETRIC-BACKWARD-v14.json','PARAMETRIC-INVERSE-v14.json',
                 'PARAMETRIC-FORWARD-v14.json','PARAMETRIC-HCODE-v14.json',
                 'PARAMETRIC-HCODE-INVERSE-v14.json'):
        raw=(CALLER/name).read_bytes();data=json.loads(raw);pins[name]=sha256(raw).hexdigest()
        need(pins[name]==EXPECTED[name],'frozen v14 file hash '+name)
        need(data.get('complete_caller') is False,'retain local-only status')
    a,ai=code(0),code(0,True)
    need(r.mm(a,ai)==r.I(2) and r.mm(ai,a)==r.I(2),'H1 both inverse products')
    u=[[r.z(0),r.one]]
    need(r.mm(u,ai)==[[{},r.one]],'U H1 inverse selects only h')

    rows=r.I(4);caches=[];events=[]
    # F0: the explicit noninvolutive natural B-swap wrapper, not a
    # guessed replacement of Aq^-1 by qA.
    rows=r.mm(source_q2(),rows)
    rows=r.mm(bank_code(0,0,True),rows)
    jinv=r.I(4);j=r.I(4)
    for i in range(4):
        jinv[i]=[{} for _ in range(4)];j[i]=[{} for _ in range(4)]
    for i in range(2):
        jinv[i][i+2]=r.one;jinv[i+2][i]=r.term(c=-1)
        j[i][i+2]=r.term(c=-1);j[i+2][i]=r.one
    rows=r.mm(jinv,rows)
    cache0=native_query(0,rows)
    expect0=[{},r.neg(r.q(-1)),{},{}]
    need(cache0==expect0,'natural F0 saved query is pure -q^-1 k')
    rows=r.mm(native_b(0),rows)
    rows=r.mm(j,rows)
    rows=r.mm(bank_code(0,1,True),rows)
    rows=r.mm(source_q2(),rows)
    caches.append([r.mul(r.d(0),p) for p in cache0])
    events.append({'op':'F0_NATURAL_CALLER','chronology':[
        'source bank q^2','source H0 inverse','J inverse','native B0, COPY eight query results to caller-owned cache0',
        'J','target H0 inverse','source bank q^2','eight paid D0 calls on retained cache0'],
        'cache0_raw':encode_rows([cache0]),'cache0_after_D0':encode_rows([caches[0]])})
    after0=rows

    # B1 is literal v14 native main map, with no claimed middle uncode.
    rows=r.mm(native_b(1),rows)
    events.append({'op':'B1_NATIVE_UNRECODED','no_middle_uncoding_assumed':True})
    after1=rows

    # F2 proper inverse-enabled main map. The caller recodings are literal:
    # target H2 before F, source H2 after F. Its inverse-prefeed query,
    # retained before the final clear and given the wrapper D2^2 translation,
    # equals D2*(Z2*q^-1*x+q^-1*k) on the pre-F source bank.
    rows=r.mm(bank_code(2,1,False),rows)
    cache2=[r.mul(r.d(2),r.add(r.mul(r.z(2),r.q(-1),rows[0][j]),
                              r.mul(r.q(-1),rows[1][j]))) for j in range(4)]
    rows=r.mm(proper_f(2),rows)
    rows=r.mm(bank_code(2,0,False),rows)
    caches.append(cache2)
    events.append({'op':'F2_PROPER_RECODED','chronology':[
        'target H2','actual inverse-enabled proper F2, retain eight inverse-prefeed query results',
        'apply D2^2 monomial to retained cache2 as in proper F wrapper','source H2'],
        'cache2_after_monomial':encode_rows([cache2]),'extra_cache_gaussians':0})
    after2=rows

    # The p1 controller's terminal signed swap is kept literal. No scalar
    # boundary fitting, input code absorption, or output decoding is done.
    rows=[rows[2],rows[3],[r.neg(p) for p in rows[0]],[r.neg(p) for p in rows[1]]]
    kinds=('p','h','p','h')
    for i,row in enumerate(rows):
        for k,poly in enumerate(row):check_types(poly,kinds[i],kinds[k])
    for row in caches:
        for k,poly in enumerate(row):check_types(poly,'h',kinds[k])

    result={'schema_version':1,'status':'EXACT_TYPED_THREE_FACTOR_MAIN_AND_RETAINED_CACHE_ROWS',
      'main_bank_order':['x:112','k:8','y:112','h:8'],
      'cache_order':['cache0:8','cache2:8'],
      'main_input_directions':240,'retained_cache_owner_fields':16,
      'source_pins':pins,
      'stage_embedding':{'central_axis':0,'noncentral_axes':{'0':list(range(1,9)),
                         '1':list(range(9,17)),'2':list(range(17,25))},
                         'one_stage_operator':'D_s=product C on its eight fresh axes; q=C on axis0; R_s=D_s q'},
      'physical_operator_definitions':{'W_s':'diag(Kp_s^-1) M diag(Km_s)/2',
          'Z_s':'diag(Km_s^-1) M^T diag(Kp_s)/2',
          'H1_s':'[[I-W_s Z_s,-W_s],[Z_s,I]]'},
      'formal_relations':['q^4=I','D_s commute q and each other',
          'D_s conjugates W_s,Z_s by q^-1 (...) q; D_t commutes W_s,Z_s if t!=s',
          'Z_s W_s=14I8, coefficient14 exterior'],
      'literal_events':events,
      'rows_after_F0':encode_rows(after0),'rows_after_B1':encode_rows(after1),
      'rows_after_F2_before_signed_swap':encode_rows(after2),
      'final_main_rows':encode_rows(rows),'final_retained_cache_rows':encode_rows(caches),
      'additional_resources_beyond_three_v14_full_calls':{
          'paid_H8':8,'paid_H1':0,'caller_owned_fields':16,
          'query_cache_COPY':16,'query_cache_final_CLEAR':16,
          'cache2_D_squared_monomial_fields':8},
      'ownership':'All16caller-owned cache fields start arbitrary and are CLEARed before COPY. Nativeprovider9owned fields remain separate. Cache0 is copied before B0 provider; cache2 is copied from inverse-prefeed queries after its native inverse. CLEAR caches only after all proposed caller reads. No productive original owner is erased.',
      'tail_boundary':'Neither cache receives later D1 or D2 unless explicitly shown. Cache0 gets only D0; cache2 gets the D2^2 monomial from F2. No free Gaussian tail transport is claimed.',
      'proved_local_identities':['H1 inverse both products','U H1 inverse=[0,I]',
          'F0 raw query cache=-q^-1 original k','all four main bank columns and both typed cache rows explicitly composed'],
      'complete_gaussian_endpoint':False,'complete_caller':False,'gain_claimed':False,
      'scope':'Exact compressed all-owner-column formula within inherited v14 local ABI and listed source operator relations. No all-f Gaussian endpoint claim; a formal residual alone is not a physical counterexample.'}
    (HERE/'THREE-FACTOR-CACHE-ROWS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','main_input_directions','retained_cache_owner_fields','additional_resources_beyond_three_v14_full_calls','complete_caller')},sort_keys=True))

if __name__=='__main__':main()
