# SPDX-License-Identifier: Apache-2.0
"""Exact comparison identities and invocation-site accounting; no runtime oracle.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
The controller, Compact and Ordinary source remains credited to Jose Manuel;
#4166/#4167 supply the frozen caller and occurrence census. Integer calculations
here are checkers, never an encoded allocator, reset or packet compiler.
"""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def natural(value, positive=False):
    need(type(value) is int and value >= int(positive), 'integer cardinality')
    return value


def invocation_sites(columns, outer_rows, early_gates, late_gates):
    """Actual Ordinary.run calls in one successful source MonomialEngine.run.

    Reference Compact.operations emits four swaps for an early/constant gate
    and twelve for a late gate. For columns=1 the monomial bypasses Compact.
    For columns>1 every swapped field has (columns-1)*G positive width.
    Returned counts exclude all calls in other monomials and descendants.
    """
    for x in (columns, outer_rows): natural(x, True)
    for x in (early_gates, late_gates): natural(x)
    return 0 if columns == 1 else outer_rows*(4*early_gates+12*late_gates)


def radix_digits(binary_width, radix):
    """Checker for Binary.run's encoded multiply-until-radix>=2**width loop."""
    natural(binary_width, True); natural(radix, True)
    need(radix >= 2, 'compiled radix')
    power, digits = 1, 0
    while power < (1 << binary_width):
        power *= radix
        digits += 1
    return digits


def census_contract(census):
    expected = {'original':510662, 'same_payload':503674,
                'changed_core':6972, 'added':32, 'removed':16,
                'service':336, 'later':493097}
    need(type(census) is dict and set(census)==set(expected), 'complete occurrence partition')
    need(all(type(census[k]) is int and census[k]==v for k,v in expected.items()),
         'literal frozen root census')
    need(census['same_payload']+census['changed_core']+census['removed']==census['original'],
         'original partition')
    return {'counts_per_Gamma':dict(expected),
            'matched_header_actions_per_Gamma':28*census['same_payload'],
            'later_header_actions_per_Gamma':28*census['later'],
            'all_retained_header_actions_per_Gamma':28*(census['same_payload']+census['changed_core']),
            'root_installed_per_Gamma':census['original']-census['removed']+census['added'],
            'all_external_D_per_Gamma':census['original']-census['removed']+census['added']+census['service']}


CENSUS = {'original':510662, 'same_payload':503674, 'changed_core':6972,
          'added':32, 'removed':16, 'service':336, 'later':493097}


def complete_difference(*, gamma, nonchild_difference, service,
                        native_history_residual, other_same_payload_residual,
                        changed_core_difference, added, removed,
                        extra_control_difference=0):
    """Exact signed sum ONLY when supplied terms are complete matched totals.

    All supplied costs except header are already whole-root, including Gamma.
    service includes its 336 children and every descendant/copy exactly once.
    Never call this with an unproved subtraction of upper bounds.
    """
    natural(gamma, True)
    signed=(nonchild_difference,native_history_residual,other_same_payload_residual,
            changed_core_difference,extra_control_difference)
    need(all(type(x) is int for x in signed), 'signed exact action differences')
    for x in (service,added,removed): natural(x)
    header=14102872*gamma
    return nonchild_difference+service+header+native_history_residual+other_same_payload_residual+changed_core_difference+added-removed+extra_control_difference


def scan_volume(gamma, bank_bits):
    """Exact difference in full-bank group volume, a separate diagnostic unit.

    Inherited emitted-group census, not an R/W/M total. Service bank=B/32.
    New producer groups replace two groups; later groups cancel only in this
    geometric volume metric. Fence/acquisition scans are additional.
    """
    natural(gamma,True); natural(bank_bits,True)
    need(gamma%51==0 and bank_bits%32==0, 'complete cover and family-bank geometry')
    producer=Fraction(14479,51)*gamma*bank_bits
    original=2*gamma*bank_bits
    service=2022*gamma*(bank_bits//32)
    difference=producer+service-original
    need(difference==Fraction(281593,816)*gamma*bank_bits and difference.denominator==1,
         'complete source group scan volume')
    return {'unit':'sum of complete bank bit lengths over emitted gather/scatter groups',
            'producer':int(producer), 'original_replaced':original,
            'service':service,'difference':int(difference),
            'coefficient_Gamma_times_B_bank':'281593/816',
            'not_a_tape_action_lower_bound_on_total_difference':True}


def adoption_adjustment(gamma, owner_packet_bits, *, adopt_D=False):
    """Exact action adjustment of the frozen D-B identity for fair B* / D*.

    B* saves 11v+4 on every original child. D* is a separately implemented
    variant only; if supplied it must save at all root AND service child sites.
    It is not silently substituted for frozen D.
    """
    natural(gamma,True); natural(owner_packet_bits,True)
    need(type(adopt_D) is bool,'explicit new D variant')
    per=11*owner_packet_bits+4
    baseline=510662*gamma*per
    candidate=(510678+336)*gamma*per if adopt_D else 0
    return {'B_star_saving':baseline,'new_D_star_saving':candidate,
            'incremental_difference_adjustment':baseline-candidate,
            'finite_binding_control':'additional signed control charges remain separate',
            'scope':'all child packets have the same owner packet extent v under inherited source geometry; descendants unchanged'}


def check_sources(source):
    """Fail-closed structural controls on already authenticated source text.

    This supplements the written proof; substring checks are not a parser proof.
    The caller must authenticate these bytes before this function is used.
    """
    expected={'binary','compact','monomial','ordinary','reference'}
    need(set(source)==expected and all(type(v) is str for v in source.values()),'source closure')
    required={
      'binary':('if width.zero():','returned = self.native.run(', 'digits.increment()'),
      'compact':('for operation in control.operations:', 'while not rows.finished:',
                 'returned = self.binary.run(', 'self.calls["ordinary"] += 1'),
      'monomial':('if n.zero():','self.single_column_rows(', 'self.compact_gate('),
      'ordinary':('if plan["fits"] else','lambda: select(original, self.q, self.profile)'),
      'reference':('def operations(self):','ops.append(("swap",front,"b"))',
                   'if self.late:', 'else:flip(self.source)')}
    for name, needles in required.items():
        need(all(s in source[name] for s in needles),'actual source invocation site: '+name)
    return {'source_site_controls':'passed','scope':'source-structure regression, not branch execution evidence'}


def reduced_threshold(*, gamma, nonchild_and_startup_difference,
                      unmatched_protocol_difference, rank_one_body,
                      rank_eight_body, finite_control_difference=0):
    """Context/payload theorem's reduced COMPLETE action threshold.

    E_r is one complete original C.run including descendants at the common
    admitted child geometry and a named marker class. Nonchild/startup contains
    acquisition/compiler/service nonchild/scalar/maps/scans/publication/disposal
    and any first-use marker-class corrections. Unmatched protocol contains the
    32 producer and 336 service shells minus 16 B shells, excluding E_r and
    already multiplied by Gamma. This exact API does not manufacture these prices.
    """
    natural(gamma,True);natural(rank_one_body);natural(rank_eight_body)
    need(all(type(x) is int for x in (nonchild_and_startup_difference,
         unmatched_protocol_difference,finite_control_difference)), 'signed exact difference')
    positive=nonchild_and_startup_difference+unmatched_protocol_difference+14298088*gamma+368*gamma*rank_one_body
    removed=16*gamma*rank_eight_body
    return {'D_minus_B_actions':positive-removed,
            'D_minus_B_with_additional_control':positive-removed+finite_control_difference,
            'necessary_and_sufficient_threshold': '16 Gamma E_8 > Delta_nonchild_startup + Delta_unmatched_protocol + 14298088 Gamma + 368 Gamma E_1',
            'remaining_budget_after_new_rank_one_bodies_and_headers': removed-368*gamma*rank_one_body-14298088*gamma,
            'prices_are_supplied_exact_totals_not_bounds':True}


def check(prior_census=None, mechanism_contract=None):
    census=census_contract(CENSUS)
    if prior_census is not None:
        need(prior_census['same_payload_external_calls']['calls']==503674 and
             prior_census['changed_core_retained_calls']['calls']==6972 and
             prior_census['retained_suffix']['calls']==493097 and
             prior_census['retained']['calls']==510646,'authenticated prior literal census')
    # The theorem is reported separately; passing a label cannot prove it.
    if mechanism_contract is not None:
        need(isinstance(mechanism_contract,dict),'explicit mechanism receipt')
    need(census['matched_header_actions_per_Gamma']==14102872 and
         census['later_header_actions_per_Gamma']==13806716,'header arithmetic')
    cases=[]
    for columns,rows,early,late in ((1,7,2,3),(2,1,1,0),(2,3,0,1),(4,5,7,2)):
        cases.append({'columns':columns,'outer_rows':rows,'early':early,'late':late,
                      'actual_ordinary_calls':invocation_sites(columns,rows,early,late)})
    need([x['actual_ordinary_calls'] for x in cases]==[0,4,36,260],'literal swap schedule')
    rejected=[]
    for label,action in (
      ('omitted later calls',lambda:census_contract(dict(CENSUS,later=0))),
      ('bool alias in multiplicity',lambda:census_contract(dict(CENSUS,service=True))),
      ('callback count used as ordinary count',lambda:need(invocation_sites(2,3,0,1)==1,'wrong invocation count')),
      ('missing removal charge',lambda:need(complete_difference(gamma=1,nonchild_difference=0,service=0,native_history_residual=0,other_same_payload_residual=0,changed_core_difference=0,added=0,removed=14102873)==0,'removed calls retained')),
      ('double Gamma publication',lambda:need(11*(14336*51)+4==51*(11*(14336*51)+4),'whole bank contains Gamma'))):
        try: action()
        except ValueError: rejected.append(label)
        else: raise ValueError('cost control accepted: '+label)
    # Source-level exact identity can have either sign after native history=0.
    common=dict(gamma=1,nonchild_difference=0,service=1,native_history_residual=0,
                other_same_payload_residual=0,changed_core_difference=0,added=1)
    positive=complete_difference(**common,removed=0)
    negative=complete_difference(**common,removed=positive+1)
    need(positive>0 and negative==-1,'zero history residual does not determine total sign')
    return {'census':census,'monomial_invocation_cases':cases,
            'radix_digit_controls':[radix_digits(1,2),radix_digits(4,3),radix_digits(9,5)],
            'scan_volume_control':scan_volume(51,14336*51),
            'fair_B_star_adjustment_control':adoption_adjustment(51,3),
            'fair_both_adopt_adjustment_control':adoption_adjustment(51,3,adopt_D=True),
            'rejections':rejected,
            'sign_controls':{'positive':positive,'negative':negative,'synthetic_accounting_only':True},
            'remaining_terms':['nonchild matched difference including all full-bank groups and fence predicates',
                               'complete service assembly/compiler/extraction/cleanup and336Gamma children',
                               'complete geometric rank-one and rank-eight original C body prices after all retained history/payload differences cancel',
                               '32Gamma complete added calls minus16Gamma complete B removed calls',
                               'separately compiled finite control and historical backing'],
            'all_retained_reduced_threshold': 'Delta_nonchild_startup + Delta_unmatched_protocol + 14298088 Gamma + 368 Gamma E_1 - 16 Gamma E_8',
            'reduced_threshold_accounting_control':reduced_threshold(gamma=1,nonchild_and_startup_difference=10,unmatched_protocol_difference=20,rank_one_body=2,rank_eight_body=1000000),
            'scientific_claim':'The history/payload theorem removes retained body price uncertainty; unpriced nonchild and E_1/E_8 terms prevent a full QQ16 sign.'}
