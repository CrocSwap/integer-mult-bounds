"""Source-bound actual-file endpoint audit for the ordinary tagged quotient route."""
from contextlib import ExitStack
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from types import FunctionType
import argparse
import inspect
from importlib import import_module
import json
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from byte_meter import Meter, aliases, need


def peek(tape, start=0, end=None):
    at = tape.tell()
    tape.seek(start)
    value = tape.read() if end is None else tape.read(end-start)
    tape.seek(at)
    return value


def pattern(n, salt=0):
    return bytes((17*i + i//251 + salt) % 256 for i in range(n))


def owner_case(n, digits, groups, older=1, gap=1, suffix=1):
    from binary_receiver import Receiver
    from receiver import OwnerBanks
    from factored_frames import inverse_word
    core = Receiver(n, (1, digits, 0, 0), direct=False)
    body = older * core.atom**(2*n) * gap * suffix
    block, q = core.high * body, core.low
    volume = groups * q * block
    raw, guard = pattern(volume, 3), pattern(volume, 117)
    meter = Meter().bind()
    core.previous = meter.previous
    word = (('add', 0, 1, Fraction(1)), ('add', 1, 0, Fraction(2)),
            ('scale', 0, Fraction(-1)))
    try:
        with core.storage() as arena, ExitStack() as held:
            saved = []
            for kind, arity in (('compiler', 3), ('triangular-body', 2)):
                for i, page in enumerate(held.enter_context(arena.frames(kind, arity))):
                    data = (kind + ':' + str(i) + ':dirty-parent').encode()
                    page.write(data)
                    saved.append((page, data))
            pg, ag = b'pending:borrowed-parent', b'answers:borrowed-parent'
            p = BytesIO(pg); p.seek(len(pg)); arena.pending.push_reverse(p, len(pg))
            arena.answers.append(BytesIO(ag), len(ag))
            baseline = {key: head.peak for key, head in arena.heads.items()}
            with arena.frames('compiler', 1) as (backing,):
                def transition(src, dst, w):
                    core.transition(src, dst, w, 1, groups, older, gap, suffix, lambda a,b: 1)
                banks = OwnerBanks(backing, n, volume, transition)
                owner, spectator = banks.zero(), banks.zero()
                banks.install(owner, BytesIO(raw)); banks.install(spectator, BytesIO(guard))
                for w in (word, inverse_word(word), word, inverse_word(word)):
                    banks.route(owner, w)
                    banks.start(spectator)
                    need(backing.read(volume) == guard, 'borrowed neighboring owner changed')
                banks.start(owner)
                need(backing.read(volume) == raw, 'route/inverse did not restore full owner')
                need(backing.size == 2*volume, 'owner route changed backing extent')
                banks.retire(owner); banks.retire(spectator)
                need(not banks.live, 'owner route retained a physical owner')
            for page, data in saved:
                need(peek(page) == data, 'suspended named parent changed')
            need(arena.pending.top == len(pg) and arena.answers.top == len(ag),
                 'ordinary route changed a parent packet marker')
            need(peek(arena.pending.head.file, 0, len(pg)) == pg[::-1], 'pending parent changed')
            need(peek(arena.answers.head.file, 0, len(ag)) == ag, 'answer parent changed')
            named_extra = sum(arena.heads[('triangular-body', i)].peak - baseline[('triangular-body', i)]
                              for i in range(2))
            need(named_extra <= 2*body, 'compensation page exceeded its body byte cap')
            for key, head in arena.heads.items():
                live = head.frames[-1].base + head.frames[-1].size if head.frames else 0
                if key == ('pending', 0): live = len(pg)
                if key == ('answers', 0): live = len(ag)
                need(peek(head.file, live, head.peak) == bytes(head.peak-live),
                     'dirty historical named-page suffix survived return')
            arena.pending.pop_forward(BytesIO(), len(pg))
            arena.answers.take_answers(0, BytesIO())
        result = meter.report()
        bound = Fraction(volume + 5*q*block + 5*q*n*n + 5*body) + Fraction(32*block, 3)
        observed = result['local_historical_bytes'] + named_extra
        need(observed <= bound < 8*volume, 'historical byte inequality failed')
        result.update({'n':n, 'digits':digits, 'groups':groups, 'body_bytes':body,
                       'highs':core.high, 'low_packets':q, 'owner_bytes':volume,
                       'tag_bytes_per_group':q*n*n, 'named_scratch_bytes':named_extra,
                       'local_plus_named_bytes':observed,
                       'rational_bound':[bound.numerator,bound.denominator],
                       'borrowed_bank_bytes':2*volume, 'route_calls':4,
                       'sha256_restored_owner':sha256(raw).hexdigest()})
        print('owner', n, digits, groups, volume, observed, flush=True)
        return result
    finally:
        meter.unbind()


def unit_cases():
    from limb_scale import unit_scale
    meter = Meter().bind()
    results = []
    try:
        for digits in range(8):
            for unit in (1, 2, 4, 5, -1):
                prefixes, piece, side = 2, 3, 3**digits
                raw = pattern(prefixes*side*piece, digits+unit)
                out = BytesIO()
                unit_scale(BytesIO(raw), out, digits, prefixes, piece, unit, meter.previous)
                expected = bytearray(len(raw))
                for p in range(prefixes):
                    for x in range(side):
                        start = (p*side+x)*piece
                        dest = (p*side+unit*x%side)*piece
                        expected[dest:dest+piece] = raw[start:start+piece]
                need(out.getvalue() == expected, 'independent unit permutation oracle failed')
                results.append({'digits':digits,'unit':unit,'bytes':len(raw)})
        result = meter.report()
        rmax = max(case['bytes'] for case in results)
        need(3*result['local_historical_bytes'] <= 17*rmax, 'unit historical 17R/3 bound failed')
        result['cases'] = results
        print('unit', len(results), result['local_historical_bytes'], flush=True)
        return result
    finally:
        meter.unbind()


def type_cases():
    from streaming_routes import type_route, ternary_extent
    results = []
    for rows, types, suffix in ((2,2,5),(2,4,5),(2,16,5),(2,27,5),(2,28,5),
                                (2,1,5),(0,4,5),(2,4,0)):
        meter = Meter().bind()
        try:
            volume = rows*types*suffix
            raw, middle, out = pattern(volume, 91), BytesIO(), BytesIO()
            type_route(BytesIO(raw), middle, rows, types, suffix)
            middle.seek(0)
            type_route(middle, out, rows, types, suffix, inverse=True)
            need(out.getvalue() == raw, 'padded type route roundtrip failed')
            result = meter.report()
            padded = rows*ternary_extent(types)[1]*suffix
            need(result['local_historical_bytes'] <= 3*padded, 'padded role-byte bound failed')
            if volume: need(result['local_historical_bytes'] < 9*volume, 'type 9V bound failed')
            if not rows or not suffix or types == 1:
                need(not result['historical_role_bytes'], 'zero/simple type route allocated scratch')
            result.update({'rows':rows,'types':types,'suffix':suffix,'bytes':volume,'padded_bytes':padded})
            results.append(result)
        finally:
            meter.unbind()
    print('type', len(results), flush=True)
    return results


def empty_case():
    from quotient_route import quotient_right_route
    meter = Meter().bind()
    try:
        quotient_right_route(BytesIO(), BytesIO(), 2, 1, 0, 81, (('add',0,1,Fraction(1)),))
        result = meter.report()
        need(len(result['historical_role_bytes']) == 10 and result['local_historical_bytes'] == 0,
             'empty groups had a payload extent')
        return result
    finally:
        meter.unbind()


def mutate(name):
    import quotient_route, limb_scale, streaming_routes
    if name == 'bucket-erase':
        owner, attr = quotient_route, 'sort_packets'
        old, new = '                erase(tape)', '                pass  # omit bucket erase'
    elif name == 'odd-collision':
        owner, attr = limb_scale, 'unit_scale'
        old, new = 'outs[factor * t % 3]', 'outs[0]'
    else:
        owner, attr = streaming_routes, 'erase'
        old, new = '    write_zeros(tape, size)', '    pass  # discard dirty bytes'
    original = getattr(owner, attr)
    source = dedent(inspect.getsource(original))
    need(source.count(old) == 1, 'mutation lacks a unique source site')
    ns = dict(original.__globals__)
    exec(compile(source.replace(old,new), original.__code__.co_filename, 'exec'), ns)
    created = ns[original.__name__]
    replacement = FunctionType(created.__code__, original.__globals__, created.__name__,
                               created.__defaults__, created.__closure__)
    replacement.__kwdefaults__ = created.__kwdefaults__
    aliases(original, replacement)
    setattr(owner, attr, replacement)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mutation', choices=('bucket-erase','odd-collision','dirty-truncate'))
    parser.add_argument('--full-high', action='store_true')
    args = parser.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    # Verify the exact dynamically resolved source against the stable snapshot.
    here = Path(__file__).resolve().parent
    bindings = json.loads((here/'SOURCE-BINDINGS.json').read_text())
    for name, pin in bindings['resolved_modules'].items():
        module = import_module(name)
        need(sha256(Path(module.__file__).read_bytes()).hexdigest() == pin['sha256'],
             'resolved source mismatch: '+name)
    if args.mutation:
        mutate(args.mutation)
        try:
            if args.mutation == 'odd-collision': unit_cases()
            else: owner_case(2,1,2)
        except AssertionError as error:
            text = str(error)
            # Cleanup may expose a second symptom; the dirty-data control is
            # rejected by the audited physical truncate/close, never an oracle.
            if args.mutation == 'dirty-truncate':
                need('erasure' in text or 'dirty byte' in text or 'ownership' in text,
                     'unexpected dirty-truncate rejection: '+text)
            else:
                need('role byte cap exceeded' in text, 'unexpected cap rejection: '+text)
            result = {'status':'rejected','mutation':args.mutation,'reason':text}
        else:
            raise AssertionError('mutation survived: '+args.mutation)
    else:
        started = time.monotonic()
        owners = [owner_case(2,1,1), owner_case(2,1,3,2,2,2), owner_case(3,1,1)]
        if args.full_high: owners.append(owner_case(2,2,1))
        result = {'status':'PASS_ORDINARY_ROLE_BYTES','owner_cases':owners,
                  'unit_cases':unit_cases(),'type_cases':type_cases(),'empty_case':empty_case(),
                  'seconds':time.monotonic()-started}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
