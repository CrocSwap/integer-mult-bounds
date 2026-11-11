"""Independent review of the CRT endpoint join, not its author verifier.

The oracle uses direct CRT idempotents, unlike the encoded mixed-radix
reconstruction. Observer-only integers/snapshots never enter runtime control.
Run: python3 -I -W error -B independent_check.py [package-directory]
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import json
import math
import sys


PKG = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def load(name, relative):
    spec = spec_from_file_location(name, PKG / relative)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


w = load("words", "source/research/r437-preparation-composition/predecessor4025/source/words.py")
r = load("peer_records", "source/research/r437-preparation-composition/predecessor4025/source/records.py")
e = load("peer_entry", "source/research/encoded-crt-entry-lifecycle/entry.py")
n = load("peer_numeric", "source/research/encoded-current-crt/producer.py")
o = load("peer_owner", "source/research/crt-persistent-numerical-owner/owner.py")
c = load("peer_canonical", "source/research/crt-mixed-row-entry/bridge.py")
f = load("peer_frontend", "source/research/encoded-balanced-crt-entry/frontend.py")
endpoint = load("peer_endpoint", "endpoint.py")


def fixture(moduli, widths, coords):
    tape = e.Port(w)
    fields = []
    for modulus, width, coordinate in zip(moduli, widths, coords):
        tape.append(r.ROOT)
        for _ in range(width):
            tape.append(w.ONE)
        tape.append(r.WORD_END)
        for value, end in ((modulus, r.WORD_END), (coordinate, r.RECORD_END)):
            positions = []
            for b in range(width):
                positions.append(tape.head)
                tape.append((value >> b) & 1)
            tape.append(end)
        fields.append(positions)
    tape.append(w.RIGHT)
    tape.rewind()
    # Deliberately hostile inaccessible tail: includes a second LEFT/RIGHT.
    tape.cells.extend([r.PAIR, w.LEFT, w.RIGHT, w.ONE, w.BLANK, r.ROOT])
    return tape, fields


def decode(tape, fields):
    return tuple(sum(tape.cells[position] << b for b, position in enumerate(field))
                 for field in fields)


def node_math(moduli, current, start, half):
    result = list(current)
    selected = moduli[start:start+half]
    total = math.prod(selected)
    lower = 0
    if all(current[i] < moduli[i] for i in range(start, start+half)):
        prefix = 1
        # CRT idempotent formula, independent of digit-by-digit reconstruction.
        for i in range(start, start+half):
            modulus = moduli[i]
            residue = (current[i] * prefix) % modulus
            cofactor = total // modulus
            lower += residue * cofactor * pow(cofactor, -1, modulus)
            prefix *= modulus
        lower %= total
    prefix = total
    for i in range(start+half, start+2*half):
        if current[i] < moduli[i]:
            result[i] = (current[i] + lower * pow(prefix, -1, moduli[i])) % moduli[i]
        prefix *= moduli[i]
    return tuple(result)


def port_actions(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def run_case(moduli, widths, original, implementation=endpoint):
    require(len(moduli) >= 2 and len(moduli) & (len(moduli)-1) == 0, "fixture dyadic")
    require(max(widths)-min(widths) <= 1, "fixture near-equal widths")
    require(all(2 <= s < 2**h and 0 <= x < 2**h
                for s, h, x in zip(moduli, widths, original)), "fixture domain")
    require(all(math.gcd(s,t)==1 for i,s in enumerate(moduli) for t in moduli[:i]),
            "fixture pairwise coprime")
    source, fields = fixture(moduli, widths, original)
    initial = bytes(source.cells)
    coordinates = set(sum(fields, []))
    state = implementation.Endpoint(f, w, r, e, n, o, c, source)
    it = state.iterator
    private = (*it.bank.ports, *it.guards, *it.counters.values(), state.staging)
    all_ports = (source, *private)
    identities = tuple(id(port.cells) for port in all_ports)
    require(len(private) == 79 and len(set(identities)) == 80, "fixed disjoint role inventory")
    A, d = sum(widths), len(widths)
    M = 2+3*A+4*d
    expected = tuple(original)
    node_count = 0
    adapter_actions = 0
    numeric_actions = 0
    max_stage_head = 1
    old_step = e.Port.step

    def observing_step(port, direction):
        nonlocal max_stage_head
        old_step(port, direction)
        if port is state.staging:
            max_stage_head = max(max_stage_head, port.head)

    e.Port.step = observing_step
    try:
        half = 1
        while half < d:
            for start in range(0, d, 2*half):
                node_count += 1
                lease = it.next()
                require(lease is not None, "exact node count lower bound")
                require(bytes(source.cells)==initial or decode(source,fields)==expected,
                        "source supplied current state")
                require(source.head == 1, "source restored after fresh projection")
                P = 1+sum(widths[start:start+2*half])
                guide = lease.actual.guide
                require(list(guide.cells[:P+1]) == [w.LEFT]+[w.ONE]*P,
                        "guide reflects preserved widths at actual node")
                require(guide.head==1, "guide handoff head")
                axis = it.counters['axis']
                require(axis.cells[start+1]==r.STEP, "encoded start agrees with independent schedule")
                if start+2*half < d:
                    require(axis.cells[start+2*half+1]==r.VALUE, "encoded next-node marker")
                topologies = {key:(bytes(port.cells),port.head)
                              for key,port in it.counters.items() if key!='width'}
                before = bytes(source.cells),source.head
                raw = port_actions(all_ports)
                state.stage(lease)
                require((bytes(source.cells),source.head)==before,
                        "source immutable throughout live numerical lease")
                require(all((bytes(it.counters[key].cells),it.counters[key].head)==snapshot
                            for key,snapshot in topologies.items()), "staging restores topology")
                require(it.counters['width'].head==1 and
                        all(x==w.BLANK for x in it.counters['width'].cells[1:]),
                        "width role completely erased after full scan")
                stage_actions = port_actions(all_ports)-raw
                lease.close()
                meter = lease.actual.context.arena.meter
                numeric_actions += meter.reads+meter.writes+meter.moves
                require(not it.live and not it.bank.busy, "close releases numerical lease")
                raw = port_actions(all_ports)
                state.commit()
                actions = stage_actions+port_actions(all_ports)-raw
                require(actions <= 2048*(M+2*half*(P+2))+32,
                        "full stage/commit raw tariff")
                adapter_actions += actions
                expected = node_math(moduli,expected,start,half)
                require(decode(source,fields)==expected, "direct CRT node endpoint")
                require(source.head==1 and tuple(id(port.cells) for port in all_ports)==identities,
                        "physical identity and source entry head")
                require(len(source.cells)==len(initial) and
                        all(source.cells[i]==initial[i] for i in range(len(initial))
                            if i not in coordinates), "source metadata and hostile old tail")
                require(all(port.head==1 and all(x==w.BLANK for x in port.cells)
                            for port in (*it.bank.ports,*it.guards,state.staging)),
                        "every numerical/guard/staging history fully retired")
            half *= 2
        require(it.closed and it.next() is None, "exact terminal boundary")
        require(all(port.head==1 and all(x==w.BLANK for x in port.cells)
                    for port in private), "all 79 histories blank at termination")
        require(len(state.staging.cells)==M and max_stage_head==M,
                "M retained staging cells and M+1 visited span")
        if all(x<s for x,s in zip(original,moduli)):
            K, prefix = 0,1
            for x,s in zip(original,moduli):
                K += x*prefix
                prefix *= s
            closed = []
            prefix = 1
            for s in moduli:
                closed.append(K*pow(prefix,-1,s)%s)
                prefix *= s
            require(expected==tuple(closed), "independent global mixed-radix closed form")
        return dict(axes=d,widths=widths,nodes=node_count,
                    original=original,result=expected,adapter_actions=adapter_actions,
                    numeric_actions=numeric_actions,staging_backing=M,staging_visited=M+1)
    finally:
        e.Port.step = old_step


def main():
    cases = [
        ((2,3),(2,2),(0,0)),
        ((2,3),(2,2),(1,2)),
        ((2,3),(2,2),(3,2)),
        ((3,5),(3,3),(2,7)),
        ((5,7),(4,3),(4,6)),
        ((17,257),(9,9),(16,256)),
        ((17,257),(9,9),(511,256)),
        ((17,257),(9,9),(16,511)),
        ((2,3,5,7),(3,4,3,4),(1,2,4,6)),
        ((2,3,5,7),(3,4,3,4),(2,1,4,6)),
        ((2,3,5,7),(3,4,3,4),(1,3,4,6)),
        ((2,3,5,7),(3,4,3,4),(1,2,5,6)),
        ((2,3,5,7),(3,4,3,4),(1,2,4,7)),
        ((2,3,5,7),(3,4,3,4),(7,15,7,15)),
        ((2,3,5,7),(4,3,4,3),(0,2,3,5)),
        ((2,3,5,7),(4,3,4,3),(1,0,2,4)),
        ((2,3,5,7,11,13,17,19),(4,4,4,5,5,4,5,5),(1,2,4,6,10,12,16,18)),
        ((2,3,5,7,11,13,17,19),(4,4,4,5,5,4,5,5),(1,3,4,6,10,15,16,31)),
    ]
    rows = [run_case(*case) for case in cases]
    text = (PKG/'endpoint.py').read_text()
    mutated = ModuleType('peer_mutant')
    require(text.count('self.staging.append(new)')==1, 'unique mutation site')
    exec(compile(text.replace('self.staging.append(new)','self.staging.append(old)'),
                 'stale-coordinate-negative-control','exec'),mutated.__dict__)
    try:
        run_case((2,3,5,7),(3,4,3,4),(1,2,4,6),mutated)
    except AssertionError as err:
        require(str(err)=='direct CRT node endpoint', 'negative control rejects for semantic mismatch')
    else:
        raise AssertionError('stale-coordinate mutant survived')
    output = dict(status='PASS',method='direct CRT idempotents plus independent global closed form',
                  cases=len(rows),nodes=sum(row['nodes'] for row in rows),
                  negative_controls=['stale-coordinate commit rejected'],rows=rows,
                  pins={str(p.relative_to(PKG)):sha256(p.read_bytes()).hexdigest()
                        for p in sorted(PKG.rglob('*.py')) if '__pycache__' not in str(p)},
                  proof_sha256=sha256((PKG/'PROOF.md').read_bytes()).hexdigest())
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
