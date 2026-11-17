def final_application(root):
    native = read(root / 'producer54/validation_native/NATIVE-RESULT.json')
    signed = read(root / 'producer54/validation_signed/RESULT.json')
    old = read(HERE / 'data/7642-FINAL.json')
    assert native['status'] == NATIVE_MARKER and signed['status'] == SIGNED_MARKER
    assert native['word_canonical_sha256'] == digest(canonical(read(HERE / 'data/word.json.gz')))
    assert signed['price']['new_native'] == native['word_canonical_sha256']
    assert signed['caller_sha256'] == '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
    assert signed['assumptions'] == old['assumptions']
    assert native['native']['lifetimes'] == 74 and native['native']['owned_peak'] == 50
    assert native['derived_grid']['odd_scale'] == 1125 and native['derived_grid']['fractional_bits'] == 25
    assert native['controls'] and all(native['controls'].values())
    required_controls = (
        'wrong_helper757_source', 'missing_helper757_paid_move', 'missing_main46_paid_move',
        'wrong_main46_move_source', 'missing_main46_coframe_correction',
    )
    assert all(native['controls'][name] for name in required_controls)
    assert native['charts']['main46_composed_columns'] == native['charts']['main46_composed_adjoint_columns'] == 512
    assert native['charts']['wrong_phase_rejected']
    pairs = {tuple(item['pair']): item for item in native['charts']['all_affected_pairs']}
    for pair, rank in (((3, 618), 3), ((716, 807), 3), ((327, 907), 5), ((618, 913), 4), ((729, 808), 2), ((3, 603), 2), ((914, 245), 1), ((245, 127), 1), ((914, 127), 2)):
        item = pairs[pair]
        assert item['rank'] == rank and item['columns'] == item['adjoint_columns'] == 512 and item['absolute_phase_verified']
    assert native['physical_checks'] == ['verify_host3_odd.py', 'physical.py']
    price = signed['price']
    invoice = price['after']
    target = read(HERE / 'data/invoice-new.json')
    assert invoice['P'] == target['paid'] and invoice['T'] == target['targets']
    assert invoice['S'] == 1424 and invoice['empty_root_credits'] == 0
    assert sum(invoice['P'].values()) == 110332 and sum(invoice['T'].values()) == 22461
    checks = signed['checks']
    partial = checks['ODD-ADMISSION-PARTIAL.json']
    assert partial['invoice'] == invoice and partial['compiler_outer'] == price['gate']
    for gate in (price['gate'], price['public_claim_gate']):
        outer = gate['outer']
        assert outer['strict_count'] == 54 and outer['functional_count'] == 4
        assert Q(outer['minimum_margin']) > 0 and outer['BIT_just_below_effective_rejected']
    assert Q(price['public_claim_gate']['claim']) == Q(PUBLIC_CLAIM)
    assert Q(price['public_claim_gate']['tested']) == Q(PUBLIC_CLAIM) + Q(7,10**14)
    ordinary = partial['ordinary']['conservative_total']
    assert ordinary == 782668204 < 10**9
    joined = checks['ODD-8X9-APPLICATION-CHECKS.json']
    assert joined['status'] == 'PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS'
    assert joined['native_canonical_sha256'] == native['word_canonical_sha256']
    assert joined['caller_sha256'] == signed['caller_sha256']
    catalogue = signed['catalogue']
    maps = sum(item['checked_maps'] for item in catalogue)
    assert catalogue and all(item['catalogue_size'] == maps for item in catalogue)
    assert sum(item['main_boundary_pairs'] for item in catalogue) == 104
    tape = checks['ODD-FIXED-TAPE-COUNTS.json']
    precision = checks['ODD-PRECISION.json']
    assert tape['context_c'] == precision['context_c'] and tape['native_invocations'] == 17
    public_h = int(price['public_claim_gate']['H'])
    public_kstar = 1920 * 153**1920 * (public_h + 1)**2
    public_context_bits = (4096 * public_kstar).bit_length()
    assert precision['context_c'] <= 4096 and public_context_bits < public_h
    assert max(item['strict_power_of_two'] for item in precision['rounded_caller']['bounds'].values()) < public_h
    fields = ('native_invocations', 'monomial_map_slots', 'elementary_records_upper', 'scalar_services_upper')
    return dict(status='PASS_CONTACT134_329_FINAL_APPLICATION', claim=PUBLIC_CLAIM,
                framework_claim=signed['claim'], raw_crossing=price['gate']['raw_bracket'],
                candidate_canonical_sha256=native['word_canonical_sha256'], caller_sha256=signed['caller_sha256'],
                paid_calls=110332, productive_calls=22461, surplus=1424,
                ordinary_bound=ordinary, ordinary_change_over_7642=ordinary-old['ordinary_bound'],
                precision_c=precision['context_c'], tape={k: tape[k] for k in fields},
                public_context_bound_bits=public_context_bits, public_H=public_h,
                comparator_claim=old['framework_claim'], comparator_crossing=old['raw_crossing'],
                public_claim_derivation='Weakening the stronger complete framework claim; tape H inequalities also checked at the public gate.',
                tape_change_over_7642={k: tape[k]-old['tape'][k] for k in fields},
                outer=price['public_claim_gate']['outer'], signed_physical_map_count=maps,
                assumptions=signed['assumptions'])

