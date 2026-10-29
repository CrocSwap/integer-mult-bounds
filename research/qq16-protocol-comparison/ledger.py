# SPDX-License-Identifier: Apache-2.0
"""Independent literal-occurrence and complete-comparison ledger.

Inputs are already authenticated source objects. This checker does not execute
machine code, build encoded descriptors, or turn a bound into an exact price.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def record(hist):
    return {'calls':sum(hist.values()), 'rank_mass':sum(k*v for k,v in hist.items()),
            'ranks':dict(sorted(hist.items()))}


def literal_census(data, producer):
    """Enumerate actual finite source occurrences, quotienting only cover owner.

    Identifier: (source event, subgroup, original raw event, original group PC).
    Each row also binds target/rank and the installed event/PC. Local group PC
    includes the exact owner-entry wrapper count, independent of owner index.
    Idle group child PC is literally 1. Gamma is a multiplicity, not expanded.
    """
    source=producer.source
    need(len(source.events)==482, 'frozen selected event count')
    native={}; clean={}; lead={}
    for direction in ('forward','backward'):
        orig=data['programs'][direction]
        core=producer.packet['core_words'][direction]
        original=[(raw,e) for raw,e in enumerate(orig) if e[0] in ('climb','center')]
        kept=[(raw,e) for raw,e in original if e[0]!='center']
        cleaned=[(raw,e) for raw,e in enumerate(core) if e[0] in ('climb','center')]
        need([e for _,e in cleaned]==[e for _,e in kept], 'ordered persistent native identity')
        oc={op[1]:(pc,op[2],op[3]) for pc,op in enumerate(source.codes[direction]) if op[0]=='child'}
        cc={op[1]:(pc,op[2],op[3]) for pc,op in enumerate(producer.core.codes[direction]) if op[0]=='child'}
        need(len(oc)==len(original) and len(cc)==len(cleaned), 'one literal child per native event')
        native[direction]=[(raw,*oc[raw],e[0]) for raw,e in original]
        clean[direction]={oldraw:cc[newraw] for (oldraw,_),(newraw,_) in zip(kept,cleaned)}
    core_events={}
    added=[]
    for index,event in enumerate(producer.events):
        if event[0]!='qq16':continue
        macro=event[4]
        if macro[0]=='retained_core':
            need(event[1] not in core_events, 'one retained core per replaced event')
            core_events[event[1]]=index
        elif macro[0]!='cover_map':
            body=macro[2] if macro[0] in ('cover_sweep','private_sweep') else [macro]
            for offset,op in enumerate(body):
                if op[0]=='native_line':
                    recipe=producer.packet['native_line_recipes'][op[2]]
                    need(recipe['rank']==1, 'new source-bound rank-one recipe')
                    added.append([event[1],index,event[3],offset,op[1],op[2],recipe['rank']])
    need(set(core_events)=={0,4} and len(added)==32, 'exact producer replacements')
    original_hist=Counter(); retained_hist=Counter(); removed_hist=Counter()
    prefix=Counter();suffix=Counter();same_payload=Counter();changed_core=Counter(); per_event=[]
    original_digest=sha256(); pair_digest=sha256();removed=[]; samples={}
    paired_count=0
    for event_index,event in enumerate(source.events):
        rows=[];kind=event['kind']
        if kind=='local_cover_sweep':
            call=source.calls[event['time']];direction=call['orientation']
            owners=source.owner_specs[event['time']]
            prelude=sum(1+bool(owner.entry) for owner in owners)
            for raw,pc,target,rank,native_kind in native[direction]:
                ident=[event_index,0,raw,prelude+pc]
                if event_index in (0,4) and native_kind=='center':
                    installed=None
                elif event_index in (0,4):
                    newpc,newtarget,newrank=clean[direction][raw]
                    need((target,rank)==(newtarget,newrank), 'paired native target/rank')
                    installed=[core_events[event_index],0,prelude+newpc]
                else:installed=[producer.source_events[event_index],0,prelude+pc]
                rows.append((ident,target,rank,installed))
        elif kind=='idle_cover_sweep':
            for subgroup in range(224):
                side,port=divmod(subgroup,112)
                child=event['child_indices'][side]
                rem=source.remainders.get((event['replica'],child,port))
                if not rem:continue
                family=896*event['replica']+(2*event['pair']+side)*112+port
                axes=data['phases']['recipes'][port]['idle_children'][child]['orthogonal_axes']
                active=axes[rem['pending_offset']:]
                need(rem['family']==family and len(active)==rem['rank'], 'literal idle geometry')
                rows.append(([event_index,subgroup,-1,1],0,len(active),
                             [producer.source_events[event_index],subgroup,1]))
        else:
            need(kind in {'bridge','terminal','terminal_Y_translations','bank_padding_cover_sweep',
                          'translate_every_live_family'}, 'nonchild source alphabet')
        h=Counter()
        for ident,target,rank,installed in rows:
            original_hist[rank]+=1;h[rank]+=1
            original_digest.update(canonical([ident,target,rank])+b'\n')
            if installed is None:
                removed_hist[rank]+=1;removed.append([ident,target,rank])
            else:
                paired_count+=1;retained_hist[rank]+=1
                (prefix if event_index<=6 else suffix)[rank]+=1
                (changed_core if event_index in (0,4) else same_payload)[rank]+=1
                pair_digest.update(canonical([ident,target,rank,installed])+b'\n')
                key=('prefix' if event_index<=6 else 'suffix')+':'+str(rank)
                samples.setdefault(key,{'source':ident,'target':target,'rank':rank,'installed':installed})
        per_event.append({'event':event_index,'kind':kind,**record(h)})
    need(original_hist==Counter({1:349604,2:60192,3:62585,4:20448,5:11808,7:7,8:1152,48:4866}),
         'whole original histogram')
    need(removed_hist==Counter({8:16}) and paired_count==510646, 'sixteen literal centre removals')
    need(sum(prefix.values())==17549 and sum(suffix.values())==493097, 'full suffix retained')
    need(sum(same_payload.values())==503674 and sum(changed_core.values())==6972,
         'same-payload calls versus changed producer cores')
    for i in (1,2,3):
        families={o.family for o in source.owner_specs[source.events[i]['time']]}
        need(len(families)==704 and families.isdisjoint(range(224)), 'intervening source family disjointness')
    idle_event=source.events[5]
    idle_families={896*idle_event['replica']+(2*idle_event['pair']+side)*112+p
                   for side in range(2) for p in range(112)}
    need(idle_families.isdisjoint(range(224)), 'source idle5 family disjointness')
    installed=retained_hist+Counter({1:len(added)})
    need(sum(installed.values())==510678, 'installed root count')
    bounds=lambda binding:(2,len(binding.events),max(1,*(binding.group_count(i) for i in range(len(binding.events)))),
                           binding.cover.size,65536,binding.slots+binding.private,binding.dimension)
    header=lambda binding:sum(max(1,(x-1).bit_length()) for x in bounds(binding))
    return {'unit':'one occurrence per cover owner; multiply every call count by Gamma once',
            'A_original':record(original_hist),'B_shared_protocol_only':record(original_hist),'B_protocol_only':record(original_hist),
            'C_D_root':record(installed),'service_calls':336,
            'retained':record(retained_hist),'retained_prefix':record(prefix),'retained_suffix':record(suffix),
            'same_payload_external_calls':record(same_payload),'changed_core_retained_calls':record(changed_core),
            'original_occurrence_sha256':original_digest.hexdigest(),
            'literal_pairing_sha256':pair_digest.hexdigest(),'per_event':per_event,
            'removed_literal_occurrences':removed,'added_literal_occurrences':added,
            'representative_pairs':samples,
            'header':{'A_B_bits':header(source),'C_D_bits':header(producer),
                      'A_B_events':len(source.events),'C_D_events':len(producer.events)},
            'pairing_scope':'Position and target/rank only. Prefix values and C execution costs are not equated.',
            'suffix_scope':'Source events 7..481; semantic continuation equality is inherited from #4166. Frozen D has independent primitive allocator history while B_shared matches A history; native action residual remains explicit.'}


def geometry(prefixes, rows, gamma, front, compact_bits, before, lam, spacing, after,
             back, coefficients, component_bits):
    """Exact physical volumes; check-only integers are not an encoded compiler."""
    values=locals().copy()
    need(all(type(v) is int and v>=0 for v in values.values()), 'integral nonnegative geometry')
    need(all(values[k]>0 for k in ('prefixes','rows','gamma','lam','spacing','coefficients','component_bits')),
         'positive physical dimensions')
    need(rows%(14336*gamma)==0, 'whole parent row stock divisor')
    unused=rows//(14336*gamma)
    exponent=front+3*compact_bits+before+73*lam*spacing+after+back
    row_bits=2*component_bits*coefficients*(1<<exponent)
    v=prefixes*unused*row_bits
    return {'row_bits':row_bits,'unused_rows':unused,'owner_packet_bits':v,
            'whole_family_bits':gamma*v,'parent_bank_bits':14336*gamma*v,
            'service_bank_bits':448*gamma*v,
            'child_packet_bits':prefixes*unused*2*component_bits*coefficients*
                (1<<(front+3*compact_bits+before+lam*spacing+(after+72*lam*spacing)+back)),
            'numerical_width':'component_bits is actual H_b, never logical W_c or address guard H_g',
            'stock_scope':'This checks one L divisor only; depth-law row-stock admission remains required.'}


def exact_decomposition(nonchild_A,nonchild_B,nonchild_D, A_calls,B_calls,D_retained_calls,
                        D_added_calls,service_D,retained_indices):
    """An exact operation sum, usable only with matched complete measurements.

    Each call value already includes preparation, entry, body/descendants and
    return. This prevents adding descendants again in this API. It does not
    certify cancellation or physical reachability of supplied measurements.
    """
    need(len(A_calls)==len(B_calls), 'literal A/B occurrence pairing')
    need(len(set(retained_indices))==len(retained_indices), 'unique retained occurrences')
    need(all(type(i) is int and 0<=i<len(A_calls) for i in retained_indices), 'retained domain')
    need(len(D_retained_calls)==len(retained_indices), 'D retained occurrence pairing')
    allcosts=[nonchild_A,nonchild_B,nonchild_D,service_D,*A_calls,*B_calls,*D_retained_calls,*D_added_calls]
    need(all(type(x) is int and x>=0 for x in allcosts), 'complete nonnegative action sums')
    A=nonchild_A+sum(A_calls);B=nonchild_B+sum(B_calls)
    D=nonchild_D+sum(D_retained_calls)+sum(D_added_calls)+service_D
    generic=B-A;incremental=D-B
    removed=set(range(len(A_calls)))-set(retained_indices)
    retained_credit=sum(A_calls[j]-f for j,f in zip(retained_indices,D_retained_calls))
    threshold=nonchild_D-nonchild_A+service_D+sum(D_added_calls)-sum(A_calls[j] for j in removed)
    need(D-A==generic+incremental==threshold-retained_credit, 'same-boundary identity')
    return {'A':A,'B':B,'D':D,'B_minus_A':generic,'D_minus_B':incremental,'D_minus_A':D-A,
            'retained_credit':retained_credit,'threshold':threshold,'D_beats_A':retained_credit>threshold,
            'D_beats_B':incremental<0}


def fair_threshold(census):
    need(census['retained_suffix']['calls']==493097 and census['retained']['calls']==510646,
         'full root and later occurrence coverage')
    need(census['A_original']['calls']==510662 and census['C_D_root']['calls']==510678,
         'original/installed complete counts')
    need(census['service_calls']==336 and census['header']=={'A_B_bits':2685,'C_D_bits':2687,
         'A_B_events':482,'C_D_events':1051}, 'full service and literal header domain')
    return {'generic':'T_B-T_A = (N_B-N_A) + sum_all_original (F_B(j)-F_A(j))',
            'incremental':'T_D-T_B = (N_D-N_B) + T_service_D + sum_retained (F_D(j)-F_B(j)) + sum_32_added F_D - sum_16_removed F_B',
            'full':'T_D-T_A = (T_B-T_A) + (T_D-T_B)',
            'C_minus_D':'11*B_bank+4-c_R; already credited by #4166, not multiplied by Gamma',
            'no_cancellation':['equal rank','equal mathematical output','matching histogram','unrelated upper bounds'],
            'unpriced_terms':['source-specific nonchild delta','changed-core payload-dependent C body delta','independent-versus-shared allocator context residual on same-payload calls',
                              'literal protocol/header context delta','complete service',
                              'fixed engine setup/cleanup and historical backing'],
            'fair_inventory':{'A':'678+M','B_shared':'678+M+J','B_independent_explored':'678+2M',
                              'C_D':'678+3M+2^20 sufficient roles',
                              'M':'2q^2+100696145','J':1023},
            'scientific_scope':'one changed outer root; descendants retain the original controller; no all-node substitution or exponent claim'}


def rejection_controls(census):
    import copy
    bad=copy.deepcopy(census);bad['retained_suffix']['calls']=0
    try:fair_threshold(bad)
    except ValueError:pass
    else:raise ValueError('omitted suffix accepted')
    for kwargs in ({'retained_indices':[0,0]}, {'retained_indices':[0,2]}):
        try:exact_decomposition(1,1,1,[3,4],[2,3],[2,3],[],0,**kwargs)
        except ValueError:pass
        else:raise ValueError('invalid occurrence pairing accepted')
    # Generic improvement does not imply a QQ16 improvement.
    toy=exact_decomposition(0,0,0,[20,20],[5,5],[5],[5,5],20,[0])
    need(toy['B_minus_A']==-30 and toy['D_minus_B']==25 and toy['D_minus_A']==-5,
         'generic credit and incremental expense remain distinct')
    return {'omitted_suffix':'rejected','duplicate_occurrence':'rejected','out_of_range_occurrence':'rejected',
            'generic_win_incremental_loss':toy,'toy_scope':'arithmetic accounting control, not a source execution'}


def count_body_length(value):
    need(type(value) is int and value>=0, 'canonical Count value')
    return max(1,value.bit_length())+1  # binary digits, then RIGHT


def capsule_injection(descriptors, rank, target_bits):
    """Finite checks of the proof's injective body-length comparison C <= S.

    The returned S0 is a lower bound: only the parent target and the distinct
    parent descriptor roles used by the injection are counted. The current
    parent bank, header and every other parked role provide additional stock.
    """
    names=('prefixes','rows','front','compact_bits','before','width','after','back',
           'spacing','guard','residue','component_bits','coefficients','root_width')
    need(set(descriptors)==set(names), 'exact fourteen descriptor domain')
    need(all(type(v) is int and v>=0 for v in descriptors.values()), 'Count descriptor values')
    d=descriptors
    need(type(rank) is int and 0<rank<73 and d['width']>0 and d['width']%73==0,
         'source child rank and post-remainder width')
    need(d['rows']>0 and d['prefixes']>0 and d['component_bits']>0 and d['coefficients']>0 and d['spacing']>0,
         'positive physical packet')
    need(type(target_bits) is int and target_bits>0, 'nonempty actual target')
    lam=d['width']//73
    exponent=d['front']+3*d['compact_bits']+d['before']+d['width']*d['spacing']+d['after']+d['back']
    row_bits=2*d['component_bits']*d['coefficients']*(1<<exponent)
    child_after=d['after']+(73-rank)*lam*d['spacing']
    need(child_after<=exponent<=row_bits, 'after Count dominated by derived row_bits Count')
    # The row Count in the capsule is already copied from the parent unused
    # role, regardless of its admitted L divisor or large depth stock.
    # Its common length cancels from the bound; use zero as a placeholder.
    unchanged=[n for n in names if n not in ('rows','width','after')]
    common=target_bits+sum(count_body_length(d[n]) for n in unchanged)
    common+=count_body_length(0)
    capsule=common+count_body_length(rank*lam)+count_body_length(child_after)
    injected=common+count_body_length(d['width'])+count_body_length(row_bits)
    need(capsule<=injected, 'injective canonical body length domination')
    return {'capsule_partial_length':capsule,'distinct_parent_roles_lower_bound':injected,
            'after_value':child_after,'row_bits':row_bits,
            'common_unused_placeholder':'same Count length on both sides; actual unused may be arbitrarily larger',
            'conclusion':'C<=S for admitted full physical geometry; no decoded descriptor arithmetic is proposed for the machine'}


def protocol_aggregate_bound(calls, gamma, bank_bits, parked_roles=732,
                             setup_cleanup=None, marker_correction_max=705):
    """Conditional complete-root consequence of PROTOCOL.md's exact delta.

    Total action unit is reads+writes+unit moves. Setup/cleanup is an exact
    nonnegative additional bill or a proved upper bound, never an absent zero.
    An absent setup/cleanup invoice leaves the net sign undecided.
    """
    need(all(type(x) is int and x>=0 for x in
             (calls,gamma,bank_bits,parked_roles,marker_correction_max)),
         'nonnegative complete protocol parameters')
    need(calls>0 and gamma>0 and bank_bits>0 and parked_roles>=1, 'nonempty invocation domain')
    need(setup_cleanup is None or type(setup_cleanup) is int and setup_cleanup>=0,
         'known setup/cleanup bound or explicit unknown')
    per_call_lower_credit=52*bank_bits+26*parked_roles-113-marker_correction_max
    credit=calls*gamma*per_call_lower_credit
    return {'raw_protocol_credit_lower_bound':credit,'per_call_credit_lower_bound':per_call_lower_credit,
            'setup_cleanup_upper_bound':setup_cleanup,'net_saving_lower_bound':None if setup_cleanup is None else credit-setup_cleanup,
            'strict_improvement_certified_if_setup_bound_admitted':None if setup_cleanup is None else credit>setup_cleanup,
            'unit':'read+write+unit-move actions','scope':'same arithmetic and source binding, original root calls only, actual sequentially shared primitive objects and allocator history',
            'threshold':'extra controller-bank setup/final cleanup < raw_protocol_credit_lower_bound',
            'marker_scope':'705=704 packet-origin corrections plus one protected-output correction; replace only under proved source lifecycle bound'}


def selected_whole_root_bound(census, gamma, q, startup_actions):
    """Uniform source-admitted-bank corollary, with an explicit setup invoice.

    Every complete owner packet has at least one bit, hence B_bank>=14336Gamma.
    q, Gamma and the startup invoice must be independently source-authenticated.
    """
    need(census['A_original']['calls']==510662, 'all original root calls')
    selected_gamma=1<<1296
    for i in range(1,37):selected_gamma*=(1<<(2*i))-1
    need(type(gamma) is int and gamma==selected_gamma, 'actual O(73,2) cover cardinality')
    need(type(q) is int and q==213*(1<<80)+1, 'fixed selected native parameter')
    need(type(startup_actions) is int and startup_actions>=0, 'paid setup and final retirement')
    bound=protocol_aggregate_bound(510662,gamma,14336*gamma,setup_cleanup=startup_actions)
    need(bound['net_saving_lower_bound']>0, 'complete startup-absorbing physical improvement')
    # Independently substitute C<=S into the three signed source invoices.
    # Read credit:18S-2C+10r-48. Write credit:18S+2r+1-epsilon.
    # Move credit:20S-2C+14r-66. Then S>=B_bank, r=732, epsilon<=705.
    coordinate_coefficients={'reads':(16,10*732-48),
                             'writes':(18,2*732+1-705),
                             'moves':(18,14*732-66)}
    need(sum(v[0] for v in coordinate_coefficients.values())==52 and
         sum(v[1] for v in coordinate_coefficients.values())==18214,
         'coordinate derivation agrees with total-credit algebra')
    coordinates={}
    for name,(slope,constant) in coordinate_coefficients.items():
        raw=510662*gamma*(slope*14336*gamma+constant)
        # Each nonnegative coordinate of the startup invoice is <= its total.
        # Subtracting that total separately is conservative, not three actual
        # startup charges in the whole execution bill.
        net=raw-startup_actions
        need(net>0, 'strict whole-root coordinate improvement:'+name)
        coordinates[name]={'per_call_bank_coefficient':slope,
                           'per_call_constant':constant,
                           'net_lower_bound_at_minimum_bank':net,
                           'net_lower_bound_bitlength':net.bit_length()}
    return {'minimum_bank_bits_used':14336*gamma,
            'minimum_bank_bits_bitlength':(14336*gamma).bit_length(),
            'startup_retirement_actions':startup_actions,
            'startup_retirement_bitlength':startup_actions.bit_length(),
            'saving_lower_bound':bound['net_saving_lower_bound'],
            'saving_lower_bound_bitlength':bound['net_saving_lower_bound'].bit_length(),
            'coordinate_savings':coordinates,
            'coordinate_startup_rule':'Subtract the total E_B bound from each coordinate independently; do not add these conservative bounds as an exact invoice.',
            'weighted_tariff_consequence':'Strict whole-root improvement for every fixed positive read/write/unit-move weight; separately priced finite control remains outside this conclusion.',
            'per_call_coefficient':'52*B_bank+18214',
            'whole_root_lower_bound':'510662*Gamma*(52*B_bank+18214)-E_B',
            'scope':'all nonleaf source-admitted selected roots; one modified root; original descendants; extra controller bank with sequentially shared primitive object/history admitted',
            'unit':'read+write+unit-move actions; separate finite-control charge excluded unless included in startup_actions'}


def suffix_header_cost(census):
    """Exact header-only suffix cost; native context residual is not cancelled."""
    h=census['header']; delta=h['C_D_bits']-h['A_B_bits']
    need(delta==2 and census['retained_suffix']['calls']==493097,'literal expanded header/suffix')
    return {'per_suffix_call_extra_header_actions':14*delta,
            'all_suffix_extra_header_actions_per_Gamma':493097*14*delta,
            'header_action_laws':{'write':'5h+4','read':'4h+7','clear':'5h+7'},
            'native_context_residual_status':'unresolved for frozen independent-engine D versus shared-primitive B; retained explicitly',
            'required_relation_for_total_suffix_cancellation':'same suffix bank/target/descriptor symbols and heads PLUS proved native allocator-history/codec action correspondence; equal payloads are insufficient',
            'excludes':'native allocator/context residual on every suffix call; separately priced finite-control fence predicates; changed-core payload-dependent differences, service and new/removed calls'}


def matched_external_header_cost(census):
    """Include unchanged intervening source calls, retaining the changed cores.

    #4166 supplies complete helper endpoints and disjoint intervening-family
    semantics. Shared B and frozen independent D can still differ in native
    allocator history. This is only the explicit header component.
    """
    need(census['same_payload_external_calls']['calls']==503674 and
         census['changed_core_retained_calls']['calls']==6972, 'exact semantic call partition')
    suffix=suffix_header_cost(census)
    return {'same_payload_retained_calls_per_Gamma':503674,
            'same_payload_prefix_calls_per_Gamma':10577,
            'changed_core_retained_calls_per_Gamma':6972,
            'header_extra_actions_per_call':28,
            'matched_retained_header_extra_actions_per_Gamma':503674*28,
            'suffix':suffix,
            'native_context_residual_calls_per_Gamma':503674,
            'complete_incremental_identity':'N_D-N_B + T_service_D + 14102872*Gamma + sum_503674 nonheader_call_context_residual + sum_6972 changed_core_call_delta + sum_32_added F_D - sum_16_removed F_B',
            'scope':'same-payload semantic partition plus exact header component only; independent D versus shared B native context residual remains on all503674 calls; changed core calls are not cancelled'}
