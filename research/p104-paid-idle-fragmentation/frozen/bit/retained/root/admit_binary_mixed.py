#!/usr/bin/env python3
"""Exact finite and ordinary admission of the independently replayed BIT caller.

This reuses the authenticated native, cover, ordinary-wrapper and finite
compiler theorems. It does not assert an unconditional multiplication theorem.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
import hashlib, importlib.util, json, time

H=Path(__file__).resolve().parent
RAW=Q('.00374458'); GAP=Q(1,10**10); ADMITTED=Q('.00374457')

def need(v,s):
    if not v:raise ValueError(s)

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v)for v in x]
    return x

def main():
    started=time.monotonic()
    pins=json.loads((H/'INPUT-PINS.json').read_text())
    for p in pins:
        b=(H/p['path']).read_bytes()
        need(len(b)==p['bytes']and hashlib.sha256(b).hexdigest()==p['sha256'],'Retained source pin '+p['path'])
    audit=load(H/'audit_binary_mixed.py','independent_binary_audit')
    audit.main()
    a=json.loads((H/'INDEPENDENT-BINARY-MIXED-AUDIT.json').read_text())
    need(a['status']=='PASS_INDEPENDENT_BINARY_MIXED_CALLER_AND_SOURCE_BINDING','Fresh source/caller replay')
    C=load(H/'inputs/credited_trim.py','retained_finite_compiler')
    I=load(H/'inputs/independent_interval.py','independent_binary_intervals')
    T={int(k):v for k,v in a['targets'].items()};P={int(k):v for k,v in a['paid'].items()}
    cert=C.certificate(T,P,RAW,768,15,16,Q(1,5),Q(1,5),uniform_gap=GAP,
        label='exact_characteristic_two_mixed_root',source_status='New literal354-event caller; independently replayed physical source charts and complete scalar endpoint; retained unchanged all-width native theorem')
    @lru_cache(None)
    def power(r,t):
        lo,hi=I.power(r,t);s=10**65
        return Q((lo*s).__floor__(),s),Q(-((-hi*s).__floor__()),s)
    def moment(hist,t):
        lo=hi=Q(0)
        for r,n in hist.items():
            x,y=power(r,t);lo+=n*x;hi+=n*y
        return lo,hi
    def margin(k):
        tt,pp=moment(T,1-k),moment(P,1-k)
        return tt[0]-pp[1],tt[1]-pp[0]
    # The two endpoints are exact decimal rationals, not floating root claims.
    lower,upper=Q('.0037445923587'),Q('.0037445923590')
    need(margin(lower)[0]>0 and margin(upper)[1]<0,'Independent strict raw crossing bracket')
    margins={}
    for k in (RAW,lower,upper,Q('.0042'),Q('.00424927762')):
        m=margin(k);margins[str(k)]=I.bounds_text(m,28)
        need(m[0]>0 if k in (RAW,lower) else m[1]<0,'Independent moment sign')
    t=1-RAW;tt=moment(T,t);u=Q(1,5)
    ratios=(I.div(moment(P,t),tt),I.div(moment(P,t+u),I.mul(power(15,u),tt)),I.div(I.mul(power(16,u),moment(T,t-u)),tt))
    limits=list(map(Q,cert['rational_upper_limits']))
    for r,bound in zip(ratios,limits):need(0<r[0]<=r[1]<=bound<1,'Independent finite tail enclosure')
    aa,gg,ll=limits;norm=1/(1+768*(1-aa))+2*gg**768+ll**768
    need(norm<1,'All discarded targets and high-rank splits paid')
    compiler=cert['uniform_compiler'];threshold=compiler['H'];p=compiler['logarithm_power'];e=compiler['integer_test_exponent']
    need(threshold==GAP.denominator*e and(threshold+1)**p<2**e,'Independent uniform integer gate')
    need(not(GAP.denominator*(e-1)+1)**p<2**(e-1),'Preceding uniform grid point rejects')
    need(Q(compiler['uniform_saving'])==RAW-GAP,'Exact uniform debit')
    # Fresh complete reserves. The caller's ADD/SWAP basis programs are
    # literal binary operations, with three additions charged per swap.
    n,m,F=111,34,18;thin=a['event_counts']['QUERY'];idles=a['event_counts']['IDLE']+a['event_counts']['IDLE_ONE'];h=127
    ordinary_basis=n*8*(a['event_counts']['ADD']+3*a['event_counts']['SWAP'])
    visible=F*10**7+ordinary_basis+256*n*(F+thin+m)
    route_per=8*(10*h*h+10*h)
    route_count=4*(sum(P.values())+sum(T.values()))+8*n*F+8*n*idles
    routes=route_per*route_count
    # Overreserve two complete main banks for every declared basis/idle
    # event, even though the emitted ADD/SWAP program is in-place.
    owned=F*a['source']['owned_labels']+2*n*m*len(audit.load(audit.CALLER,audit.CALLER_SHA)['events'])+16*n*(F+thin+m)
    need(visible+routes<10**12 and owned<10**7,'All ordinary routing and scratch funded')
    # Finite target restriction also specializes discarded independent
    # outputs to owned zero. Name that stock and its activation/reset work
    # explicitly; it is not silently dropped into an unrelated reserve.
    constants={'U_raw':'sum(i=0..767,11640^(767-i)*56895^i)',
        'D':'11640^768-W','D_nonnegative':True,
        'O':f'{owned}*U_raw+D','Z':'W+O',
        'G':'1000000000000*U_raw+8*R+2*11640^768',
        'E':'64*(Z+N+P+G+1)^3','B_constant':'P+E','C0':'32*N*B_constant^2'}
    old=json.loads((H/'inputs/BASELINE-ADMISSION.json').read_text())['branches']['bit']
    b0=Q(old['ordinary_admitted']);need(b0==Q('.00369905737'),'Retained ordinary BIT baseline')
    covered=RAW-2*GAP;atom=Q('.00375');previous=b0;stages=[]
    for admitted in (Q('.00374440908'),ADMITTED):
        envelope=(1-atom)*covered+atom*previous
        need(atom>envelope>admitted>previous and atom<1-envelope,'Full retained ordinary-wrapper envelope')
        stages.append(dict(previous_ordinary=previous,atom=atom,covered_saving=covered,full_envelope_limiting_term=envelope,admitted=admitted,strict_debit=envelope-admitted))
        previous=admitted
    need(previous==ADMITTED and ADMITTED>Q(old['ordinary_admitted']),'Strict ordinary improvement')
    # Negative controls target substantive accounting mistakes, in addition
    # to the missing-event controls in the independent full caller replay.
    need(margin(Q('.0042'))[1]<0,'Unsupported target claim rejected')
    bad_envelope=(1-atom)*Q(old['covered_saving'])+atom*b0
    need(bad_envelope<ADMITTED,'Old source cannot fund new ordinary claim')
    need((1-atom)*covered+atom*b0<ADMITTED,'One bootstrap step is insufficient')
    out=dict(status='PASS_BINARY_MIXED_COMPLETE_ORDINARY_00374457',
        ordinary_admitted=ADMITTED,previous_ordinary=b0,ordinary_gain=ADMITTED-b0,
        raw_tested=RAW,raw_crossing=[lower,upper],covered_saving=covered,
        caller_sha256=a['caller_sha256'],native_source_sha256=a['source_sha256'],
        independent_moment_intervals=margins,independent_finite_ratios=[I.bounds_text(r,28)for r in ratios],
        independent_normalized_upper=I.bounds_text((norm,norm),28),finite_admission=cert,
        paid=P,targets=T,paid_calls=sum(P.values()),productive_fields=sum(T.values()),rank_surplus=a['rank_surplus'],
        full_calls=F,thin_rank_one_queries=n*thin,ordinary_basis_record_bound=ordinary_basis,
        ordinary_visible_record_bound=visible,whole_job_route_bound_per_map=route_per,
        whole_job_route_count_bound=route_count,whole_job_route_record_bound=routes,
        ordinary_record_allowance=10**12,owned_bank_bound_per_raw_invocation=owned,
        compiler_constants=constants,ordinary_bootstrap=stages,
        inherited_native_scope=a['physical_binding_scope'],
        prime_rule='Retained odd-prime rule q>2^48*N^5 excluding every nonzero fixed rational denominator and native rank witness; new ordinary basis coefficients are binary.',
        negative_controls={'claimed_0042':'Strict complete moment is negative','old_native_stock':'Retuning the wrapper alone cannot reach the new saving','only_one_bootstrap':'First full ordinary envelope is below the final claim',**a['mutation_controls']},
        assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
        scope='Constructive improvement of the BIT dependency under the retained framework. The complex branch still limits global kappa. This is not a new global kappa=.00374457 theorem.',
        uniform_word_materialized=False,new_global_kappa_claim=False,seconds=time.monotonic()-started)
    (H/'BINARY-MIXED-ADMISSION.json').write_text(json.dumps(encode(out),indent=2)+'\n')
    print(json.dumps(encode({k:out[k]for k in ('status','ordinary_admitted','ordinary_gain','raw_crossing','ordinary_visible_record_bound','whole_job_route_record_bound','owned_bank_bound_per_raw_invocation','seconds')}),indent=2))

if __name__=='__main__':main()
