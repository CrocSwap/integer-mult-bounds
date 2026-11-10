"""Reconstruct the signed caller invoice and run both retained price engines."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import gzip
import json
import sys

from physical_child import ROLES, WORD


def module(name, path, replacements=()):
    source = path.read_text()
    for old, new in replacements:
        assert source.count(old) == 1, (path, old)
        source = source.replace(old, new)
    obj = ModuleType(name)
    obj.__file__ = str(path)
    sys.modules[name] = obj
    exec(compile(source, str(path), 'exec'), obj.__dict__)
    return obj


def independent(vendor):
    return module('rank9_independent', vendor/'independent.py', (
        ("elif event[1]=='IDLE_ONE':degree.update(event[3])",
         "elif event[1] in ('IDLE_ONE','IDLE_ODD'):degree.update(event[3])"),
        ("elif op=='IDLE_ONE':rows[r]=pscale(rows[r],m=sum(1<<(8*(s-1)) for s in e[3]))",
         "elif op in ('IDLE_ONE','IDLE_ODD'):rows[r]=pscale(rows[r],q=e[4] if op=='IDLE_ODD' else 0,m=sum(1<<(8*(s-1)) for s in e[3]))"),
        ("elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports",
         "elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports\n   elif e[1]=='IDLE_ODD':P[1+8*len(e[3])]+=ports"),
        ("queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)",
         "queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\n  fusedroute=sum(21000*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])"),
        ("idle_routes=idleroute,query_routes=queryroute)",
         "idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)"),
    ))


def precision(vendor, word, caller, gate, manifest):
    for item in manifest['files']:
        if item['path'].startswith('retained/'):
            assert sha256((vendor/item['path']).read_bytes()).hexdigest() == item['sha256']
    grid = module('rank9_grid', vendor/'retained/odd-native-common-grid/independent_bounds.py', (
        ('elif op != "IDLE_ONE":', 'elif op not in ("IDLE_ONE", "IDLE_ODD"):'),
    ))
    binding = module('source_binding', vendor/'retained/query-only-precision-envelope/source_binding.py')
    env_path = vendor/'retained/query-only-precision-envelope/envelopes.py'
    src = env_path.read_text()
    old = 'elif op in ("LAMBDA", "IDLE_ONE"):'
    assert src.count(old) == 2
    # Each fused operation is one whole-field unitary request with one child defect.
    env = ModuleType('rank9_envelope')
    env.__file__ = str(env_path)
    sys.modules[env.__name__] = env
    src = src.replace(old, 'elif op in ("LAMBDA", "IDLE_ONE", "IDLE_ODD"):')
    src = src.replace('word["public"] - len(mains) == 1061', 'word["public"] - len(mains) == 1080')
    src = src.replace('fresh_arbitrary_helpers=18 * 1061', 'fresh_arbitrary_helpers=18 * 1080')
    exec(compile(src, str(env_path), 'exec'), env.__dict__)
    wg, cg = grid.word_run(word), grid.caller_run(caller)
    wp, wr = env.native_envelope(word)
    cp, cr = env.caller_envelope(caller, wp, word)
    height = max(cg['denominator_height'], cg['pre_joint_height'] + wg['dyadic_height'])
    mass = max(binding.strict_power(Q(cg['maximum_mass'])), binding.strict_power(Q(cg['pre_joint_mass'])) +
               binding.strict_power(Q(wg['maximum_scaled_mass'])))
    H, lp, step = int(gate['H']), gate['written_log_power'], Q(gate['compiler_gap']).denominator
    kstar = 1920 * 153**1920 * (H+1)**2
    assert (H+1)**lp < 2**(H//step) and (H-step+1)**lp >= 2**(H//step-1)
    assert (4096*kstar).bit_length() < H
    assert max(2*max(height,mass), *(x['strict_power_of_two'] for x in cr['bounds'].values())) < H
    return dict(word=wg, caller=cg, context_height=height, context_mass_bits=mass, context_c=2*max(height,mass),
                rounded_native=wr, rounded_caller=cr, Kstar_bits=kstar.bit_length(),
                scope='Exact-child grid and attributed all-fibre error envelope, with one signed unitary per fused event')


def main(replay, word, candidate, physical):
    vendor = replay/'research/shared-wire-split-composition'
    base = json.loads((replay/'research/coupled-helper-rechart/RESULT.json').read_text())
    old = json.loads((vendor/'data/caller.json').read_text())
    new = json.loads(candidate.read_text())
    raw = gzip.decompress(word.read_bytes())
    assert sha256(raw).hexdigest() == WORD
    native_word = json.loads(raw)
    old_actions = [e for e in old['events'] if e[0] in ('J','A')]
    assert [e for e in new['events'] if e[0] in ('J','A')] == old_actions
    assert new['types'] == old['types']
    fused = [e for e in new['events'] if e[:2] == ['B','IDLE_ODD']]
    assert len(fused) == 4 and {e[2]:e[3][0] for e in fused} == ROLES
    assert all(e[4] == -1 and len(e[3]) == 1 for e in fused)
    p = json.loads(physical.read_text())
    assert p['status'] == 'PASS_PHYSICAL_RANK9_ALGEBRA'
    assert p['word_sha'] == WORD and p['proposed_sha'] == sha256(candidate.read_bytes()).hexdigest()
    assert p['paid_calls'] == 32
    assert all(row['logical_child_rank'] == 9 and row['ordinary_route_units'] == 19 for row in p['bindings'])
    peer = module('rank9_peer', replay/'research/peer-move-retiming/verify.py')
    previous = module('rank9_previous', replay/'research/shared-wire-stop-fusion/verify.py')
    check = independent(vendor)
    audited = check.caller(new)
    assert not audited['bad_outputs']
    n = base['native']
    n['paid'] = {int(k): v for k,v in n['paid'].items()}
    n['helpers'] = {int(k): v for k,v in n['helpers'].items()}
    before, after = check.invoices(native_word, old, n), check.invoices(native_word, new, n)
    for key in ('T','P'):
        assert {str(r):v for r,v in before[key].items()} == base['invoice'][key]
    delta = Counter(after['P']); delta.subtract(before['P'])
    assert {r:v for r,v in delta.items() if v} == {1:-32,8:-32,9:32}
    assert before['T'] == after['T'] and before['S'] == after['S'] == 1520
    assert after['empty_root_credits'] == before['empty_root_credits'] == 0
    ordinary = check.ordinary(native_word,new,n)
    routes = 1000 * sum(len(row['caller_fields']) * row['ordinary_elementary_units'] for row in p['bindings'])
    assert routes == 1168000
    route_delta = routes - ordinary['caller_items']['B']['fused_routes']
    ordinary['caller_items']['B']['fused_routes'] = routes
    for name in ('caller_total','raw_upper','conservative_total'):
        ordinary[name] += route_delta
    scalar_surcharge = 0
    for e in new['events']:
        if e[0] == 'B' and e[1] in ('ADD','SCALE'):
            q = Q(e[4] if e[1] == 'ADD' else e[3])
            a, d = abs(q.numerator), q.denominator
            scalar_surcharge += 4 * (a.bit_length() + d.bit_length() + 1 +
                                     (a.bit_count() if e[1] == 'ADD' else 0))
    ordinary['extra_B_scalar_surcharge'] = len(new['types']['B']['ports']) * scalar_surcharge
    ordinary['conservative_total'] += ordinary['extra_B_scalar_surcharge']
    ordinary['margin_to_billion'] = 10**9 - ordinary['conservative_total']
    assert ordinary['conservative_total'] == 847191616 and ordinary['margin_to_billion'] > 0
    _, _, price = peer.price_audit(previous, before, after, base['gate'])
    engine = module('rank9_directed_price', vendor/'interval_gate.py')
    claim = Q('.003635202569271')
    tested = claim + Q(7,10**17)
    low, high = map(Q, price['crossing_intervals']['candidate'])
    old_low, old_high = map(Q, price['crossing_intervals']['baseline'])
    old_claim = Q(base['gate']['claim'])
    assert old_low < old_high < claim < tested < low < high
    gate = engine.gate(after, claim, tested, low, high, base['gate']['BIT_pin'])
    assert engine.sub(engine.moment(before['T'],claim), engine.moment(before['P'],claim))[1] < 0
    gain = dict(claim_gain=str(claim-old_claim), claim_vs_old_raw_upper=str(claim-old_high),
                raw_gain_interval=[str(low-old_high),str(high-old_low)])
    price.update(claim_decimal='0.003635202569271',gain_decimal='0.000000875329271')
    manifest = json.loads((vendor/'INDEPENDENT-SOURCES.json').read_text())
    limits = precision(vendor, native_word, new, gate, manifest)
    print(json.dumps(dict(status='PASS_RANK9_CONDITIONAL_GATES', word_sha=WORD,
                          caller_sha=p['proposed_sha'], caller=audited, invoice=after, ordinary=ordinary,
                          gate=gate,gain=gain,independent_price=price,precision=limits),sort_keys=True))


if __name__ == '__main__':
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    for name in ('replay','word','candidate','physical'):
        parser.add_argument(name,type=Path)
    main(**vars(parser.parse_args()))
