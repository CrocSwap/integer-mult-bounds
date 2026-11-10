"""Complete rank profile and positive inherited ordinary-cost comparison.

This is source accounting under the declared historical tariff, not a proof
of its physical bit-tape rate. Prepared for @CubeJerry with substantial OpenAI
assistance. Apache-2.0.
"""
from collections import Counter
from source_binding import module,need
from replacement import counts


def verify(old,new,root,word):
    iv=module('invoice')
    need(old['types'] == new['types'] and old['roles'] == new['roles'] == 76,
         'unchanged complete arbitrary main inventory and targets')
    need([e for e in old['events'] if e[0] == 'J'] ==
         [e for e in new['events'] if e[0] == 'J'], 'same 18 exact local native contacts')
    masks=[[-1,0]+[int(r in s['mask']) for s in root['stages']] for r in range(root['n'])]
    need(masks == old['types']['A']['diagonal'] == new['types']['A']['diagonal'],
         'unchanged exact E-free root target masks')
    need(all(sum(d[2:])>0 for t in new['types'].values() for d in t['diagonal']),
         'no empty-mask main target credit')
    local=iv.local_invoice(word)
    oldT,oldP=iv.outer_invoice(old,local)
    newT,newP=iv.outer_invoice(new,local)
    need(oldT == newT and oldP == newP, 'complete rankwise moment polynomial unchanged')
    a,b=iv.caller_cost(old),iv.caller_cost(new)
    oldc,newc=counts(old),counts(new)
    def amount(c,op):
        return sum(v['physical_instances'].get(op,0) for v in c.values())
    need((amount(oldc,'QUERY'),amount(oldc,'QSELF'),amount(newc,'QUERY'),amount(newc,'QSELF'))
         == (224,192,416,0), 'actual complete outer lifetime counts')
    need(len(new['events'])-len(old['events']) == 104
         and amount(newc,'LAMBDA')-amount(oldc,'LAMBDA') == 28*96,
         'all additional ordinary work counted')
    need(b['caller_envelope']-a['caller_envelope'] == 104*32*38*96,
         'complete changed caller envelope')
    need(b['lambda_recharge']-a['lambda_recharge'] == 28*1000*96,
         'positive extra lambda allowance')
    need(a['qself_extra_lifecycle'] == 192*128 and b['qself_extra_lifecycle'] == 0,
         'only obsolete QSELF-specific surcharge removed')
    for name in ('thin_lifecycle','main_normalizers','main_maps','idle_maps','query_maps'):
        need(a[name] == b[name], 'unchanged complete term '+name)
    scale=18*word['public']*104
    oldraw=18*local['reviewed_per_call']+a['raw_rest']
    newraw=18*local['reviewed_per_call']+b['raw_rest']
    before=oldraw+a['lambda_recharge']+scale
    after=newraw+b['lambda_recharge']+scale
    need((oldraw,newraw,before,after) == (796934944,809050912,811461936,826265904),
         'full exact inherited invoice')
    need(after < 10**9, 'full inherited ordinary allowance preserved')
    # A fourth query would change the full paid profile, even with free metadata.
    mutant={**new,'events':new['events']+[['A','QUERY',0,1,-1]]}
    mt,mp=iv.outer_invoice(mutant,local)
    need(mt == newT and mp[1]-newP[1] == 96 and mp != newP,
         'fourth-query budget negative control')
    main=sum(t['roles']*len(t['ports']) for t in new['types'].values())
    helpers=18*sum(local['helpers'].values())
    return dict(targets=dict(sorted(newT.items())),paid=dict(sorted(newP.items())),
        target_count=sum(newT.values()),paid_count=sum(newP.values()),
        rank_mass_surplus=sum(r*(newT[r]-newP[r]) for r in set(newT)|set(newP)),
        paid_rank_mass=sum(r*n for r,n in newP.items()),
        all_rankwise_deltas_zero=True,main_arbitrary_inputs=main,fresh_local_helpers=helpers,
        old_opcode_counts=oldc,new_opcode_counts=newc,
        local_source_lifetimes_per_joint=local['lifetimes'],local_source_peak_owned=local['peak_owned'],
        outer_query_or_QSELF_lifetimes_before=416,outer_QUERY_lifetimes_after=416,
        additional_public_or_helper_roles=0,additional_owned_bank_inventory=0,
        outer_query_peak_bank_inventory=1,
        owned_inventory_scope='Relative to the existing completed QUERY contract; no physical binding installed.',
        old_caller_cost=a,new_caller_cost=b,old_reviewed_raw=oldraw,new_reviewed_raw=newraw,
        per_call_conversion_recharge=scale,full_before=before,full_after=after,
        margin_below_inherited_cap=10**9-after,
        controls=['fourth_QUERY_adds_96_paid_rank_one_without_target_credit'],
        tariff_scope='Inherited scalar/routing convention only; actual common precision and bit-tape tariff remain open.',
        selected_kappa_change=False)
