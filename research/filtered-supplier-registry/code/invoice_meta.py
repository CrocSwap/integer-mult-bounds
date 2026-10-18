"""Recount a changed local word and its actual asynchronous finite invoice.

Prepared for icekylinx with OpenAI Codex assistance. Apache-2.0.
Adapted from the attributed Round19 audit_async_invoice.py and its PR484/514
ancestry. Uses the fresh hash-bound independent local replay for exact scalar
endpoints; independently recounts emitted Horner work, prefix envelopes,
paid local calls, wrappers and finite charges. Does not rerun the old baseline
or read an old INTEGRATION.json as evidence for the changed word.
"""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import meta_registry


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contenthash(path):
    data = path.read_bytes()
    return hashlib.sha256(gzip.decompress(data) if path.suffix == '.gz' else data).hexdigest()


def recount_variant(z, m):
    w,programs,replay,checks = z['canon'],z['programs'],z['replay'],z['checks']
    v,helpers,h = w['v'],w['R'],w['h']
    n=2*v+helpers
    widths = [h-len(w['frames'][f]) for f in w['start'][2*v:]]
    assert len(widths) == helpers
    entrances = {r: f for r, f in enumerate(w['start']) if r >= 2*v and f != 0}
    entering = len(entrances)
    assert entering == replay['entering_helpers']
    local = {}
    for orientation, events in programs.items():
        # Endpoint equality and native frames were already independently
        # replayed on all n columns in the hash-bound receipt above.
        env = {('L', r): Q(1) for r in range(n)}
        peak = Q(1)
        real = macros = workops = 0
        paid = Counter()
        wrappers = {'pre': set(), 'post': set()}
        for event in events:
            tag = event[0]
            if tag == 'climb':
                paid[event[5]] += 1
            elif tag == 'center':
                paid[event[4]] += 1
            elif tag == 'residual_adapter':
                _, kind, register, frame = event
                assert kind in wrappers and entrances.get(register) == frame
                assert register not in wrappers[kind]
                wrappers[kind].add(register)
            elif tag == 'scalar':
                macros += 1
                scalar = event[1]
                op, target = scalar[0], tuple(scalar[1])
                if op == 'clear':
                    env[target] = Q(0)
                    count = 1
                elif op == 'copy':
                    env[target] = env[tuple(scalar[2])]
                    count = 1
                elif op == 'scale':
                    q = Q(scalar[2], scalar[3])
                    numerator, denominator = abs(q.numerator), q.denominator
                    assert numerator and numerator & (numerator-1) == 0
                    assert denominator & (denominator-1) == 0
                    env[target] *= abs(q)
                    count = abs(numerator.bit_length()-denominator.bit_length()) + int(q < 0)
                elif op == 'add':
                    source = tuple(scalar[2])
                    q = Q(scalar[3], scalar[4])
                    numerator, denominator = abs(q.numerator), q.denominator
                    assert source != target and numerator > 0
                    assert denominator & (denominator-1) == 0
                    acc, count = 0, 1  # clear coefficient work
                    for i, bit in enumerate(bin(numerator)[2:]):
                        if i:
                            acc *= 2
                            count += 1
                            peak = max(peak, acc*env[source])
                        if bit == '1':
                            acc += 1
                            count += 1
                            peak = max(peak, acc*env[source])
                    value = Q(acc)
                    for _ in range(denominator.bit_length()-1):
                        value /= 2
                        count += 1
                        peak = max(peak, value*env[source])
                    assert value == abs(q)
                    count += 2  # signed accumulation and work clear
                    env[target] = env.get(target, Q(0)) + abs(q)*env[source]
                    workops += count
                else:
                    raise AssertionError(op)
                real += 2*count
                peak = max(peak, env[target])
            else:
                assert tag in ('adapter', 'phase')
        assert wrappers['pre'] == wrappers['post'] == set(entrances)
        assert all(value == 0 for register, value in env.items() if register[0] == 'C')
        prior = replay['local'][orientation]
        assert prior['all_exact_columns'] == n and prior['private_work_erased']
        assert peak == Q(prior['prefix_l1_upper']) and peak < 2**prior['charged_payload_bits']
        bits = peak.numerator.bit_length()-peak.denominator.bit_length()+1
        assert bits == prior['prefix_bits_upper']
        assert real == checks[orientation]['real_component_primitive_bound']
        assert macros == checks[orientation]['scalar_macros']
        assert dict(paid) == {int(r): count for r, count in checks[orientation]['paid_profile'].items()}
        assert dict(paid) == {int(r): count for r, count in replay['paid_profiles'][orientation].items()}
        local[orientation] = dict(
            events=len(events), macros=macros, real_component_primitives=real,
            prefix_l1=str(peak), prefix_bits=bits,
            coefficient_work_primitive_count=workops, all_exact_columns=n,
            dirty_helper_columns=helpers, all_dirty_helper_columns_restored=True,
            private_centres_and_coefficient_work_cleared=True,
            pre_wrappers=len(wrappers['pre']), post_wrappers=len(wrappers['post']),
            endpoint_evidence='Hash-bound fresh INDEPENDENT-LOCAL-REPLAY.json')

    centres = len(w['centers'])
    children = sum(checks['forward']['paid_profile'].values())
    assert checks['forward']['paid_profile'] == checks['backward']['paid_profile']
    macro_bound = max(row['macros'] for row in local.values())
    compiler = 64*(m+1)**3
    adapters = 16*(macro_bound+children+n+centres)+64*m
    primitive_bound = max(row['real_component_primitives'] for row in local.values())+adapters*compiler

    return dict(local=local,widths=widths,entering=entering,centres=centres,
                adapters=adapters,primitive_bound=primitive_bound)

def run(base, hosted, audit, out, registry_path, retained_invoice=None):
    spec,registry=meta_registry.load(registry_path)
    local_dir = base / 'split-centres'
    cp = local_dir / 'CANONICAL-WORD.json.gz'
    pp = local_dir / 'LOCAL-PROGRAMS.json.gz'
    rp = local_dir / 'INDEPENDENT-LOCAL-REPLAY.json'
    w, programs, replay = read(cp), read(pp), read(rp)
    checks = read(local_dir / 'LOCAL-CHECKS.json')
    parent = read(local_dir / 'GLOBAL-TEMPLATE.json.gz')
    template_path = hosted / 'GLOBAL-TEMPLATE.json.gz'
    template = read(template_path)
    owners = read(audit / 'OWNERS-AND-PROFILE.json')
    control = read(audit / 'ASYNC-AUDIT.json')
    template_hash = contenthash(template_path)
    assert template_hash == control['complex_template_sha256'] == owners['template_sha256']
    assert owners['status'] == 'PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE'
    assert replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert replay['canonical_word_sha256'] == filehash(cp)
    assert replay['local_programs_sha256'] == filehash(pp)
    assert template['local_programs'] == {name:z['programs']for name,z in registry.items()}
    assert template['supplier_registry']=={'selection':spec['selection'],'bindings':meta_registry.bindings(registry_path,registry)}
    for tm,call in enumerate(template['calls']):
        assert call['time']==tm and call['supplier']==spec['selection'][tm]
        assert call['local_program_sha256']==registry[call['supplier']]['checks'][call['orientation']]['sha256']
    assert template['recipe'] == parent['recipe']
    assert Counter(c['orientation'] for c in template['calls']) == Counter(c['orientation'] for c in parent['calls'])

    v, helpers, h, m = w['v'], w['R'], w['h'], template['m']
    assert v == 112 and h == 9 and m == 73
    assert replay['v'] == v and replay['helpers'] == helpers
    n = 2*v + helpers
    stages, replicas, blocks_per_stream = 9, 8, 4
    call_count = len(template['calls'])
    assert call_count == stages*replicas == control['complete_invocations']
    assert control['one_owner_per_complete_invocation']
    payload = 512

    counts={name:recount_variant(z,m)for name,z in registry.items()}
    local={name+'_'+o:row for name,z in counts.items()for o,row in z['local'].items()}
    widths=counts[spec['selection'][0]]['widths']
    entering=max(z['entering']for z in counts.values())
    centres=len(w['centers'])
    compiler=64*(m+1)**3
    adapters=max(z['adapters']for z in counts.values())
    primitive_bound=max(z['primitive_bound']for z in counts.values())

    bridge_steps = sum(event['kind'] == 'bridge' for event in parent['recipe'])
    bridge_sweeps = sum(event['kind'] == 'bridge' for event in template['execution_schedule'])
    assert bridge_sweeps == replicas*bridge_steps
    bridge_additions = 2*v*bridge_sweeps
    shifts = blocks_per_stream*v*replicas
    moves = 2*shifts
    parent_live, parent_physical = parent['live'], parent['physical']
    data_stock = 2*v*blocks_per_stream*replicas
    assert (parent_live-data_stock) % stages == 0
    parent_banks = (parent_live-data_stock)//stages
    assert parent_banks >= 0
    assert parent_physical == parent_live+helpers+centres+2
    scalar = sum(counts[call['supplier']]['local'][call['orientation']]['real_component_primitives'] for call in template['calls'])
    factors_per_wrapper = 2*(m-1)
    wrapper_factors = 2*sum(counts[call['supplier']]['entering']for call in template['calls'])*factors_per_wrapper
    nonlocal_items = (
        4*v*replicas*stages + 2*v*replicas*stages
        + 2*call_count*helpers
        + sum(child['replicas'] for child in parent['idle_children'])
        + stages*parent_banks + bridge_additions + shifts + moves
        + parent_live + parent_physical + wrapper_factors)
    outside = 8*nonlocal_items+64*m
    parent_pervertex = (
        scalar+bridge_additions+shifts+moves+parent_live
        +(call_count*adapters+outside)*compiler+64*parent_physical)

    live, physical = template['live'], template['physical']
    mass, profile = owners['rank_mass'], owners['paid_profile']
    assert m*live-mass == owners['deficit'] == 2560
    assert mass == sum(int(r)*count for r, count in profile.items())
    assert physical == live+helpers+centres+2
    assert live == owners['live'] and physical == owners['physical']
    assert live <= parent_live and physical <= parent_physical
    assert not template['bank_padding']['families']
    assert owners['explicit_idle_remainder_children'] <= owners['source_idle_children_charged']
    rebased = parent_pervertex+65*(physical-parent_physical)+(live-parent_live)
    used = max(rebased, parent_pervertex)
    retained = None
    if retained_invoice is not None:
        previous = read(retained_invoice)
        assert previous['compiler'] == compiler
        assert previous['charged_prefix_bits'] == payload
        previous_bound = previous['conservative_pervertex_used']
        # The entire newly reconstructed charge is added to the retained old
        # allowance. This is intentionally stronger than only paying positive
        # deltas and makes no claim that the old integration certifies this word.
        used = max(used, previous_bound+parent_pervertex)
        retained = dict(sha256=filehash(retained_invoice),
                        previous_pervertex_allowance=previous_bound,
                        added_complete_new_pervertex=parent_pervertex,
                        policy='Retain old allowance and add the entire fresh recount.')

    half = m//2
    group = 2**(half*half)
    for i in range(1, half+1):
        group *= 2**(2*i)-1
    stock, streamed_mass = group*physical, group*mass
    logical = group*used+64
    router = compiler*(logical+1)*(stock+1)**2
    g_bound, e_bound, c0 = 2**30000, 2**100000, 2**210000
    total_mass = streamed_mass+e_bound
    literal = 2*g_bound*stock**2+8*streamed_mass+4*stock+4+32*m
    row = 2*stock.bit_length()+9909+252+2*payload
    maxchild = max(map(int, profile))
    inequalities = dict(
        local_primitive_bound=primitive_bound < 2**48,
        logical=logical < 2**6050, router=router < g_bound,
        literal=literal < e_bound, mass=total_mass < 2**100001,
        precision=32*m*total_mass*total_mass < c0,
        tape=2*total_mass+18 < c0, row=row < 20161,
        halving=m*m > 2*maxchild*maxchild)
    assert all(inequalities.values())
    localbits = max(row['prefix_bits'] for row in local.values())
    input_l2_bits = (m+1)//2
    required_prefix = localbits+input_l2_bits+call_count+bridge_sweeps+4
    assert required_prefix < payload

    receipt = dict(
        supplier_registry=template['supplier_registry'],
        provider_call_counts=dict(Counter(c['supplier']for c in template['calls'])),
        provider_width_inventories={name:dict(Counter(z['widths']))for name,z in counts.items()},
        status='PASS_INDEPENDENT_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE',
        template_sha256=template_hash,
        parent_template_sha256=contenthash(local_dir/'GLOBAL-TEMPLATE.json.gz'),
        owner_audit_sha256=filehash(audit/'OWNERS-AND-PROFILE.json'),
        controller_audit_sha256=filehash(audit/'ASYNC-AUDIT.json'),
        independent_local_replay_sha256=filehash(rp),
        canonical_word_sha256=filehash(cp), local_programs_sha256=filehash(pp),
        local_checks_sha256=filehash(local_dir/'LOCAL-CHECKS.json'),
        global_prefix_bits=required_prefix, charged_prefix_bits=payload,
        complete_invocation_sweeps=call_count, bridge_sweeps=bridge_sweeps,
        row_prefix_extra=2*payload, local=local, helpers=helpers,
        centres=centres, live=live, physical=physical,
        physical_stock_identity=dict(data_and_owner_families=live,
                                     local_helpers=helpers, private_centres=centres,
                                     coefficient_work=2),
        entering_helpers=entering, entrance_rank=sum(h-width for width in widths),
        width_inventory=dict(sorted(Counter(widths).items())),
        local_adapters=adapters, local_primitive_bound=primitive_bound,
        wrapper_elementary_factors_charged=wrapper_factors,
        factors_per_wrapper=factors_per_wrapper, compiler=compiler,
        unhosted_pervertex=parent_pervertex, hosted_rebased_pervertex=rebased,
        conservative_pervertex_used=used, retained_prior_overcharge=retained,
        finite=dict(physical_stock_bits=stock.bit_length(), router_bits=router.bit_length(),
                    literal_bits=literal.bit_length(), physical_row_coefficient=row,
                    retained_row_coefficient=20161,
                    required_C0_bits=(32*m*total_mass*total_mass).bit_length(),
                    halving_integer_inequality=[m*m, 2*maxchild*maxchild],
                    G_exponent=30000, E_exponent=100000, C0_exponent=210000),
        strict_checks=inequalities,
        scope='Fresh emitted primitive/Horner, prefix, wrapper and finite recount, using the hash-bound independent local all-column/frame replay and actual whole-owner audit. No old INTEGRATION receipt is used to certify the changed word. The inherited all-size compiler, precision/tape and analytic-transfer contracts remain conditional. Retained payload 512 and physical row allowance 20161 are unchanged.')
    prefix = dict(
        status='PASS_ASYNC_GLOBAL_PREFIX', template_sha256=template_hash,
        global_prefix_bits=required_prefix, retained_payload_bits=payload,
        complete_invocation_cover_sweeps=call_count,
        bridge_factor_two_sweeps=bridge_sweeps,
        local_scalar_coefficient_work_prefix_bits=localbits,
        stream_input_sup_to_l2_bits=input_l2_bits,
        primitive_arithmetic_margin_bits=4,
        controller_audit_sha256=filehash(audit/'ASYNC-AUDIT.json'),
        independent_local_replay_sha256=filehash(rp),
        proof=f'Each complete normalized invocation has unitary helper endpoints and a data shear with at most two unitary summands. Actual full orthogonal owner charts act by right-translation bijections on the retained cover group. Count all {call_count} complete local sweeps and {bridge_sweeps} individual bridge sweeps. Unit-modulus phases, idle children, terminal translations and normalized spectator endpoints are unitary. The independently recounted scalar/Horner envelope uses {localbits} bits; input sup-to-L2 uses {input_l2_bits}; arithmetic margin is 4. Total {required_prefix} < {payload}. All-size child/compiler and precision/tape interfaces remain inherited.')
    out.mkdir(parents=True, exist_ok=True)
    (out/'PREFIX-AND-INVOICE.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (out/'GLOBAL-PREFIX.json').write_text(json.dumps(prefix, indent=2)+'\n')
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--hosted', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--retained-invoice', type=Path)
    args = parser.parse_args()
    run(args.base, args.hosted, args.audit, args.out, args.registry, args.retained_invoice)
