"""Independent literal caller census, field allocation, and Decimal diagnostic.

Only the separately written sibling check_native is imported. No primary
constructor, caller evaluator, pricing module, or interval engine is imported.
Jerry Chen / @CubeJerry, substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

from check_native import chronology, require, word


CLAIM = '.00330814'
TESTED = '.003308145'
CERTIFIED_RAW_LOWER = '.0033081451891'


ROLE_SLOTS = {
    'ADD': (1, 2), 'SCALE': (1,), 'SWAP': (1, 2), 'LAMBDA': (1,),
    'QUERY': (1, 2), 'LOCAL': (2, 3), 'IDLE': (1, 2), 'IDLE_ONE': (1,),
}


def inverse(gates):
    answer = []
    for gate in reversed(gates):
        gate = gate.copy()
        if gate[0] == 'ADD':
            gate[-1] = str(-Fraction(gate[-1]))
        elif gate[0] == 'SCALE':
            gate[-1] = str(1 / Fraction(gate[-1]))
        elif gate[0] == 'LAMBDA':
            gate[-1] = -gate[-1]
        else:
            require(gate[0] == 'SWAP', 'invertible ordinary retirement gate')
        answer.append(gate)
    return answer


def rebuild_retirements(base, witnesses, first, final):
    """Bind both complete literals to their declared ordinary basis edits."""
    current = deepcopy(base)
    result = []
    for witness, recorded in zip(witnesses, (first, final)):
        pivot, fresh = witness['pivot'], witness['fresh']
        cut = witness['cut_after']
        require(fresh == current['roles'], 'one independent new caller role')
        require(current['events'][cut] ==
                ['IDLE_ONE', 2, witness['prefix_stages']], 'retirement cut')
        before = (witness['input_basis'] + current['events'][:cut + 1] +
                  witness['cut_basis'])
        after = inverse(witness['cut_basis']) + current['events'][cut + 1:] + inverse(witness['input_basis'])
        after = deepcopy(after)
        for gate in after:
            for slot in ROLE_SLOTS[gate[0]]:
                if gate[slot] == pivot:
                    gate[slot] = fresh
        require(len(before) - 1 == witness['handoff_after'], 'handoff index')
        require(all(fresh != gate[slot] for gate in before
                    for slot in ROLE_SLOTS[gate[0]]), 'fresh role untouched in prefix')
        require(all(pivot != gate[slot] for gate in after
                    for slot in ROLE_SLOTS[gate[0]]), 'retired role untouched in suffix')
        prefix = [0] * (current['stages'] + 2)
        prefix[0] = -witness['head']
        for stage in witness['prefix_stages']:
            prefix[stage + 1] = 1
        suffix = [a - b for a, b in zip(current['diagonal'][pivot], prefix)]
        require(prefix == witness['prefix_target'] and
                suffix == witness['suffix_target'], 'split target exponents')
        current['events'] = before + after
        current['diagonal'][pivot] = prefix
        current['diagonal'].append(suffix)
        current['roles'] += 1
        current['schema'] = 'two-paid-fragments-two-independent-retirements/1'
        require(current == recorded, 'entire reconstructed caller literal')
        result.append(dict(pivot=pivot, fresh=fresh, cut=cut,
                           events=len(current['events']), roles=current['roles']))
    return result


def caller_columns(caller):
    """Exact reverse adjoint over Q(i)[q,C1,...,C18]/(q^4-1).

    A key (output, q-exponent, stage-exponents) in variable j describes the
    contribution of intermediate variable j to that output. At the entry it
    is precisely input column j. All initial caller variables are arbitrary.
    """
    n, stages = caller['roles'], caller['stages']
    zero = (0,) * stages
    variables = [{(j, 0, zero): (Fraction(1), Fraction(0))} for j in range(n)]

    def add(dst, src, real=Fraction(1), imag=Fraction(0), qshift=0, stage_shift=()):
        for (output, qpower, powers), (a, b) in src.items():
            key = (output, (qpower + qshift) % 4,
                   tuple(v + int(j + 1 in stage_shift) for j, v in enumerate(powers)))
            old_a, old_b = dst.get(key, (Fraction(0), Fraction(0)))
            value = (old_a + real * a - imag * b, old_b + real * b + imag * a)
            if value == (0, 0):
                dst.pop(key, None)
            else:
                dst[key] = value

    for event in reversed(caller['events']):
        operation = event[0]
        if operation == 'ADD':
            add(variables[event[2]], variables[event[1]], Fraction(event[3]))
        elif operation == 'SCALE':
            result = {}
            add(result, variables[event[1]], Fraction(event[2]))
            variables[event[1]] = result
        elif operation == 'SWAP':
            variables[event[1]], variables[event[2]] = variables[event[2]], variables[event[1]]
        elif operation == 'LAMBDA':
            result, sign = {}, event[2]
            require(sign in (-1, 1), 'ordinary Lambda direction')
            add(result, variables[event[1]], Fraction(1, 2), Fraction(sign, 2))
            add(result, variables[event[1]], Fraction(1, 2), Fraction(-sign, 2), qshift=2)
            variables[event[1]] = result
        elif operation == 'QUERY':
            _, dst, src, power = event
            require(power in (-1, 1), 'thin query orientation')
            add(variables[src], variables[dst], qshift=power)
        elif operation == 'LOCAL':
            _, stage, src, dst = event
            # Pull back both D_stage diagonal maps before the Q^-1 shear.
            for role in (src, dst):
                result = {}
                add(result, variables[role], stage_shift=(stage,))
                variables[role] = result
            add(variables[src], variables[dst], qshift=-1)
        elif operation in ('IDLE', 'IDLE_ONE'):
            roles = event[1:3] if operation == 'IDLE' else event[1:2]
            selected = event[3] if operation == 'IDLE' else event[2]
            for role in roles:
                result = {}
                add(result, variables[role], stage_shift=selected)
                variables[role] = result
        else:
            raise ValueError('unknown caller opcode: ' + operation)
    for role, actual in enumerate(variables):
        diagonal = caller['diagonal'][role]
        require(diagonal[1] == 0, 'absent old stage zero')
        expected = {(role, diagonal[0] % 4, tuple(diagonal[2:])):
                    (Fraction(1), Fraction(0))}
        require(actual == expected, 'complete arbitrary-input caller column ' + str(role))
    return dict(inputs=n, coefficients=n*n, direction='reverse adjoint',
                ring='Q(i)[q,C1,...,C18]/(q^4-1)')


def invoice(caller, local):
    target, paid, idle, main = Counter(), Counter(), Counter(), Counter()
    counts, stages = Counter(), []
    require(caller['roles'] == len(caller['diagonal']) == 34 and
            caller['stages'] == 18 and caller['ambient_rank'] == 153,
            'complete final caller dimensions')
    for event in caller['events']:
        operation = event[0]
        counts[operation] += 1
        require(operation in ROLE_SLOTS, 'recognized complete caller instruction')
        used = [event[slot] for slot in ROLE_SLOTS[operation]]
        require(all(type(role) is int and 0 <= role < caller['roles'] for role in used),
                'actual caller role in range')
        require(len(set(used)) == len(used), 'distinct source and destination roles')
        if operation == 'LOCAL':
            stages.append(event[1])
            target.update(local['helpers'])
            paid.update(local['paid'])
        elif operation == 'QUERY':
            paid[1] += 104
        elif operation in ('IDLE', 'IDLE_ONE'):
            selected = event[3] if operation == 'IDLE' else event[2]
            require(len(selected) == len(set(selected)) and
                    all(1 <= stage <= 18 for stage in selected), 'whole fresh idle axes')
            rank, multiplicity = 8*len(selected), 104*len(used)
            require(rank > 0, 'nontrivial whole idle')
            paid[rank] += multiplicity
            idle[rank] += multiplicity
    require(stages == list(range(1, 19)), 'all eighteen distinct forward native calls')
    for diagonal in caller['diagonal']:
        require(len(diagonal) == 20 and diagonal[0] in (-1, 0, 1) and
                diagonal[1] == 0 and all(x in (0, 1) for x in diagonal[2:]),
                'full main target exponent format')
        rank = int(bool(diagonal[0])) + 8*sum(diagonal[2:])
        require(rank > 0, 'every credited main output productive')
        main[rank] += 104
    target.update(main)
    require(counts == {'ADD': 275, 'SCALE': 86, 'SWAP': 94, 'LAMBDA': 100,
                       'LOCAL': 18, 'QUERY': 15, 'IDLE': 12, 'IDLE_ONE': 6},
            'complete literal caller census')
    require(sum(main.values()) == 34*104, 'all main outputs exactly once')
    return target, paid, main, idle, counts


def allocation(caller, native):
    main_roles = set(native['live']) | {role+112 for role in native['live']}
    helpers = sorted(set(range(native['public'])) - main_roles)
    require(len(helpers) == 564, 'all independent helper roles')
    main_count = 104*caller['roles']
    public_count = main_count + 18*len(helpers)
    owned = set(range(public_count, public_count + native['owned_fields']))
    all_helpers, invocations = set(), []
    for _, stage, src, dst in (e for e in caller['events'] if e[0] == 'LOCAL'):
        mapping = {}
        for port, role in enumerate(native['live']):
            mapping[role] = 104*src + port
            mapping[role+112] = 104*dst + port
        helper_ids = set()
        for ordinal, role in enumerate(helpers):
            allocated = main_count + (stage-1)*len(helpers) + ordinal
            mapping[role] = allocated
            helper_ids.add(allocated)
        require(set(mapping) == set(range(native['public'])) and
                len(set(mapping.values())) == native['public'], 'injective full native public allocation')
        require(not (helper_ids & all_helpers) and min(helper_ids) >= main_count,
                'fresh helpers disjoint from other calls and all main fields')
        require(not (owned & set(mapping.values())), 'owned fields disjoint from every public input')
        all_helpers.update(helper_ids)
        invocations.append(dict(stage=stage, src=src, dst=dst,
                                helper_first=min(helper_ids), helper_last=max(helper_ids),
                                extra_helper=mapping[771]))
    require(all_helpers == set(range(main_count, public_count)), 'no unused or doubly credited helper')
    require(public_count == 13688, 'exact independent public field inventory')
    return dict(main_fields=main_count, helper_fields=len(all_helpers),
                helpers_per_call=len(helpers), public_fields=public_count,
                additional_helpers=18, owned_labels=len(owned),
                owned_first=min(owned), owned_last=max(owned),
                thin_query_scratch=public_count+native['owned_fields'],
                reserved_field_slots=public_count+native['owned_fields']+1,
                invocations=invocations)


def canonical_adapter_inventory(caller, native_word, phase_data):
    """Derive explicit complete-caller adapters from literal job axis sets.

    Each missing desired coordinate below rank r is paired with a desired
    coordinate outside 0,...,r-1. These disjoint two-coordinate swaps map the
    canonical set exactly onto the desired set. Both Gaussian boundaries pay
    for every swap. A q direction also pays for both fixed-nine-axis basis
    maps; a negative q exponent pays for the Q^2 translation.
    """
    dimension = caller['ambient_rank']
    require(dimension == 153, 'complete ambient dimension for canonical adapters')
    recipes = {recipe['q']: recipe for recipe in phase_data['recipes']}
    basis_checks = 0
    for q in native_word['ports']:
        basis = [q] + recipes[q]['idle_children'][0]['orthogonal_axes'][:8]
        require(len(basis) == 9 and all(0 < v < 512 for v in basis), 'nine-axis q basis')
        require(all((a & b).bit_count() % 2 == int(i == j)
                    for i,a in enumerate(basis) for j,b in enumerate(basis)),
                'orthonormal q basis and complement')
        # Independently form coordinates and reconstruct every nine-bit address.
        for address in range(512):
            coordinates = [(address & v).bit_count() % 2 for v in basis]
            rebuilt = 0
            for bit,vector in zip(coordinates,basis):
                if bit:
                    rebuilt ^= vector
            require(rebuilt == address, 'full q-basis address permutation and inverse')
            if address == q:
                require(coordinates == [1] + [0]*8, 'q becomes canonical coordinate zero')
            basis_checks += 1

    counts, profiles = Counter(), Counter()

    def coordinates(stages):
        require(len(stages) == len(set(stages)) and
                all(1 <= s <= caller['stages'] for s in stages), 'fresh adapter axes')
        return {coordinate for stage in stages
                for coordinate in range(9+8*(stage-1), 9+8*stage)}

    def job(kind, desired, central, negative, multiplicity):
        require(bool(desired) and max(desired) < dimension and
                min(desired) >= 0, 'nonempty canonical target axes')
        canonical = set(range(len(desired)))
        missing, outside = sorted(canonical-desired), sorted(desired-canonical)
        require(len(missing) == len(outside), 'equal axis-set differences')
        permutation = list(range(dimension))
        for a,b in zip(missing,outside):
            permutation[a],permutation[b] = permutation[b],permutation[a]
        require({permutation[i] for i in canonical} == desired and
                all(permutation[permutation[i]] == i for i in range(dimension)),
                'explicit two-axis-swap permutation and inverse')
        require(not central or (0 in desired and permutation[0] == 0),
                'q-basis change retains the central coordinate')
        require(central or not negative, 'q phase has a q direction')
        counts[kind+'_jobs'] += multiplicity
        counts[kind+'_axis_swaps'] += 2*len(missing)*multiplicity
        counts[kind+'_q_basis_maps'] += 2*int(central)*multiplicity
        counts[kind+'_phase_maps'] += int(negative)*multiplicity
        profiles[(kind,len(desired),len(missing),int(central),int(negative))] += multiplicity

    for event in caller['events']:
        if event[0] in ('IDLE','IDLE_ONE'):
            selected = event[3] if event[0] == 'IDLE' else event[2]
            job('idle',coordinates(selected),False,False,208 if event[0] == 'IDLE' else 104)
        elif event[0] == 'QUERY':
            require(event[3] in (-1,1), 'canonical thin-query orientation')
            job('query',{0},True,event[3] == -1,104)
    for term in caller['diagonal']:
        require(term[1] == 0 and term[0] in (-1,0,1), 'canonical main target format')
        selected = [stage+1 for stage,present in enumerate(term[2:]) if present]
        desired = coordinates(selected)
        if term[0]:
            desired.add(0)
        job('main',desired,bool(term[0]),term[0] == -1,104)
    total = sum(count for key,count in counts.items() if not key.endswith('_jobs'))
    require(total == 286728, 'complete literal elementary canonical-adapter census')
    return dict(ambient_axes=dimension,q_bases_checked=len(native_word['ports']),
                q_basis_address_checks=basis_checks,components=dict(sorted(counts.items())),
                elementary_maps=total,
                profiles=[dict(kind=k[0],rank=k[1],swaps_per_side=k[2],central=k[3],
                               negative=k[4],multiplicity=n) for k,n in sorted(profiles.items())],
                scope='Exact coordinate permutations, q-basis inverses and multiplicity count. The 1000-unit rate is retained for each fixed native whole-job map or each elementary map supported on at most 17 specified axes; it is not a rate for an arbitrary 153-axis map.')


def ordinary(caller, native, native_word, phase_data):
    total_work, total_height, maximum = 0, 0, Fraction(0)
    for event in caller['events']:
        operation = event[0]
        if operation in ('ADD', 'SCALE'):
            value = Fraction(event[-1])
            n, d = abs(value.numerator), value.denominator
            require(n and d & (d-1) == 0, 'nonzero dyadic caller scalar')
            require(n.bit_length() <= 8 and d.bit_length() <= 7, 'literal scalar bit envelope')
            if operation == 'ADD':
                work = 2*((n.bit_length()-1)+(n.bit_count()-1)+(d.bit_length()-1)+int(value < 0)+1)
            else:
                require(n & (n-1) == 0, 'dyadic-unit caller scale')
                work = 2*(abs(n.bit_length()-d.bit_length())+int(value < 0))
            height = (n+d).bit_length()+d.bit_length()
            maximum = max(maximum, abs(value))
        elif operation == 'LAMBDA':
            work, height = 16, 8
        elif operation == 'SWAP':
            work, height = 8, 4
        else:
            work, height = 0, 0
        require(work <= 32 and height <= 32, 'complete per-gate ordinary envelope')
        total_work += work
        total_height += height
    helper_normalizers = 2*sum(native['helpers'].values())
    main_adapters = 2*104
    contact_routes, lifetime_routes = 4*104, 4*native['lifetimes']
    routes = 1000*(sum(native['paid'].values())+helper_normalizers+main_adapters+
                   contact_routes+lifetime_routes)
    per_call = native['scalar']+routes
    require(per_call < 10**7, 'complete recounted native bound')
    caller_envelope = 32*caller['roles']*104*len(caller['events'])
    require(104*total_work <= caller_envelope and 104*total_height <= caller_envelope,
            'literal ordinary caller work and height')
    thin = 104*16*sum(event[0] == 'QUERY' for event in caller['events'])
    # The former 1000-per-main-output allowance omitted the explicit full-axis
    # whole-idle/query/main canonical adapters. Replace that flat term by the
    # complete elementary inventory; keep the 26 scalar units per output.
    output_scalars = 104*caller['roles']*26
    old_output_routes = 104*caller['roles']*1000
    adapters = canonical_adapter_inventory(caller,native_word,phase_data)
    adapter_units = 1000*adapters['elementary_maps']
    former_partial = 18*10**7+caller_envelope+thin+output_scalars+old_output_routes
    conservative = 18*10**7+caller_envelope+thin+output_scalars+adapter_units
    counted = 18*per_call+caller_envelope+thin+output_scalars+adapter_units
    require(conservative < 10**9 and counted <= conservative, 'complete ordinary budget')
    return dict(helper_normalizers_per_call=helper_normalizers,
                helper_normalizers_all_calls=18*helper_normalizers,
                main_adapters_per_call=main_adapters,
                contact_routes_per_call=contact_routes,
                lifetime_routes_per_call=lifetime_routes,
                local_scalar=native['scalar'], local_routes=routes, local_per_call=per_call,
                local_upper_per_call=10**7, caller_envelope=caller_envelope,
                caller_actual_work_per_port=total_work, caller_actual_height_per_port=total_height,
                caller_maximum_scalar=str(maximum), thin_query_work=thin,
                main_output_scalar_units=output_scalars,
                canonical_adapters=adapters,canonical_adapter_units=adapter_units,
                superseded_flat_main_output_routes=old_output_routes,
                former_partial_raw_upper=former_partial,
                full_adapter_correction=adapter_units-old_output_routes,
                raw_counted=counted,
                raw_upper=conservative, budget=10**9,
                route_rate_status='Retained physical/tape contract: 1000 per fixed native whole-job map or per <=17-axis elementary map; full 153-axis adapters are explicitly decomposed and charged.')


def diagnostic(target, paid, precision=110):
    with localcontext() as context:
        context.prec = precision
        signed = Counter(target)
        signed.subtract(paid)
        logs = {rank: Decimal(rank).ln() for rank in signed}

        def margin(kappa):
            return sum(Decimal(count)*((1-kappa)*logs[rank]).exp()
                       for rank, count in signed.items())

        left, right = Decimal('.0033'), Decimal('.0034')
        require(margin(left) > 0 > margin(right), 'Decimal diagnostic bracket')
        for _ in range(280):
            middle = (left+right)/2
            if margin(middle) > 0:
                left = middle
            else:
                right = middle
        root = (left+right)/2
        return dict(precision=precision, raw_root=str(root),
                    bracket=[str(left), str(right)],
                    claim=CLAIM, tested=TESTED,
                    margin_claim=str(margin(Decimal(CLAIM))),
                    margin_tested=str(margin(Decimal(TESTED))),
                    derivative_at_root=str(-sum(Decimal(count)*logs[rank]*
                         ((1-root)*logs[rank]).exp() for rank, count in signed.items())),
                    certification='High-precision Decimal diagnostic only; not an exact interval certificate.')


def claim_arithmetic(target, paid):
    claim, tested, lower = map(Fraction, (CLAIM, TESTED, CERTIFIED_RAW_LOWER))
    gap = (tested-claim)/7
    require(claim < tested < lower and gap == Fraction(1, 1400000000),
            'tightened claim remains strictly below certified lower crossing')
    reserve, decay, power = Fraction(1, 10**27), Fraction(31, 32), 1920
    finite_upper = 1/(1+power*reserve)+4*decay**power
    require(finite_upper < 1 and 11**64 < 12**63,
            'unchanged exact finite strictification and rank rounding')
    with localcontext() as context:
        context.prec = 110
        kappa = Decimal(TESTED)
        t = 1-kappa
        def moment(histogram, exponent):
            return sum(Decimal(n)*(exponent*Decimal(r).ln()).exp()
                       for r,n in histogram.items())
        tm, pm = moment(target,t), moment(paid,t)
        alpha = pm/tm
        gamma = moment(paid,t+Decimal(1)/7)/((Decimal(11).ln()/7).exp()*tm)
        delta = Decimal(12*sum(target.values()))/((kappa*Decimal(11).ln()).exp()*tm)
        require(alpha < 1-Decimal('1e-27') and gamma < Decimal(31)/32 and delta < Decimal(31)/32,
                'tightened tested price has diagnostic completion slack')
        eta = t/((Decimal(1920)*kappa*Decimal(145).ln()).exp())
        theta_power = (Decimal(63)/64)**2100
        require(eta > theta_power, 'diagnostic compiler complement capacity')
        return dict(claim=str(claim),tested=str(tested),certified_lower=str(lower),
                    lower_minus_tested=str(lower-tested),compiler_gap=str(gap),
                    strictification_reserve=str(reserve),strictification_power=power,
                    exact_finite_strictification=True,exact_rank_rounding=True,
                    alpha=str(alpha),one_minus_alpha=str(1-alpha),
                    reserve_slack_factor=str((1-alpha)/Decimal('1e-27')),
                    gamma=str(gamma),delta=str(delta),decay=str(Decimal(31)/32),
                    eta=str(eta),theta_power=str(theta_power),
                    certification='Parameter inequalities are exact rationals; moments are Decimal diagnostics. The raw lower endpoint is supplied by the primary exact interval certificate.')


def controls(caller, first, candidate, native_word, source_word):
    cases = []

    def reject(label, operation):
        try:
            operation()
        except ValueError as error:
            cases.append(dict(mutation=label, rejected=str(error)))
        else:
            raise ValueError('negative control accepted: ' + label)

    reject('price the intermediate one-retirement caller', lambda: invoice(first, candidate))
    omitted = deepcopy(caller)
    omitted['events'].pop(next(i for i,e in enumerate(omitted['events']) if e[0] == 'LOCAL'))
    reject('omit one full native call', lambda: invoice(omitted, candidate))
    wrong = deepcopy(caller)
    next(e for e in wrong['events'] if e[0] == 'QUERY')[-1] = 1
    reject('reverse one thin-query orientation', lambda: caller_columns(wrong))
    aliased = deepcopy(caller)
    event = next(e for e in aliased['events'] if e[0] == 'LOCAL')
    event[3] = event[2]
    reject('alias one native source and destination', lambda: allocation(aliased, native_word))
    reject('retain the old 563-helper allocation', lambda: allocation(caller, source_word))
    return cases


def run(caller_root, source_path, candidate_path, local_receipt):
    paths = {name: caller_root/name for name in ('CONTROLLER.json', 'CALLER-ONE-RETIRED.json',
             'CALLER-UNRETIRED.json', 'RETIREMENT-WITNESSES.json')}
    data = {name: json.loads(path.read_text()) for name, path in paths.items()}
    caller = data['CONTROLLER.json']
    retirements = rebuild_retirements(data['CALLER-UNRETIRED.json'], data['RETIREMENT-WITNESSES.json'],
                                     data['CALLER-ONE-RETIRED.json'], caller)
    symbolic = caller_columns(caller)
    candidate_word = word(candidate_path)
    source_word = word(source_path)
    source, candidate = chronology(source_word), chronology(candidate_word)
    # Full local all-column audit was independently executed in check_native.py.
    for name, path, counted in [('base', source_path, source), ('candidate', candidate_path, candidate)]:
        key = 'source_sha256' if name == 'base' else 'candidate_sha256'
        require(sha256(path.read_bytes()).hexdigest() == local_receipt[key], 'independent local receipt binding')
        for field in ('public', 'owned', 'events', 'scalar', 'peak', 'lifetimes'):
            require(counted[field] == local_receipt[name][field], 'local recount: ' + field)
        for field in ('paid', 'helpers'):
            require(counted[field] == {int(k): v for k,v in local_receipt[name][field].items()},
                    'local histogram recount: ' + field)
    old_target, old_paid, _, _, _ = invoice(caller, source)
    target, paid, main, idle, counts = invoice(caller, candidate)
    target_delta, paid_delta = Counter(target), Counter(paid)
    target_delta.subtract(old_target)
    paid_delta.subtract(old_paid)
    target_delta = {r: v for r,v in target_delta.items() if v}
    paid_delta = {r: v for r,v in paid_delta.items() if v}
    require(target_delta == {4:18, 5:18, 9:-18} and paid_delta == {1:18, 5:18, 6:-18},
            'entire eighteen-call target and paid deltas')
    require(sum(target.values()) == 13688 and sum(paid.values()) == 66870, 'complete global census')
    target_mass, paid_mass = (sum(r*n for r,n in histogram.items()) for histogram in (target, paid))
    require(target_mass-paid_mass == 760 and paid_mass == 178080, 'complete rank masses')
    fields = allocation(caller, candidate_word)
    phase_path = caller_root.parent/'runtime/DATA-PHASES.json'
    work = ordinary(caller, candidate, candidate_word, json.loads(phase_path.read_text()))
    original = json.loads((caller_root/'RESULT.json').read_text())['candidate']['complete_cost']
    require(old_target == {int(k):v for k,v in original['targets'].items()} and
            old_paid == {int(k):v for k,v in original['paid'].items()}, 'retained invoice reproduced from literals')
    old_root = diagnostic(old_target, old_paid)
    new_root = diagnostic(target, paid)
    with localcontext() as context:
        context.prec = 100
        gain = str(Decimal(new_root['raw_root'])-Decimal(old_root['raw_root']))
    return dict(status='PASS_INDEPENDENT_COMPLETE_CALLER_INVOICE',
                inputs={**{name:sha256(path.read_bytes()).hexdigest() for name,path in paths.items()},
                        'DATA-PHASES.json':sha256(phase_path.read_bytes()).hexdigest()},
                source_sha256=sha256(source_path.read_bytes()).hexdigest(),
                candidate_sha256=sha256(candidate_path.read_bytes()).hexdigest(),
                correct_final_literal='CONTROLLER.json', retirement_reconstruction=retirements,
                caller_all_columns=symbolic, counts=dict(counts), main_targets=dict(sorted(main.items())),
                whole_idle_paid=dict(sorted(idle.items())), targets=dict(sorted(target.items())),
                paid=dict(sorted(paid.items())), target_count=sum(target.values()), paid_count=sum(paid.values()),
                target_rank_mass=target_mass, paid_rank_mass=paid_mass, surplus=target_mass-paid_mass,
                target_delta=target_delta, paid_delta=paid_delta, fields=fields, ordinary=work,
                old_diagnostic=old_root, new_diagnostic=new_root, raw_root_gain=gain,
                final_claim_arithmetic=claim_arithmetic(target, paid),
                controls=controls(caller, data['CALLER-ONE-RETIRED.json'], candidate,
                                  candidate_word, source_word),
                limitations=['Native absolute phases and physical routes require the primary native verifier.',
                             '1000-unit route rate, owned erasure and other inherited framework assumptions remain.',
                             'No completion/compiler/outer admission is inferred from the Decimal root diagnostic.'])
