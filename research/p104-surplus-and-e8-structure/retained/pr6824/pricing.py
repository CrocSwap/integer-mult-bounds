"""Complete price of the common-idle / second-retirement caller.

The actual word and common-block construction are checked by the caller
package. This module independently counts every request and endpoint, then
uses the retained zxv/Cao Yifan interval engines, Jacob Alan Sussman compiler
and PR4359 outer ledger. Binary/caller/native authors retain their credit.
Adapted to the recounted native helper split by @CubeJerry (#6805) with OpenAI assistance,
and to the shared-carrier input lift by DreamingOfClouds with Claude Opus 5.5 (Anthropic),
via Claude Code. Apache-2.0. No selected-frontier change is inferred.
"""
from collections import Counter
from fractions import Fraction as Q

KAPPA=Q('.00330823')
TESTED=Q('.003308234')
PREVIOUS=Q('.00330814')
HELPERS={1:14,2:8,3:4,4:109,5:17,6:3,7:10,8:40,9:359}
LOCAL_PAID={1:2234,2:454,3:489,4:110,5:152,6:7,7:9,8:1}

def need(ok,message):
    if not ok:raise ValueError(message)

def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):encode(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v)for v in value]
    return value

def formula_invoice(local):
    T=Counter({r:18*n for r,n in local['helpers'].items()})
    P=Counter({r:18*n for r,n in local['paid'].items()})
    # Six child sizes(4,4,1,1,4,4), twelve genuine internal binary nodes.
    for size,count in {2:8,4:4}.items():
        T[8*size+1]+=208*count
        P[8*size]+=208*count
    # Eight root outputs, one D target split into S,D and one BC into B,S*C.
    T.update({145:104,73:208,41:208,9:208,1:104,32:208})
    P[1]+=15*104
    P[40]+=208
    P[32]+=208;P[8]+=208                 # One whole common idle B+C and one paid fragmented direction.
    return T,P

def assemble(local,native,word,physical):
    need(dict(local['paid'])==LOCAL_PAID and dict(local['helpers'])==HELPERS,
         'Exact new native paid and independent-helper boundary')
    need(local['helpers']==native['helpers'],'Every productive helper has a checked native map')
    need(word['roles']==34 and word['stages']==18,'All independent main inputs and native stages')
    T,P=Counter(),Counter();idle=Counter();counts=Counter(e[0]for e in word['events'])
    for event in word['events']:
        op=event[0]
        if op=='LOCAL':T.update(local['helpers']);P.update(local['paid'])
        elif op=='QUERY':P[1]+=104
        elif op in('IDLE','IDLE_ONE'):
            stages=event[3]if op=='IDLE'else event[2]
            need(len(stages)==len(set(stages)),'No repeated fresh axis in a whole idle')
            r=8*len(stages);n=208 if op=='IDLE'else 104
            P[r]+=n;idle[r]+=n
    main=Counter()
    for term in word['diagonal']:
        need(not term[1],'No old nonfresh stage-zero factor is silently present')
        main[int(term[0]%2)+8*sum(term[2:])]+=104
    T.update(main)
    need((T,P)==formula_invoice(local),'Formula and every emitted Gaussian request agree')
    need(main==physical['main_targets'],'Every main target has its checked absolute physical phase')
    need(idle==physical['whole_idle_jobs'],'Every fused and unfused whole idle is physically checked')
    need((counts['LOCAL'],counts['QUERY'],counts['IDLE'],counts['IDLE_ONE'],counts['LAMBDA'])==(18,15,12,6,100),
         'Complete literal paid/normalization census')
    need(len(word['events'])==606,'Every ordinary basis and retirement gate is present')
    need((sum(T.values()),sum(P.values()))==(13688,66888),'All independent targets and paid requests')
    need(sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())==760,'Exact unchanged rank-mass surplus')
    need((max(T),max(P))==(145,40),'Actual maximum target and paid ranks')
    return T,P,counts

def ordinary(local,native,word,adapters):
    from scalars import verify as scalar_envelope
    actual_scalars=scalar_envelope(word)
    need(native['helper_normalizers']==2*sum(HELPERS.values()) and native['main_adapters']==208,
         'Native normalization counts derive from every independent helper and main port')
    need(local['owned_lifetimes']==47 and local['peak_owned_fields']==14,
         'Unchanged actual native owned lifetimes and peak')
    need(local['public_inputs']==772 and local['owned_fields']==29,
         'Exact native public and owned label inventory')
    # Source routes are literal whole-job / fixed17-axis route rates. The
    # rates remain framework contracts; their counts are recomputed here.
    routes=(sum(local['paid'].values())+native['helper_normalizers']+native['main_adapters']
            +4*104+4*local['owned_lifetimes'])*1000
    per_call=local['real_scalar_allowance']+routes
    need(per_call<10**7,'All actual local scalar and route work fits the displayed per-call bound')
    scalars=[abs(Q(e[-1]))for e in word['events']if e[0]in('ADD','SCALE')]
    need(all(x and x.denominator&(x.denominator-1)==0 for x in scalars),'Every new basis coefficient is nonzero dyadic')
    need(max(x.numerator.bit_length()for x in scalars)<=8 and max(x.denominator.bit_length()for x in scalars)<=7,
         'Literal dyadic coefficient-height gate for the complete caller')
    # The complete Horner work is checked gate by gate, including every caller coefficient.
    # scalar_envelope checks every actual gate's complete joint Horner,
    # halving/sign and destination-add cost and coefficient height.
    # Scanning all34 fields for each gate is an explicit overcount.
    caller=32*word['roles']*104*len(word['events'])
    need(104*actual_scalars['real_scalar_units_per_port']<=caller and
         104*actual_scalars['coefficient_height_units']<=caller,
         'Actual complete scalar work and height fit the new envelope')
    thin=15*16*104
    main_maps=adapters['main_two_axis_exchanges']+adapters['main_nine_axis_basis_maps']+adapters['main_phase_translations']
    idle_maps=adapters['idle_two_axis_exchanges']
    query_maps=adapters['query_nine_axis_basis_maps']+adapters['query_phase_translations']
    output=word['roles']*104*26+1000*main_maps
    idle_adapter_work=1000*idle_maps;query_adapter_work=1000*query_maps
    total=18*10**7+thin+caller+output+idle_adapter_work+query_adapter_work
    need(total<10**9,'Fresh complete ordinary count, not an opaque predecessor allowance')
    return {'local_scalar':local['real_scalar_allowance'],'local_routes':routes,'local_per_call_counted':per_call,
            'local_per_call_upper':10**7,'native_invocations':18,'caller_gate_passes':caller,'thin_query_work':thin,
            'all_main_input_output_adapters_and_normalizers':output,'whole_idle_adapter_work':idle_adapter_work,
            'query_adapter_work':query_adapter_work,'elementary_canonical_maps':main_maps+idle_maps+query_maps,
            'canonical_adapter_rate':1000,'raw_scalar_upper':total,'raw_budget':10**9,
            'maximum_literal_scalar':max(scalars),'scalar_numerator_bits':8,'scalar_denominator_bits':7,
            'actual_scalar_work_per_port':actual_scalars['real_scalar_units_per_port'],
            'actual_scalar_height_per_port':actual_scalars['coefficient_height_units'],
            'peak_owned_fields':14,'native_owned_lifetimes':47,'new_productive_fresh_fields_per_port':2,
            'native_public_inputs':772,'native_owned_labels':29,
            'thin_owned_contract':'One uncredited copied-query stream reused sequentially, cleared on return; no new helper credit.',
            'scalar_growth_bound':'At most 2^(10^9+R*f), R the recounted complete paid rank mass; inherited physical precision/tape rates remain assumptions.'}

def local_lift_gain(E):
    """Per-call sign of the input-lift saving, for every exponent t=1-k with 0<k<=.0034.

    Delta(T-P)=g(t) with H_r=r^t and g(t)=H7+H3+H5-H9-H4-2*H1 (Delta T=H7-H9,
    Delta P=2*H1+H4-H3-H5).  Rank masses agree (15=15) but the multiset is not majorized, so
    concavity alone gives no sign.  Instead g(1)=0 and, for s in [1-.0034,1],
    g'(s)<=g'(1)+(1-s)*M with M=sum |coeff| x ln^2 x, so g'<0 there and g(t)>=k*(-g'(1))-k^2*M/2.
    """
    def total(terms,s):
        out=(Q(0),Q(0))
        for x,c in terms:
            out=(out[0]+c*E.power(x,s)[0],out[1]+c*E.power(x,s)[1])
        return out
    plus=[(7,1),(3,1),(5,1)];minus=[(9,1),(4,1),(1,2)]
    need(sum(x*c for x,c in plus)==sum(x*c for x,c in minus),'Equal local rank mass')
    cap=Q('.0034')
    def dlog(terms):
        lo=hi=Q(0)
        for x,c in terms:
            a=E.mul((Q(x),Q(x)),E.log_bounds(x));lo+=c*a[0];hi+=c*a[1]
        return lo,hi
    def d2log(terms):
        hi=Q(0)
        for x,c in terms:
            a=E.mul(E.mul((Q(x),Q(x)),E.log_bounds(x)),E.log_bounds(x));hi+=c*a[1]
        return hi
    dp,dm=dlog(plus),dlog(minus)
    derivative_one=(dp[0]-dm[1],dp[1]-dm[0])          # g'(1)
    M=d2log(plus)+d2log(minus)
    need(derivative_one[1]+cap*M<0,'g prime is negative on the whole interval 1-.0034..1')
    out={'g_prime_at_1':E.display(derivative_one),'second_derivative_majorant':float(M)}
    for name,k in [('claim',KAPPA),('tested',TESTED)]:
        t=1-k;gain=(total(plus,t)[0]-total(minus,t)[1],total(plus,t)[1]-total(minus,t)[0])
        need(gain[0]>0,'Exact interval engine: positive local saving at '+name)
        derived=k*(-derivative_one[1])-k*k*M/2
        need(derived>0 and derived<=gain[1],'Derivative lower bound is positive and consistent')
        out[name]={'interval':E.display(gain),'derivative_lower_bound':float(derived)}
    return out

def run(local,native,word,physical,L,adapters):
    T,P,counts=assemble(local,native,word,physical)
    work=ordinary(local,native,word,adapters)
    E=L.load(L.ROOT/'research/higher-moment-strictification/verify.py','root8_first_intervals')
    other=L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','root8_second_intervals')
    def margin(k):
        t,p=E.moment(T,1-k),E.moment(P,1-k)
        return t[0]-p[1],t[1]-p[0]
    lower,upper=Q('.00330823456614'),Q('.00330823456615')
    need(PREVIOUS<KAPPA<TESTED<lower,'Claim, tested price and raw crossing are strictly ordered')
    endpoints={}
    for name,k in [('lower',lower),('upper',upper),('tested',TESTED)]:
        first=margin(k);tl,th=other.moment(T,k);pl,ph=other.moment(P,k);second=(tl-ph,th-pl)
        need(max(first[0],second[0])<=min(first[1],second[1]),'Independent moment-engine agreement')
        need(first[1]<0 and second[1]<0 if name=='upper'else first[0]>0 and second[0]>0,
             'Both engines prove the raw endpoint/tested signs')
        endpoints[name]={'first':E.display(first),'second':E.display(second)}
    lift_gain=local_lift_gain(E)
    signed=Counter(T);signed.subtract(P);derivative=Q(0)
    for r,n in signed.items():
        log=E.log_bounds(r)
        derivative-=n*(E.mul(E.power(r,1-Q('.0034')),log)[0]if n>=0 else r*log[1])
    need(derivative<0,'Unique raw crossing through the retained BIT cap')
    t,offset,power,cutoff,floor=1-TESTED,Q(1,7),1920,11,12
    target,paid=E.moment(T,t),E.moment(P,t)
    alpha=E.divide(paid,target)
    gamma=E.divide(E.moment(P,t+offset),E.mul(E.power(cutoff,offset),target))
    delta=E.divide((Q(sum(T.values())*floor),)*2,E.mul(E.power(cutoff,TESTED),target))
    reserve,decay=Q(1,10**27),Q(31,32)
    need(alpha[1]<1-reserve and gamma[1]<decay and delta[1]<decay,'All completion and splitting tail ratios')
    alternative_delta=E.divide((Q(sum(T.values())*13),)*2,E.mul(E.power(12,TESTED),target))
    # This smaller productive census also makes the alternate12/13 cutoff viable;
    # admission below still uses the independently checked11/12 choice.
    normalized=1/(1+power*reserve)+4*decay**power
    need(normalized<1 and cutoff**64<floor**63,'Exact finite strictification and rank-rounding inequalities')
    theta,logarithm_power=Q(63,64),2100
    half=E.power(145,Q(power,2)*TESTED);factor=E.mul(half,half)
    eta=E.scale(E.divide((Q(1),Q(1)),factor),t)
    need(2*(cutoff**power)**64<=(145**power)**63 and eta[0]>theta**logarithm_power,'Compiler shifted exits and complement capacity')
    need(factor[1]<2**logarithm_power,'Compiler initial range')
    gap=(TESTED-KAPPA)/7;need(gap.numerator==1,'Exact positive compiler grid')
    step=gap.denominator
    def wins(j):return(step*j+1)**logarithm_power<2**j
    left,right=1,2
    while not wins(right):left,right=right,2*right
    while right-left>1:
        middle=(left+right)//2
        if wins(middle):right=middle
        else:left=middle
    H=step*right
    need(H>8*power and wins(right)and not wins(right-1),'Explicit uniform threshold and adjacent-grid control')
    bit=L.read(L.ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom=Q(bit['atom']);ordinary_bit=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599');admitted=Q(bit['admitted'])
    need(atom>ordinary_bit>admitted>TESTED and atom<1-ordinary_bit,'Retained ordinary/admitted BIT stock and savings')
    outer_module=L.load(L.ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','root8_outer')
    params={'kappa':KAPPA,'tested_saving':TESTED,'complex_uniform_saving':KAPPA+6*gap,
            'b':KAPPA+5*gap,'a':KAPPA+4*gap,'q':KAPPA+3*gap,'bit_saving':admitted,
            'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
    outer=outer_module.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
    need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4,'Complete54+4 outer inventory')
    need(all(v>0 for k in('strict_checks','functional_checks')for v in outer[k].values()),'Every outer inequality is strict')
    bad=outer_module.ledger(dict(params,bit_saving=Q('.0027')))
    need(any(v<=0 for v in bad['strict_checks'].values()),'Insufficient BIT budget rejected')
    work['paid_rank_mass']=sum(r*n for r,n in P.items())
    return encode({'status':'PASS_RETIMED_NATIVE_HELPER_COMPLETE_PRICE','kappa':KAPPA,'tested':TESTED,
       'targets':T,'paid':P,'productive_fields':sum(T.values()),'paid_calls':sum(P.values()),'rank_mass_surplus':760,
       'full_calls':18,'thin_queries':15,'whole_idle_jobs':3120,'counts':counts,'raw_root_interval':[lower,upper],
       'raw_endpoint_margins':endpoints,'local_lift_gain':lift_gain,'derivative_upper':derivative,'nonrecursive':work,
       'strictification':{'power':power,'cutoff':cutoff,'floor':floor,'offset':offset,'reserve':reserve,'decay':decay,
                         'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),
                         'alternative_12_13_delta':E.display(alternative_delta),'normalized_upper':normalized},
       'compiler':{'H':H,'N':'2^'+str(H),'integer_test_exponent':right,'theta':theta,'logarithm_power':logarithm_power,
                   'eta':E.display(eta),'gap':gap,'uniform_saving':params['complex_uniform_saving'],'word_materialized':False},
       'ordinary_BIT':bit,'outer':outer,'source_assumptions':['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
       'scope':'Complete conditional price, requiring the supplied caller/native/physical inputs to be independently verified by the package. Does not itself verify those scientific inputs, discharge inherited assumptions, establish scientific admission, or change selected kappa.'})
