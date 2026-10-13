"""Mixed complete-call finite invoice. Adapted from PR531/535 and prior five-copy invoice.
Original attribution: prepared for icekylinx with OpenAI Codex assistance, Apache-2.0.
Recounts actual source-bound local programs independently; all scalar, owner, storage and prefix charges retained.
"""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contenthash(path):
    data = path.read_bytes()
    return hashlib.sha256(gzip.decompress(data) if path.suffix == '.gz' else data).hexdigest()


def audit_local(local_dir,m):
    cp=local_dir/'CANONICAL-WORD.json.gz';pp=local_dir/'LOCAL-PROGRAMS.json.gz';rp=local_dir/'INDEPENDENT-LOCAL-REPLAY.json'
    w,programs,replay=read(cp),read(pp),read(rp);checks=read(local_dir/'LOCAL-CHECKS.json')
    assert set(programs)=={'forward','backward'}
    assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert replay['canonical_word_sha256']==filehash(cp) and replay['local_programs_sha256']==filehash(pp)
    v,helpers,h=w['v'],w['R'],w['h'];assert(v,helpers,h,m)==(112,504,9,73)
    assert replay['v']==v and replay['helpers']==helpers
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


    return dict(local=local,widths=widths,entering=entering,centres=centres,helpers=helpers,adapters=adapters,compiler=compiler,primitive_bound=primitive_bound,
      binding=dict(canonical_word_sha256=filehash(cp),local_programs_sha256=filehash(pp),local_checks_sha256=filehash(local_dir/'LOCAL-CHECKS.json'),independent_local_replay_sha256=filehash(rp)))

def run(base,hosted,audit,out,providers,retained_invoice=None):
    local_dir=base/'split-centres';parent=read(local_dir/'GLOBAL-TEMPLATE.json.gz');template_path=hosted/'GLOBAL-TEMPLATE.json.gz';template=read(template_path)
    owners=read(audit/'OWNERS-AND-PROFILE.json');control=read(audit/'ASYNC-AUDIT.json');template_hash=contenthash(template_path)
    assert template_hash==control['complex_template_sha256']==owners['template_sha256']
    assert owners['status']=='PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE'
    locations=read(providers);records={k:audit_local(Path(v),73)for k,v in locations.items()}
    assert set(records)==set(c['provider']for c in template['calls'])
    for k,z in records.items():
        for field,value in z['binding'].items():assert template['provider_registry'][k][field]==value,(k,field)
    assert template['recipe']==parent['recipe']
    assert Counter((c['orientation'],c['stage'],c['replica'])for c in template['calls'])==Counter((c['orientation'],c['stage'],c['replica'])for c in parent['calls'])
    v,helpers,h,m,n=112,504,9,73,728;centres=8;stages=9;blocks_per_stream=4
    replicas=1+max(c['replica']for c in template['calls']);assert replicas%8==0;clones=replicas//8
    call_count=len(template['calls']);assert call_count==stages*replicas==control['complete_invocations'];assert control['one_owner_per_complete_invocation']
    payload=512 if clones==1 else 1024
    compiler=64*(m+1)**3;adapters=max(z['adapters']for z in records.values());primitive_bound=max(z['primitive_bound']for z in records.values())
    assert all(z['helpers']==helpers and z['centres']==centres and z['compiler']==compiler for z in records.values())
    entering=max(z['entering']for z in records.values())
    local={k+':'+o:row for k,z in records.items()for o,row in z['local'].items()}
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
    scalar = sum(records[call['provider']]['local'][call['orientation']]['real_component_primitives'] for call in template['calls'])
    factors_per_wrapper = 2*(m-1)
    wrapper_factors = 2*call_count*entering*factors_per_wrapper
    nonlocal_items = (
        4*v*replicas*stages + 2*v*replicas*stages
        + 2*call_count*helpers
        + sum(child['replicas'] for child in parent['idle_children'])
        + stages*parent_banks + bridge_additions + shifts + moves
        + parent_live + parent_physical + wrapper_factors)
    outside = 8*nonlocal_items+64*m+128*call_count*len(records) # Explicit registry selection/table dispatch charge.
    parent_pervertex = (
        scalar+bridge_additions+shifts+moves+parent_live
        +(call_count*adapters+outside)*compiler+64*parent_physical)

    live, physical = template['live'], template['physical']
    mass, profile = owners['rank_mass'], owners['paid_profile']
    assert m*live-mass == owners['deficit'] == 2560*clones
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
        assert previous['charged_prefix_bits'] <= payload
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

    receipt=dict(status='PASS_INDEPENDENT_MIXED_SCALAR_PREFIX_AND_FINITE_INVOICE',template_sha256=template_hash,parent_template_sha256=contenthash(local_dir/'GLOBAL-TEMPLATE.json.gz'),
      owner_audit_sha256=filehash(audit/'OWNERS-AND-PROFILE.json'),controller_audit_sha256=filehash(audit/'ASYNC-AUDIT.json'),
      provider_bindings={k:z['binding']for k,z in records.items()},provider_counts=dict(Counter(c['provider']for c in template['calls'])),
      global_prefix_bits=required_prefix,charged_prefix_bits=payload,complete_invocation_sweeps=call_count,bridge_sweeps=bridge_sweeps,row_prefix_extra=2*payload,
      local=local,helpers=helpers,centres=centres,live=live,physical=physical,physical_stock_identity=dict(data_and_owner_families=live,local_helpers=helpers,private_centres=centres,coefficient_work=2),
      provider_widths={k:dict(sorted(Counter(z['widths']).items()))for k,z in records.items()},local_adapters=adapters,local_primitive_bound=primitive_bound,
      wrapper_elementary_factors_charged=wrapper_factors,factors_per_wrapper=factors_per_wrapper,compiler=compiler,unhosted_pervertex=parent_pervertex,hosted_rebased_pervertex=rebased,
      conservative_pervertex_used=used,retained_prior_overcharge=retained,registry_dispatch_charge=128*call_count*len(records),
      finite=dict(physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),physical_row_coefficient=row,retained_row_coefficient=20161,
        required_C0_bits=(32*m*total_mass*total_mass).bit_length(),halving_integer_inequality=[m*m,2*maxchild*maxchild],G_exponent=30000,E_exponent=100000,C0_exponent=210000),strict_checks=inequalities,
      scope='Fresh independent recount of every selected local supplier, full calls/bridges, maximum adapters and explicit finite registry dispatch. All-size compiler, precision/tape and analytic interfaces remain conditional.')
    prefix=dict(status='PASS_MIXED_GLOBAL_PREFIX',template_sha256=template_hash,global_prefix_bits=required_prefix,retained_payload_bits=payload,
      proof='Use maximum freshly recounted local prefix, pay every complete call and bridge sweep, input conversion and arithmetic margin. No unproved block-norm saving is used.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'PREFIX-AND-INVOICE.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'GLOBAL-PREFIX.json').write_text(json.dumps(prefix,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--hosted',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--providers',type=Path,required=True);p.add_argument('--retained-invoice',type=Path);a=p.parse_args()
    run(a.base,a.hosted,a.audit,a.out,a.providers,a.retained_invoice)

