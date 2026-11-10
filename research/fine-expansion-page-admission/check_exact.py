"""Independent integer/Fraction checks of the pinned interface proposition.
No numerical predecessor checker is imported or executed.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from math import isqrt
from admission import Certificate,final_budget,ceil_log2,need


def checks():
    cases=blocks=identities=wraps=0;multiple=clipped=0
    for q in (101,121,256,1024):
        alphas=sorted(set(range(2,10))|{isqrt(q-1)})
        for alpha in alphas:
            for t in (4,8,16,32,64,128):
                for s in range(t//2+1,t):
                    c=Certificate.make(s,t,alpha,q)
                    # Different construction of the ceiling root: bracket its square.
                    root=c.b//alpha
                    need((root-1)**2<q<=root**2,'literal ceiling-root bracket')
                    sequence=list(c.block_sequence());need(len(sequence)==c.blocks,'actual block count')
                    end=c.source_start+c.source_count
                    need(sequence[0]['start']==c.source_start and sequence[-1]['end']==end,'exact full-period endpoints')
                    previous=None
                    for block in sequence:
                        blocks+=1;m=block['m'];v=block['v'];n=block['n']
                        need(2*c.b+3<=n<=2*c.b+m+3 and m<=n,'actual BlockHeader span')
                        need(block['nc']==n+m-1 and n<=4*q and block['nc']<=5*q,'actual prefix/width gates')
                        need(c.P>=2*c.sigma+q+ceil_log2(32*(n+1))+12,'actual extraction precision gate')
                        if previous is not None:
                            need(previous['start']<=block['start']<=previous['end']<=block['end'],'complete monotone overlap')
                        previous=block
                        if m<c.b:clipped+=1
                        for z in sorted({0,m//2,m-1}):
                            center=Fraction(s*(v+z),t)
                            for h in sorted({-c.b-1,0,block['end']-1-block['j0']}):
                                A,B,K=c.exponents(block,h,z)
                                direct=(Fraction(block['j0']+h)-center)**2/(alpha*alpha)
                                need(A+B+K==direct,'original quadratic coefficient identity')
                                need(abs(A)<20*q and abs(B)<3*q and 0<=K<12*q,'actual exponent ranges')
                                identities+=1
                            # The full needed radius is covered; ceil/floor checked without helper.
                            first=(center.numerator//center.denominator)-c.b
                            last=-((-center.numerator)//center.denominator)+c.b
                            need(block['start']<=first and last<block['end'],'all center-radius integer occurrences covered')
                    stream=Counter(j%s for j in range(c.source_start,end))
                    need(sum(stream.values())==c.source_count,'all halo occurrences charged')
                    for r in range(s):
                        exact=(end-1-r)//s-(c.source_start-1-r)//s
                        need(stream[r]==exact,'independent residue winding multiplicity');wraps+=1
                    if max(stream.values())>1:multiple+=1
                    for lift in (-2,1):
                        # Shifting by one full source period preserves every multiplicity.
                        need(Counter((j+lift*s)%s for j in range(c.source_start,end))==stream,'signed full-period lift')
                    cases+=1
    # These are independent proof controls, not claims of native Tile execution.
    c=Certificate.make(61,64,3,101);seq=list(c.block_sequence())
    need(seq[-1]['end']>c.source_start+c.source_count-1,'one-short halo fails final source containment')
    need(c.source_count>c.s,'deduplication loses required occurrences')
    need(any(b['end']!=((c.s*(b['v']+b['m']-1))//c.t+c.b+2) for b in seq),'floor cannot replace strict upper ceiling')
    guards=0
    for args in ((3,4,2,100),(3,4,11,121),(3,6,2,101),(4,4,2,101),(3,4,1,101)):
        try:Certificate.make(*args)
        except ValueError:guards+=1
        else:raise ValueError('missing domain rejection')
    # Generic interval containment does not imply the source upper<=unit guard.
    interval_controls=reciprocal=positivity_controls=0
    for P in range(1,17):
        # Underfunded precision permits an exactly positive coefficient with
        # a valid zero stored lower endpoint. This is an explicit countermodel
        # to inferring positivity from enclosure/error alone, not a replay of
        # the production Exponentials owner with a modified precision.
        tiny=Fraction(1,1<<(P+1));zero=Fraction(0);one_ulp=Fraction(1,1<<P)
        need(zero<tiny<=one_ulp and tiny-zero<Fraction(3,2)*one_ulp,
             'underfunded enclosure allows a zero lower coefficient')
        positivity_controls+=1
        truth=Fraction(1)-Fraction(1,1<<(P+2));lower=Fraction((1<<P)-1,1<<P);upper=Fraction((1<<P)+1,1<<P)
        need(lower<=truth<=upper and upper>1 and upper-lower==Fraction(2,1<<P),'near-unit enclosure countercontrol')
        interval_controls+=1
        for R in range(P,P+8):
            U=1<<R
            for added in (0,1,2,7,U//3,U):
                lo=U+added;up=-(-(U*U)//lo)
                final=-(-up//(1<<(R-P)))
                need(up<=U and final<=1<<P,'actual reciprocal/ceil upper unit invariant')
                reciprocal+=1
    budgets=0
    for D in (1,2,7,16):
        for extra in (0,1,4,17,63):
            for Kc in (0,1,8,73):
                for tau in (0,1,13):
                    Kf=D+extra;q=Kf+Kc+tau+5
                    r=final_budget(D,Kf,Kc,q,tau)
                    need(r['admitted'] and r['restored']<r['threshold'],'same-Gamma sufficient prefix allowance')
                    exact=Fraction(1,1<<D)*Fraction(1,1<<r['J'])
                    need(exact==Fraction(1,1<<Kf),'spend actual existing forward share')
                    need(exact*(1<<D)!=exact and exact/Fraction(1<<D)!=exact,'double restoration and double attenuation controls')
                    budgets+=1
    stages=layouts=0
    for radices in ((4,4),(8,4),(4,8,4),(8,4,8,4)):
        # Source-valued labels verify the cyclic axis rotations, not only norms.
        import itertools
        initial=list(itertools.product(*(range(t) for t in reversed(radices))))
        labels=[tuple(reversed(x)) for x in initial];order=list(reversed(range(len(radices))))
        for i,t in enumerate(radices):
            need(order[-1]==i,'actual original axis next contiguous')
            V=len(labels);A=V//t
            labels=[labels[a*t+k] for k in range(t) for a in range(A)]
            order=[i]+order[:-1]
            ell=t.bit_length()-1
            for j in range(ell):
                prefixes=1<<j;suffix=(t>>(j+1))*26
                need(prefixes*A*2*suffix==26*V,'literal complete-volume FieldMove stage writes');stages+=1
        need(labels==[tuple(reversed(x)) for x in initial],'full target order restored after D rotations')
        layouts+=1
    return dict(header_cases=cases,blocks=blocks,quadratic_identities=identities,
                residue_multiplicities=wraps,multiple_wrap_cases=multiple,clipped_blocks=clipped,
                certificate_domain_rejections=guards,near_unit_countercontrols=interval_controls,
                positive_lower_countercontrols=positivity_controls,
                reciprocal_unit_cases=reciprocal,normalization_budget_cases=budgets,
                complete_axis_layouts=layouts,literal_move_stage_invoices=stages,
                mathematical_controls=['short_halo','lost_alias_multiplicity','upper_floor','positivity_precision',
                                       'near_unit_enclosure','double_forward_normalization','extra_restoration'])
