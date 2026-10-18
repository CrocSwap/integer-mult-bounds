"""Bounded real-input mutations for the pinned T16 invoice checker.

Tairitsu-Aya, with OpenAI Codex assistance. Apache-2.0.
"""
import marshal


def copy(value):
    return marshal.loads(marshal.dumps(value))


def build_cases(baseline, baseline_invoice, invoice):
    def assign(key, field, value):
        return lambda data: data[key].__setitem__(field, value)

    def increment(key, field, delta=1):
        return lambda data: data[key].__setitem__(field, data[key][field]+delta)

    cases = []
    def add(name, change, rebind=True):
        cases.append((name, change, rebind))

    add('owner status false', assign('owner', 'status', 'FAIL'))
    add('controller status false', assign('controller', 'status', 'FAIL'))
    add('controller complete calls understated', increment('controller', 'complete_invocations', -1))
    add('controller unique owner flag false', assign('controller', 'one_owner_per_complete_invocation', False))
    add('controller mutations flag false', assign('controller', 'mutation_controls_run', False))
    add('controller mutation list empty', assign('controller', 'mutations_rejected', []))
    add('controller rank mass inconsistent', increment('controller', 'rank_mass'))
    add('owner rank mass inconsistent', increment('owner', 'rank_mass'))
    add('owner deficit inconsistent', increment('owner', 'deficit'))
    add('owner live inconsistent', increment('owner', 'live'))
    add('owner physical inconsistent', increment('owner', 'physical'))
    add('owner distinct owner flag false', assign('owner', 'all_live_owners_per_call_distinct', False))
    add('owner chart count understated', increment('owner', 'actual_helper_owner_charts', -1))
    add('owner idle remainder count understated', increment('owner', 'explicit_idle_remainder_children', -1))
    add('owner idle source count understated', increment('owner', 'source_idle_children_charged', -1))
    add('owner idle count exceeds source', assign('owner', 'explicit_idle_remainder_children', 32257))
    add('owner controller hash stale', assign('owner', 'controller_audit_sha256', '0'*64), False)
    add('controller template hash stale', assign('controller', 'complex_template_sha256', '0'*64), False)
    add('owner template hash stale', assign('owner', 'template_sha256', '0'*64), False)
    add('summary template hash stale', assign('summary', 'template_sha256', '0'*64), False)
    add('template physical reserve understated', increment('template', 'physical', -1))
    add('template live count understated', increment('template', 'live', -1))
    add('template calls reversed', lambda d: d['template']['calls'].reverse())
    add('template call omitted', lambda d: d['template']['calls'].pop())
    add('template duplicate call', lambda d: d['template']['calls'].__setitem__(1, copy(d['template']['calls'][0])))
    add('template helper aliases data owner', lambda d: d['template']['calls'][0]['owners'].__setitem__(224, copy(d['template']['calls'][0]['owners'][0])))
    add('template idle children omitted', lambda d: d['template'].__setitem__('idle_children', []))
    add('template bank padding restored', lambda d: d['template']['bank_padding'].__setitem__('families', [14336]))
    bridge = next(i for i,e in enumerate(baseline['template']['execution_schedule']) if e['kind']=='bridge')
    sweep = next(i for i,e in enumerate(baseline['template']['execution_schedule']) if e['kind']=='local_cover_sweep')
    add('bridge coefficient sign flipped', lambda d: d['template']['execution_schedule'][bridge].__setitem__('coefficient', -d['template']['execution_schedule'][bridge]['coefficient']))
    add('bridge coefficient exceeds charged payload', lambda d: d['template']['execution_schedule'][bridge].__setitem__('coefficient', 2**513))
    add('bridge omitted', lambda d: d['template']['execution_schedule'].pop(bridge))
    add('sweep provider changed', lambda d: d['template']['execution_schedule'][sweep].__setitem__('provider_id', 'missing'))
    add('call program hash stale', lambda d: d['template']['calls'][0].__setitem__('local_program_sha256', '0'*64))
    add('parent idle multiplicity understated', lambda d: d['parent']['idle_children'][0].__setitem__('replicas', d['parent']['idle_children'][0]['replicas']-1))
    add('parent bank stock coherently understated', lambda d: (d['parent'].__setitem__('live', d['parent']['live']-9), d['parent'].__setitem__('physical',d['parent']['physical']-9)))
    add('parent physical stock inconsistent', increment('parent', 'physical', -1))
    add('retained compiler changed', increment('retained', 'compiler'))
    add('retained payload changed', increment('retained', 'charged_prefix_bits', -1))
    add('retained allowance zero', assign('retained', 'conservative_pervertex_used', 0))
    add('retained allowance one', assign('retained', 'conservative_pervertex_used', 1))
    add('retained allowance negative', assign('retained', 'conservative_pervertex_used', -1))
    add('retained allowance breaches logical guard', assign('retained', 'conservative_pervertex_used', 2**4000))

    def move_mass(d):
        d['owner']['paid_profile']['1'] += 2
        d['owner']['paid_profile']['2'] -= 1
    add('owner rank histogram changed with mass preserved', move_mass)

    def negative_count(d):
        d['owner']['paid_profile']['1'] += 56
        d['owner']['paid_profile']['7'] = -1
    add('owner negative rank count with mass preserved', negative_count)
    add('owner negative zero rank count', lambda d: d['owner']['paid_profile'].__setitem__('0', -1))

    def understock(d):
        for field in ('live','physical'):
            d['template'][field] -= 1
            d['owner'][field] -= 1
        d['owner']['rank_mass'] -= 73
        d['owner']['paid_profile']['1'] -= 73
    add('live stock and profile coherently understated', understock)

    def halving(d):
        d['owner']['paid_profile']['1'] -= 52
        d['owner']['paid_profile']['52'] = 1
    add('finite halving exceeds rank limit', halving)

    group = 2**(36*36)
    for j in range(1,37):
        group *= 2**(2*j)-1
    first_bad_stock = (2**4487+group-1)//group
    def row_limit(d, delta):
        physical = first_bad_stock+delta
        live = physical-490
        d['template']['physical'] = d['owner']['physical'] = physical
        d['template']['live'] = d['owner']['live'] = live
        d['owner']['rank_mass'] = 73*live-5120
        d['owner']['paid_profile'] = {'1': d['owner']['rank_mass']}
        parent_live = 14336+9*((live-14336+8)//9)
        d['parent']['live'] = parent_live
        d['parent']['physical'] = parent_live+514
    add('finite row just below limit', lambda d: row_limit(d,-1))
    add('finite row at rejected limit', lambda d: row_limit(d,0))

    last_good_used = (2**6050-65)//group
    for delta, label in ((0,'below'),(1,'above')):
        add('finite logical just '+label+' limit',
            assign('retained', 'conservative_pervertex_used',
                   last_good_used-baseline_invoice['unhosted_pervertex']+delta))

    def prefix_limit(d, power):
        # Two inverse dyadic scales preserve the endpoint but force an exact
        # intermediate magnitude 2**power. Rebind the claimed local receipts;
        # this is an adversarial supplier input, not a fresh native replay.
        events = d['programs']['forward']
        events[1:1] = [['scalar',['scale',['L',0],2**power,1],0],
                       ['scalar',['scale',['L',0],1,2**power],0]]
        check = d['checks']['forward']
        check['events'] += 2
        check['scalar_macros'] += 2
        check['real_component_primitive_bound'] += 4*power
        check['sha256'] = invoice.programhash(events)
        local = d['native']['local']['forward']
        local['prefix_l1_upper'] = str(2**power)
        local['prefix_bits_upper'] = power+1
        registry = d['template']['local_providers']['gauge44']
        registry['local_programs'] = d['programs']
        registry['local_program_checks'] = d['checks']
        for call in d['template']['calls']:
            if call['orientation']=='forward':
                call['local_program_sha256'] = check['sha256']
    for power in (181,182,183):
        add('finite prefix '+str(power+330)+' bits', lambda d,power=power: prefix_limit(d,power))

    return cases
