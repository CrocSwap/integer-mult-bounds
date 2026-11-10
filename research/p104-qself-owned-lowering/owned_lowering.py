"""Exact QSELF source expansion into the unchanged lifecycle Event alphabet.

This is finite-template construction. It does not run Gaussian payloads or
claim that an opaque Python callback is a physical implementation.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('qself_retained_ir', ROOT/'vendor/source_ir.py')
IR = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = IR
spec.loader.exec_module(IR)


def require(test, message):
    if not test:
        raise ValueError(message)


def expansion(caller, site, port, bank=('outer-query-bank',)):
    require(type(site) is int and 0 <= site < len(caller['events']), 'actual QSELF source site')
    raw = caller['events'][site]
    require(len(raw) == 4 and raw[0] == 'A' and raw[1] == 'QSELF' and raw[3] == -1, 'actual current QSELF source class')
    require(type(port) is int and port in caller['types']['A']['ports'], 'actual source type port')
    owner = ('main', raw[0], raw[2], port)
    require(owner != bank, 'owned bank disjoint from public owner')
    token = ('qself6937', site, port, tuple(raw))
    events = (IR.Event('INIT', (bank,), token),
              IR.Event('COPY', (bank, owner), token),
              IR.Event('SERVICE', (bank,), ('query-in',)+token),
              IR.Event('PAID', (bank,), token, 1),
              IR.Event('SERVICE', (bank,), ('query-out',)+token),
              IR.Event('SERVICE', (owner, bank), ('SWAP',)+token),
              IR.Event('CLEAR', (bank,), token))
    # This one-input rank-one fragment is a structural/lifetime check. Its
    # target is NOT added to the enclosing caller's productive invoice.
    unit = IR.Unit('owned-QSELF-fragment', ((owner, 1),), (bank,), events).check()
    return unit


def check_expansion(unit, caller, site, port):
    unit.check()
    target = expansion(caller, site, port)
    require(unit.roles == target.roles and unit.owned == target.owned and unit.events == target.events,
            'exact source-preserving QSELF expansion, including ordered SWAP and clearance')


def inventory(caller, word):
    sites = [(i, e) for i, e in enumerate(caller['events']) if len(e) > 1 and e[1] == 'QSELF']
    require(sites == [(457, ['A', 'QSELF', 0, -1]), (575, ['A', 'QSELF', 19, -1])], 'complete pinned QSELF census')
    records = []
    counts = Counter()
    for site, raw in sites:
        for port in caller['types']['A']['ports']:
            unit = expansion(caller, site, port)
            check_expansion(unit, caller, site, port)
            counts.update(e.op for e in unit.events)
            records.append([site, port, [[e.op, e.fields, e.token, e.rank] for e in unit.events]])
    require(len(records) == 192 and counts['PAID'] == counts['INIT'] == counts['COPY'] == counts['CLEAR'] == 192,
            'one complete copied-bank lifetime and one rank-one request per instance')
    # The old local source lowerer accepts the new native word structurally.
    # This checks operand/chart/lifetime preservation; it is not a table replay.
    events, local = IR.current_local(word)
    require(local['events'] == 71144 and local['owned_lifetimes'] == 54 and local['peak_live'] == 43,
            'source native typed chronology')
    unit = expansion(caller, sites[0][0], caller['types']['A']['ports'][0])
    names = {f: ('actual-remapped-port', j) for j, f in enumerate([unit.roles[0][0], unit.owned[0]])}
    remapped = tuple(IR.remap(e, names, ('compiled-fragment', 17)) for e in unit.events)
    lifted = IR.Unit('remapped-fragment', ((names[unit.roles[0][0]], 1),), (names[unit.owned[0]],), remapped).check()
    require(lifted.events[5].fields == (names[unit.roles[0][0]], names[unit.owned[0]]), 'actual ordered remapped SWAP')
    require(lifted.events[3].rank == 1 and lifted.events[3].fields == (names[unit.owned[0]],), 'actual owned paid recipient')
    return {'sites': [i for i, _ in sites], 'source_roles': [e[2] for _, e in sites],
            'instances': len(records), 'IR_events': sum(counts.values()), 'event_counts': dict(counts),
            'private_query_banks_per_live_unit': 1, 'new_productive_credit': 0,
            'patch_sha256': hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest(),
            'local_typed_events': len(events), 'local_source_events': local['events'],
            'local_owned_lifetimes': local['owned_lifetimes'], 'local_peak_owned': local['peak_live'],
            'SERVICE_registry_installed': False,
            'dispatch_scope': 'Relative typed-IR expansion only. New qself6937 tokens need an exact provider/table registry and header/format binding; old source-specific binders are not reused implicitly.',
            'physical_fullcaller_executed': False}, records


def adapter_records(caller, word, bases, omit_translation=False, omit_inverse=False):
    by_port = {row['port']: row for row in bases['records']}
    require(sorted(by_port) == list(range(104)), 'complete basis-port dictionary')
    checks = 0
    for port in caller['types']['A']['ports']:
        row = by_port[port]
        q = row['q']; basis = row['basis']
        require(q == word['ports'][port] and basis[0] == q and len(basis) == 9, 'actual native Q source and basis')
        require(all(0 < v < 512 for v in basis), 'nine-axis adapter domain')
        require(all((a & b).bit_count() % 2 == (i == j)
                    for i, a in enumerate(basis) for j, b in enumerate(basis)), 'exact orthogonal basis')
        def B(x):
            return sum(((a & x).bit_count() % 2) << i for i, a in enumerate(basis))
        def inverse(y):
            x = 0
            for i, a in enumerate(basis):
                if y >> i & 1:
                    x ^= a
            return x
        require(B(q) == 1, 'q maps to positive selected coordinate')
        for frequency in range(512):
            # Polynomial/spectral equation for every one-column frequency.
            parity = (q & frequency).bit_count() % 2
            require((B(frequency) if omit_inverse else inverse(B(frequency))) == frequency, 'exact inverse ambient basis return')
            require((B(frequency) & 1) == parity, 'exact positive central phase after conjugation')
            require((parity+(0 if omit_translation else 2)*parity) % 4 == (-parity) % 4, 'Q^-1 includes Q^2 translation with exact phase')
            checks += 1
    return {'new_ports': len(caller['types']['A']['ports']), 'exact_one_column_phase_equations': checks,
            'nine_axis_maps_per_QSELF': 2, 'translations_per_QSELF': 1,
            'all_positive_columns': 'Proved by exact tensor identity in PROOF.md, not inferred from these finite checks.',
            'provider_status': 'Actual tape execution, common precision, signed range and numerical return remain inherited contracts.'}
