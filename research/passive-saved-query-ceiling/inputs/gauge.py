#!/usr/bin/env python3
"""Exact deferred-code identities in a noncommutative Laurent group algebra.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent

def require(ok,message):
    if not ok: raise ValueError(message)

def reduce_word(word):
    out=[]
    for x in word:
        if out and out[-1]==-x: out.pop()
        else: out.append(x)
    return tuple(out)

class Algebra:
    """Q and all C_i freely generate; D_i conjugates only C_i by Q^-1.

    D_i commute each other and Q. Extra generator B commutes all D_i,
    but commutes neither Q nor any C_i. This semidirect-product normal
    form proves the identities without imposing spurious commutativity.
    """
    def __init__(self,n): self.n=n; self.zero={}; self.one=self.term((),(0,)*n)
    def term(self,w,d,c=1):
        c=Fraction(c)
        return {(reduce_word(w),tuple(d)):c} if c else {}
    def gen(self,g): return self.term((g,),(0,)*self.n)
    def D(self,j):
        d=[0]*self.n; d[j]=1
        return self.term((),d)
    def action(self,d,word):
        out=[]
        for x in word:
            i=abs(x)-2
            k=d[i] if 0<=i<self.n else 0
            out.extend([-1]*max(k,0)+[1]*max(-k,0))
            out.append(x)
            out.extend([1]*max(k,0)+[-1]*max(-k,0))
        return reduce_word(out)
    def add(self,*xs):
        z=defaultdict(Fraction)
        for x in xs:
            for k,v in x.items(): z[k]+=v
        return {k:v for k,v in z.items() if v}
    def neg(self,x): return {k:-v for k,v in x.items()}
    def mul(self,*xs):
        z=self.one
        for x in xs:
            t=defaultdict(Fraction)
            for (w,d),v in z.items():
                for (u,e),c in x.items():
                    t[(reduce_word(w+self.action(d,u)),tuple(a+b for a,b in zip(d,e)))]+=v*c
            z={k:v for k,v in t.items() if v}
        return z
    def inv(self,x):
        require(len(x)==1,'Only monomial inverses are defined')
        ((w,d),c),=x.items(); e=tuple(-v for v in d)
        return self.term(self.action(e,tuple(-v for v in reversed(w))),e,1/c)
    def diag(self,x,y): return [[x,{}],[{},y]]
    def L(self,x): return [[self.one,{}],[x,self.one]]
    def U(self,x): return [[self.one,x],[{},self.one]]
    def mm(self,*ms):
        z=self.diag(self.one,self.one)
        for m in ms: z=[[self.add(*(self.mul(z[i][k],m[k][j]) for k in range(2))) for j in range(2)] for i in range(2)]
        return z
    def gauge(self,B):
        q=self.gen(1)
        return self.diag(B,self.mul(self.inv(q),B,q))

def local_checks():
    a=Algebra(2); Q=a.gen(1); C=a.gen(2); D=a.D(0); B=a.gen(4)
    qi=a.inv(Q); ci=a.inv(C); DD=a.diag(D,D)
    F=a.mm(DD,a.L(a.mul(C,qi))); F0=a.mm(DD,a.L(qi))
    BW=a.mm(DD,a.U(a.neg(a.mul(Q,C)))); B0=a.mm(DD,a.U(a.neg(Q)))
    fleft=a.mm(a.diag(C,a.one),F,a.diag(a.one,C),a.gauge(B))
    fright=a.mm(a.gauge(a.mul(C,B)),F0)
    bleft=a.mm(a.diag(ci,a.one),BW,a.diag(a.one,ci),a.gauge(B))
    bright=a.mm(a.gauge(a.mul(ci,B)),B0)
    require(fleft==fright,'Forward noncommutative gauge identity')
    require(bleft==bright,'Backward noncommutative gauge identity')
    require(a.mul(C,Q)!=a.mul(Q,C),'Control: C and Q must not commute')
    require(a.mul(B,Q)!=a.mul(Q,B),'Control: B and Q must not commute')
    require(a.mul(B,C)!=a.mul(C,B),'Control: previous code and fresh code must not commute')
    require(fleft!=a.mm(a.gauge(a.mul(B,C)),F0),'Wrong update order must reject')
    require(a.mm(a.diag(C,a.one),BW,a.diag(a.one,C),a.gauge(B))!=bright,'Wrong backward exponent must reject')
    return {'forward':True,'backward':True,'noncommuting_controls':3,'wrong_word_controls':2}

def idle_checks():
    a=Algebra(4); Q=a.gen(1); d=a.one; b=a.one
    for s,e in enumerate((1,-1,-1,1)):
        c=a.gen(s+2); c=c if e==1 else a.inv(c)
        b=a.mul(c,b); d=a.mul(a.D(s),d)
    expected=a.mul(a.inv(Q),b,Q)
    require(expected==a.mul(d,b,a.inv(d)),'Exact paid-IDLE conjugation')
    require(a.mm(a.diag(b,a.one),a.diag(d,d),a.diag(a.one,b))==a.mm(a.gauge(b),a.diag(d,d)),'Paid-IDLE installs code')
    dwrong=a.mul(d,a.inv(a.D(2)))
    require(expected!=a.mul(dwrong,b,a.inv(dwrong)),'Omitted stage must reject')
    return {'stages':4,'mixed_orientations':True,'missing_stage_rejected':True}

def chronology_checks(path):
    raw=path.read_bytes(); src=json.loads(raw)
    if 'middle' in src: events=src['middle']
    else:
        # Source wrapper schemas are accepted only through an explicit event field.
        events=src.get('physical_events')
        if events is None and 'case' in src: events=src['case'].get('physical_events')
        require(events is not None,'Missing physical_events')
    full=[v for v in events if v[0]=='LOCAL']; idles=[v for v in events if v[0]=='IDLE']
    require([v[1] for v in full]==[0]+list(range(1,32,2))+[32],'Exact p16 FULL stages')
    require(len(idles)==15,'Exact p16 paid-IDLE count')
    signs={v[1]:(-1 if v[3] else 1) for v in full}
    gauges=[() for _ in range(16)]; prefix_matches=[]; mismatch=None
    for index,e in enumerate(events):
        if e[0]=='LOCAL':
            _,stage,pair,back=e; gauges[pair]=((stage,signs[stage]),)+gauges[pair]
        elif e[0]=='IDLE':
            _,pair,stages=e
            gauges[pair]=tuple((s,signs[s]) for s in reversed(stages))+gauges[pair]
        elif e[0]=='ADD' and e[1]%2==0 and e[2]==e[1]+2 and e[3]==1:
            pair=e[1]//2
            if pair<7:
                require(gauges[pair]==gauges[pair+1],f'Prefix gauge bridge {pair}')
                prefix_matches.append(pair)
            elif pair==7 and mismatch is None:
                require(gauges[pair]!=gauges[pair+1],'Actual unpaid middle mismatch must remain visible')
                mismatch={'event_index':index,'from_pair':7,'to_pair':8,'left_word':gauges[7],'right_word':gauges[8]}
    require(prefix_matches==list(range(7)) and mismatch is not None,'Exact first unmatched bridge')
    return {'source_sha256':sha256(raw).hexdigest(),'full_calls':18,'paid_idles':15,'matched_prefix_bridges':prefix_matches,'first_unmatched_bridge':mismatch,'scope':'This records the candidate per-pair gauge policy; it does not prove that every whole-word policy fails.'}

def noncommutative_core(path):
    """Replay every p16 event over freely noncommuting stage letters."""
    src=json.loads(path.read_bytes()); events=src['physical_events']
    stages=[e[1] for e in events if e[0]=='LOCAL']
    n=32; a=Algebra(0)
    scalar=lambda x:a.term((),(),Fraction(x))
    ds={s:a.gen(j+1) for j,s in enumerate(stages)}
    def replay(reverse_idle=False):
        rows=[[scalar(x) for x in r] for r in src['boundaries']['right']]
        mutated=False
        def plus(i,j,c): rows[i]=[a.add(x,a.mul(scalar(c),y)) for x,y in zip(rows[i],rows[j])]
        def left(i,d): rows[i]=[a.mul(d,x) for x in rows[i]]
        for e in events:
            if e[0] in ('LOCAL','QUERY_SHEAR'):
                kind,stage,pair,back=e; x,y=2*pair,2*pair+1
                plus(x,y,-1) if back else plus(y,x,1)
                if kind=='LOCAL':left(x,ds[stage]);left(y,ds[stage])
            elif e[0]=='IDLE':
                _,pair,chosen=e; selected=list(chosen)
                if reverse_idle and not mutated and len(selected)>1:selected.reverse();mutated=True
                d=a.one
                for stage in selected:d=a.mul(ds[stage],d)
                left(2*pair,d);left(2*pair+1,d)
            elif e[0]=='ADD':plus(e[1],e[2],e[3])
            elif e[0]=='SIGNED_SWAP':
                x,y=e[1:];rows[x],rows[y]=rows[y],[a.neg(z) for z in rows[x]]
            else:raise ValueError('Unknown core event '+str(e))
        out=[]
        for weights in src['boundaries']['left']:
            out.append([a.add(*(a.mul(scalar(weights[k]),rows[k][j]) for k in range(n) if Fraction(weights[k]))) for j in range(n)])
        return out
    actual=replay(); expected=[]; words=[]
    for i,term in enumerate(src['diagonal']):
        d=a.one
        for stage in stages:
            if term[stage+1]:d=a.mul(ds[stage],d)
        expected.append([d if i==j else {} for j in range(n)])
        words.append(next(iter(d))[0])
    require(actual==expected,'Full p16 noncommutative Q=1 core identity')
    require(replay(True)!=expected,'Reversed paid-IDLE order must reject')
    return {'field_roles':32,'matrix_entries_checked':1024,'freely_noncommuting_stage_letters':18,'physical_events':len(events),'both_scalar_boundaries':True,'diagonal_words':words,'reversed_idle_rejected':True,'scope':'Independent Q=1 binding of Dugongue frame-aware-native/noncommuting-controller, crediting Cinna Davis PR4470 and Ryanson Jonathan PR4516. Not a new core theorem; physical Q-dependent boundaries remain separate.'}

def typed_caller_recipe(path):
    src=json.loads(path.read_bytes()); signs={e[1]:(-1 if e[3] else 1) for e in src['physical_events'] if e[0]=='LOCAL'}
    left_colors=[]; right_colors=[]
    for i,row in enumerate(src['boundaries']['left']):
        colors={j%2 for j,x in enumerate(row) if Fraction(x)}
        require(colors=={int(i>=16)},'Actual left boundary pure parity row')
        left_colors.append(next(iter(colors)))
    for j in range(32):
        colors={i%2 for i,row in enumerate(src['boundaries']['right']) if Fraction(row[j])}
        require(colors=={int(j>=16)},'Actual right boundary pure parity column')
        right_colors.append(next(iter(colors)))
    events=src['physical_events']
    require(all(e[1]%2==e[2]%2 for e in events if e[0]=='ADD'),'Every bridge preserves H parity')
    require(events[-16:]==[['SIGNED_SWAP',2*j,2*j+1] for j in range(16)],'Exact terminal signed-swap suffix')
    require(all(e[0]!='SIGNED_SWAP' for e in events[:-16]),'No earlier signed swaps cross H')
    require([x[0] for x in src['diagonal']]==[-1]*16+[1]*16,'Exact target central signs')
    emitted=[]; code_evaluations=0; positive=0; negative=0
    def code(side,pair,word):
        nonlocal code_evaluations,positive,negative
        emitted.append({'op':'CODE','field':2*pair+(side=='Y'),'execution_order':[[s,signs[s]] for s in word]})
        code_evaluations+=len(word)
        positive+=sum(signs[s]==1 for s in word);negative+=sum(signs[s]==-1 for s in word)
    for e in src['physical_events']:
        if e[0]=='LOCAL':
            _,stage,pair,back=e
            code('Y',pair,[stage]);emitted.append({'op':'CENTER_FREE_FULL','stage':stage,'pair':pair,'backward':back});code('X',pair,[stage])
        elif e[0]=='IDLE':
            _,pair,stages=e
            code('Y',pair,stages);emitted.append({'op':'PAID_IDLE','pair':pair,'stages':stages});code('X',pair,stages)
        else: emitted.append({'op':'RETAINED_EVENT','event':e})
    require(code_evaluations==194 and positive==34 and negative==160,'Exact complete caller code census')
    endpoint=[]
    full=list(signs)
    for role,term in enumerate(src['diagonal']):
        chosen=[s for s in full if term[s+1]]
        b=[[s,signs[s]] for s in reversed(chosen)]
        endpoint.append({'role':role,'central_exponent':term[0],'gaussian_stages':list(reversed(chosen)),'code_word_left_to_right':b,'operator':'Q^-1 B D' if term[0]==-1 else 'B D Q','plain_gaussian_after_free_postdecode':term[0]==1})
    postdecode=[]
    for e in endpoint:
        if e['central_exponent']==1:
            postdecode.append({'op':'OUTPUT_CODE_INVERSE','role':e['role'],'execution_order':[[stage,-sign] for stage,sign in e['code_word_left_to_right']]})
    post_count=sum(len(e['execution_order']) for e in postdecode)
    require(post_count==97,'Complete positive-half output decoding code count')
    require(sum(x['central_exponent']==-1 for x in endpoint)==16,'Negative-Q coded outputs')
    require(sum(x['central_exponent']==1 for x in endpoint)==16,'Positive-Q freely decodable outputs')
    return {'left_boundary_row_parities':left_colors,'right_boundary_column_parities':right_colors,'emission':emitted,'endpoint':endpoint,'code_blocks':66,'code_evaluations':194,'A_evaluations':positive,'A_inverse_evaluations':negative,'factored_code_adds_each':896,'factored_code_adds_total':194*896,'factored_code_clears_total':194*16,'factored_code_owned_temporaries':8,'positive_half_postdecode':postdecode,'positive_half_postdecode_evaluations':97,'positive_half_postdecode_adds':97*896,'positive_half_postdecode_monomial_passes':97*224,'positive_half_postdecode_clears':97*16,'dense_code_add_bound_each':6048,'dense_code_add_bound_total':194*6048,'code_field_monomial_passes':194*224,'shared_owned_code_temporaries':112,'independent_main_inputs':3584,'independent_helper_inputs':18*408,'helper_reward_multiplicity':18,'recursive_delta_vs_retained_caller':{'rank_8':-144},'denominator_13_realization':'Required for inverse code; fixed-precision scalar closure remains explicit.','status':'EXACT_TYPED_CODED_ENDPOINT_RECIPE_NOT_GAUSSIAN_SUPPLIER_ADMISSION'}

def run(chronology):
    return {'schema':'coded-native-caller-gauge/v1','local':local_checks(),'idle':idle_checks(),'chronology':chronology_checks(chronology),'noncommutative_core':noncommutative_core(chronology),'typed_caller':typed_caller_recipe(chronology),'status':'PASS_NONCOMMUTATIVE_CONTROLLER_CORE_AND_GAUGE_IDENTITIES','complete_gaussian_supplier':False,'complete_typed_rational_caller':True}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--chronology',type=Path,default=HERE/'CONTROLLER.json');p.add_argument('--write',action='store_true');args=p.parse_args()
    result=json.loads(json.dumps(run(args.chronology)))
    if args.write:(HERE/'GAUGE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        saved=json.loads((HERE/'GAUGE.json').read_text())
        require(result==saved,'Gauge receipt equality')
    print(result['status'])
