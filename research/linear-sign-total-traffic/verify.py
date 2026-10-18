#!/usr/bin/env python3
"""Independent source-bound total-traffic audit. Arham Tahir / Codex; Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import types
from traffic import countdown, total

PACKAGE = Path(__file__).resolve().parent
HEAD = '7dba5452a4071a856a0b11cebdcd2d3b6bcd7659'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_bytes(base=PACKAGE):
    manifest = json.loads((base/'EXPORTS.json').read_text())
    require(manifest['commit'] == HEAD, 'wrong predecessor head')
    result = {}
    for row in manifest['files']:
        p = (base/row['path']).resolve()
        require(p.is_relative_to(base.resolve()), 'source escapes package')
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash: '+row['path'])
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')
        require(row['commit'] == HEAD, 'mixed predecessor heads')
        result[p.stem] = data
    require(set(result) == {'words', 'records', 'stream', 'cardinality', 'counts',
                           'cardinal_counts', 'bitstream', 'linear_sign', 'PROOF',
                           'PREDECESSOR-NOTICE', 'check_sign'}, 'source inventory')
    return result


def load_sources(data, mutation=None):
    modules = {}
    for name in ('words', 'records', 'stream', 'cardinality', 'counts',
                 'cardinal_counts', 'bitstream', 'linear_sign'):
        module = types.ModuleType(name)
        module.__file__ = str(PACKAGE/'sources'/(name+'.py'))
        sys.modules[name] = modules[name] = module
        payload = data[name].decode()
        if name == 'linear_sign' and mutation:
            payload = mutation(payload)
        # Read/compile authenticated source; stale bytecode cannot be executed.
        exec(compile(payload, module.__file__, 'exec'), module.__dict__)
    return modules


def traffic(meter):
    return meter.reads+meter.writes+meter.moves


def same_receipt(actual, expected):
    # Python equality conflates True and 1; publication receipts must not.
    return json.dumps(actual, sort_keys=True, separators=(',', ':')) == json.dumps(
        expected, sort_keys=True, separators=(',', ':'))


class Harness:
    def __init__(self, modules):
        self.modules, self.tapes, self.last_origin = modules, [], None
        harness, original = self, modules['records'].Tape

        class ObservedTape(original):
            def __init__(self):
                super().__init__()
                self.payload_source, self.origins = False, {}
                harness.tapes.append(self)

            def read(self):
                value = super().read()
                if self.payload_source and value in (0, 1):
                    harness.last_origin = self.head-1
                return value

            def write(self, value):
                if value in (0, 1):
                    self.origins[self.head] = harness.last_origin
                super().write(value)

        self.Tape = ObservedTape
        for module in modules.values():
            if hasattr(module, 'Tape'):
                module.Tape = ObservedTape

    def measured(self, arena):
        return traffic(arena.meter)+sum(traffic(t.meter) for t in self.tapes)

    def sign(self, m, b, s, width=None, malformed=None):
        mod, width = self.modules, width or m.bit_length()+1
        words, volume = mod['words'], m*b*s
        arena = words.Arena(width)
        modulus = arena.input(m)
        if width == m.bit_length()+1:
            ring = words.Ring(modulus)
        else:
            # Padded interface control; the actual Ring constructor forbids it.
            ring = types.SimpleNamespace(arena=arena, modulus=modulus,
                                         one=arena.literal(1), raw=words.Unsigned(arena))
        counts = mod['cardinal_counts'].Count
        bc, sc = counts.literal(b), counts.literal(s)
        before, suffix = bc.marginal(), sc.marginal()
        bc.close(); sc.close()
        source = self.Tape()
        source.cells.extend((i*7+i//3) % 2 for i in range(volume))
        source.payload_source = True
        if malformed == 'truncated':
            source.cells.pop()
        elif malformed == 'overlong':
            source.cells.append(1)
        elif malformed == 'non-bit':
            source.cells[2] = 3
        initial, protected = bytes(source.cells), set(arena.live)
        numerical = {i: bytes(arena.words[i].cells) for i in protected}
        template = bytes(arena.template.cells)
        cardinalities = (bytes(before.tape.cells), bytes(suffix.tape.cells))
        started, moves = self.measured(arena), source.meter.moves
        def forbidden(_):
            raise ValueError('runtime numerical decode')
        old_inspect, output = words.Word.inspect, None
        words.Word.inspect = forbidden
        try:
            try:
                output = mod['linear_sign'].sign_address(source, ring, 3, before, suffix)
            except ValueError:
                require(malformed is not None, 'unexpected sign rejection')
                return {'rejected': malformed, 'source_restored': bytes(source.cells) == initial and source.head == 1}
            measured, moved = self.measured(arena)-started, source.meter.moves-moves
            require(malformed is None, 'malformed source accepted')
            wanted = []
            for address in range(volume):
                row, inner = divmod(address, s)
                outer, atom = divmod(row, m)
                wanted.append((outer*m+(-atom) % m)*s+inner)
            actual = [output.origins[i+1] for i in range(volume)]
            require(actual == wanted, 'wrong address permutation')
            require(bytes(output.cells[1:]) == bytes(initial[i+1] for i in wanted), 'Boolean payload')
            require(bytes(source.cells) == initial and source.head == output.head == 1, 'payload restoration')
            require((bytes(before.tape.cells), bytes(suffix.tape.cells)) == cardinalities, 'cardinality content')
            require(before.tape.head == suffix.tape.head == 1, 'cardinality heads')
            require(arena.live == protected, 'numerical temporary leak')
            require(all(arena.words[i].head == 1 for i in protected), 'numerical heads')
            require(all(bytes(arena.words[i].cells) == value for i, value in numerical.items()),
                    'borrowed numerical content')
            require(bytes(arena.template.cells) == template and arena.template.head == 1,
                    'numerical template restoration')
            return {'m': m, 'b': b, 's': s, 'width': width, 'volume': volume,
                    'traffic': measured, 'source_moves': moved,
                    'origin_sha256': hashlib.sha256(json.dumps(actual).encode()).hexdigest()}
        finally:
            words.Word.inspect = old_inspect
            if output is not None:
                output.clear()
            source.clear(); before.close(); suffix.close()
            arena.free_many(ring.one, modulus)
            require(not arena.live, 'fixture cleanup')


def counter_checks(data):
    modules = load_sources(data)
    harness, rows = Harness(modules), []
    for n in range(129):
        for padding in (0, 1, 7):
            digits = max(2, n.bit_length())+padding
            arena = modules['words'].Arena(digits)
            source = arena.input(n)
            original, started = bytes(source.cells), harness.measured(arena)
            counter = modules['stream'].Counter(source)
            for _ in range(n):
                require(not counter.finished, 'early countdown completion')
                counter.decrement()
            require(counter.finished, 'countdown did not finish')
            counter.close()
            measured = harness.measured(arena)-started
            require(measured == countdown(n, digits), 'countdown identity: '+str((n,digits,measured,countdown(n,digits))))
            require(bytes(source.cells) == original and source.head == 1, 'counter input restoration')
            rows.append([n, digits, measured]); arena.free(source)
    return {'cases': len(rows), 'sha256': hashlib.sha256(json.dumps(rows).encode()).hexdigest()}


def run():
    data = source_bytes()
    counters = counter_checks(data)
    harness, rows = Harness(load_sources(data)), []
    for m in (2, 3, 4, 5, 8, 9, 17, 25, 33, 65):
        for b in (1, 2, 5):
            for s in (1, 2, 3, 5, 7):
                row = harness.sign(m, b, s)
                require(row['traffic'] == sum(total(m,b,s).values()), 'sign traffic: '+str((m,b,s,row['traffic'],total(m,b,s))))
                require(row['source_moves'] == (6*m-8)*b*s+4, 'source movements')
                require(row['traffic'] <= 2048*row['volume'], 'canonical linear bound')
                rows.append(row)
    malformed = [harness.sign(3,2,2,malformed=x) for x in ('truncated','overlong','non-bit')]
    require(all(x['source_restored'] for x in malformed), 'malformed source restoration')
    padded = harness.sign(2,1,1,width=1024)
    require(padded['traffic'] == sum(total(2,1,1,1024).values()), 'padded exact formula')
    require(padded['traffic'] > 2048*padded['volume'], 'width premise control')
    def padded_two(text):
        start = text.index('                        for _ in range(2):')
        end = text.index('            finally:\n                remaining.close()', start)
        return text[:start]+'                        move_slices(source, two, suffix, -1)\n'+text[end:]
    mutant = Harness(load_sources(data, padded_two)).sign(65,1,1)
    baseline = next(x for x in rows if (x['m'],x['b'],x['s']) == (65,1,1))
    require(mutant['source_moves'] == baseline['source_moves'], 'padded-two movement control')
    require(mutant['traffic'] > baseline['traffic'], 'padded-two total control')
    require(mutant['origin_sha256'] == baseline['origin_sha256'], 'padded-two endpoint control')
    wrong = Harness(load_sources(data, lambda text:text.replace('range(2)', 'range(1)')))
    try:
        wrong.sign(5,1,2)
    except ValueError:
        pass
    else:
        raise ValueError('one-backstep mutant accepted')
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        shutil.copy(PACKAGE/'EXPORTS.json', base/'EXPORTS.json')
        shutil.copytree(PACKAGE/'sources', base/'sources')
        with (base/'sources'/'linear_sign.py').open('ab') as stream:
            stream.write(b'\n# changed\n')
        try:
            source_bytes(base)
        except ValueError:
            pass
        else:
            raise ValueError('source mutation accepted')
    return {'status': 'PASS_LINEAR_SIGN_TOTAL_TRAFFIC', 'source_head': HEAD,
            'counter_identity': counters, 'sign_cases': len(rows),
            'addresses': sum(x['volume'] for x in rows),
            'sign_receipt_sha256': hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
            'exact_formula': 'PROOF.md', 'canonical_bound': '2048V',
            'malformed_controls': malformed, 'padded_width_control': padded,
            'padded_two_control': {'baseline_traffic': baseline['traffic'], 'mutant_traffic': mutant['traffic'],
                                   'unchanged_source_moves': mutant['source_moves'], 'same_endpoint': True},
            'wrong_backstep_rejected': True, 'source_mutation_rejected': True,
            'scope': 'Logical successful sign interval only; no physical compiler, caller, H2, supplier or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Create a new receipt; refuse overwrite')
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    else:
        expected = json.loads((PACKAGE/'RESULT.json').read_text())
        require(same_receipt(result, expected), 'receipt mismatch')
        changed = dict(expected, source_mutation_rejected=1)
        require(not same_receipt(result, changed), 'typed receipt control')
    print(result['status'], 'counters='+str(result['counter_identity']['cases']), 'signs='+str(result['sign_cases']))


if __name__ == '__main__':
    main()
