"""Independent integer oracle for the two source codecs and their lifecycle.

Only this test observer decodes payloads. The tested bridge uses actual retained
tape primitives. Numerical Core fixtures are separately labelled.
"""
from contextlib import ExitStack
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from boundary_codec import Codec, Format, BoundCore
from bridge_sources import native_models, authenticate


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sigmag(value, bits):
    need(abs(value) < 1 << (bits - 1), 'oracle external carrier')
    return str(int(value < 0)) + format(abs(value), f'0{bits-1}b')


def trunc(value, shift):
    return (-1 if value < 0 else 1) * (abs(value) >> shift)


def native_emit(tape, values, bits):
    for value in values:
        need(-(1 << (bits - 1)) <= value < 1 << (bits - 1), 'oracle native carrier')
        encoded = value % (1 << bits)
        for i in range(bits):
            tape.append((encoded >> i) & 1)
    tape.rewind()


def native_decode(tape, bits, blank):
    body = bytes(tape.cells[1:])
    body = body.rstrip(bytes((blank,)))
    need(len(body) % bits == 0, 'whole native oracle words')
    out = []
    for start in range(0, len(body), bits):
        raw = body[start:start + bits]
        need(all(b in (0, 1) for b in raw), 'binary native oracle words')
        value = sum(b << i for i, b in enumerate(raw))
        out.append(value - (raw[-1] << bits))
    return out


def bill(codec):
    return sum(sum(t.actions[k] for k in ('read', 'write', 'move'))
               for t in (*codec.templates, *codec.work)) + sum(
                   getattr(codec.input.meter, k) for k in ('reads', 'writes', 'moves'))


def backing(codec):
    return sum(t.bill()['retained_cells'] for t in (*codec.templates, *codec.work)) + len(codec.input.cells)


def forbid_observers(B, C):
    stack = ExitStack()
    stack.enter_context(patch.object(B.Tape, 'inspect', side_effect=ValueError('online payload inspection')))
    stack.enter_context(patch.object(B.Tape, '__init__', side_effect=ValueError('online B tape construction')))
    stack.enter_context(patch.object(C, '__init__', side_effect=ValueError('online C tape construction')))
    return stack


def main():
    rows = 0
    return_cases = 0
    controls = []
    digest = sha256()
    with native_models() as (B, C, blank, initialize, erase, source, state):
        codec = Codec(B, C, blank, initialize, erase, Format(2, 0, 3, 0, 0))
        ids = tuple(map(id, (*codec.templates, *codec.work, codec.input)))
        for d in range(2, 8):
            for lift in range(4):
                for normalizer in (0, 1, 3, 8):
                    fmt = Format(d, 2, d + lift + 2, 2 + lift, normalizer)
                    codec.reconfigure(fmt)
                    for value in range(-(1 << (d - 1)) + 1, 1 << (d - 1)):
                        source_bits = sigmag(value, d) + sigmag(-value, d) + '#'
                        original = B.Tape('independent external input', source_bits)
                        z = (value << lift) + (1 if lift and value >= 0 else -1 if lift else 0)
                        returned = C()
                        native_emit(returned, (z, -z), fmt.native_bits)
                        before = original.inspect()
                        with forbid_observers(B, C):
                            actual_input = codec.prepare_input(original)
                        need(native_decode(actual_input, fmt.native_bits, blank) == [value << lift, -value << lift],
                             'exact sign/grid lift differs from integer oracle')
                        with forbid_observers(B, C):
                            actual_return = codec.prepare_return(returned, original)
                        expected = sigmag(trunc(z, fmt.drop), d) + sigmag(trunc(-z, fmt.drop), d) + '#'
                        need(actual_return.inspect() == expected, 'normalized rounded return differs from integer oracle')
                        need(original.inspect() == before, 'borrowed source changed')
                        digest.update(expected.encode())
                        codec.abort()
                        codec.abort()  # failure cleanup is deliberately idempotent
                        need(not codec.active and not codec.pending and not codec.input_armed, 'idle after consume')
                        need(all(t.inspect() == '' for t in codec.work), 'all owned external work erased')
                        need(all(b == blank for b in codec.input.cells), 'all owned native backing erased')
                        returned.clear(); erase(returned)
                        rows += 1

        # Native extreme and discarded-fraction cases use a different domain
        # than the input lift; a negative arithmetic shift would fail -1 here.
        for d in (3, 6):
            for lift in (0, 2):
                for normalizer in (0, 1, 5, 12):
                    fmt = Format(d, 1, d + lift + 1, 1 + lift, normalizer)
                    codec.reconfigure(fmt)
                    original = B.Tape('native extremes source clock', sigmag(0, d) * 2 + '#')
                    for z in (-(1 << (fmt.native_bits - 1)), -(1 << (fmt.native_bits - 1)) + 1,
                              -3, -2, -1, 0, 1, 2, 3, (1 << (fmt.native_bits - 1)) - 1):
                        returned = C(); native_emit(returned, (z, z), fmt.native_bits)
                        codec.prepare_input(original)
                        expected = trunc(z, fmt.drop)
                        if abs(expected) >= 1 << (d - 1):
                            try: codec.prepare_return(returned, original)
                            except ValueError: controls.append('external_overflow')
                            else: raise ValueError('overflow control accepted')
                        else:
                            actual = codec.prepare_return(returned, original).inspect()
                            need(actual == sigmag(expected, d) * 2 + '#', 'extreme return oracle')
                        codec.abort(); returned.clear(); erase(returned)
                        return_cases += 1

        fmt = Format(5, 3, 10, 6, 2); codec.reconfigure(fmt)
        for bad in ('1000000000#', '000000000#', '0000000000', '0000000000##', '0000x00000#'):
            original = B.Tape('malformed external input', bad)
            saved = original.inspect()
            try: codec.prepare_input(original)
            except ValueError: controls.append('malformed_external')
            else: raise ValueError('malformed external control accepted')
            codec.abort()
            need(original.inspect() == saved, 'failure changed input')

        for count in (1, 3, 4):
            original = B.Tape('return count source', sigmag(1, 5) * 2 + '#')
            returned = C(); native_emit(returned, [1] * count, fmt.native_bits)
            codec.prepare_input(original)
            try: codec.prepare_return(returned, original)
            except ValueError: controls.append('wrong_return_extent')
            else: raise ValueError('wrong return extent accepted')
            codec.abort(); returned.clear(); erase(returned)

        for args in ((1, 0, 3, 0, 0), (4, 4, 8, 3, 0), (4, 0, 4, 1, 0),
                     (4, 0, 4, 0, -1), (True, 0, 4, 0, 0)):
            try: Format(*args)
            except ValueError: controls.append('bad_format')
            else: raise ValueError('invalid format accepted')

        # Numerical wrong-normalizer detector: using U-1 produces a different
        # result on an in-range exact native output, even with a loose tolerance.
        normal = Format(8, 2, 12, 5, 2)
        original = B.Tape('normalization witness', sigmag(0, 8) * 2 + '#')
        outputs = []
        for u in (2, 1):
            codec.reconfigure(Format(8, 2, 12, 5, u))
            returned = C(); native_emit(returned, (96, -96), 12)
            codec.prepare_input(original); outputs.append(codec.prepare_return(returned, original).inspect())
            codec.abort(); returned.clear(); erase(returned)
        need(outputs[0] != outputs[1], 'unpaid normalizer fault escaped exact oracle')
        controls.append('omitted_normalizer_detected')

        # Complete source-bound transport ownership, using an explicit identity
        # native protocol test double. This is not a numerical Core execution.
        class IdentityProtocol:
            def __init__(self):
                self.output = C(); self.pending = False
            def run(self, payload):
                while payload.read() != blank:
                    self.output.append(payload.read()); payload.step(1)
                payload.rewind(); self.output.rewind(); self.pending = True
                return self.output
            def consume(self):
                need(self.pending, 'protocol protected return')
                self.output.clear(); self.pending = False

        fmt = Format(6, 3, 11, 6, 1); codec.reconfigure(fmt)
        pair = sigmag(-5, 6) + sigmag(7, 6) + '#'
        transport = B.Program(pair * 16, '&@0#000;', '01000', '00001', '00000')
        identity = IdentityProtocol(); bound = BoundCore(codec, identity, ())
        try: bound.run(transport)
        except ValueError: controls.append('early_core')
        else: raise ValueError('early Core accepted')
        transport.gather(); transport.sort(transport.saved)
        saved = transport.saved.inspect(); before_backing = backing(codec)
        with forbid_observers(B, C): bound.run(transport)
        need(transport.phase == 'core' and transport.saved.inspect() == saved,
             'saved originals or phase changed')
        need(transport.source.inspect() == (sigmag(-2, 6) + sigmag(3, 6) + '#') * 16,
             'complete normalization and current-source commit')
        need(not identity.pending, 'callee protected return consumed')
        need(backing(codec) >= before_backing, 'erasure removed historical backing')
        try: bound.run(transport)
        except ValueError: controls.append('second_core')
        else: raise ValueError('second Core accepted')

        class NativeFailure(IdentityProtocol):
            def run(self, payload):
                self.output.append(payload.read())
                self.output.rewind(); self.pending = True
                raise ValueError('deliberate partial native failure')

        class ReturnFailure(IdentityProtocol):
            def run(self, payload):
                self.output.append(0)
                self.output.rewind(); self.pending = True
                return self.output

        for name, protocol in (('partial_native_failure', NativeFailure),
                               ('malformed_native_return', ReturnFailure)):
            transport = B.Program(pair * 16, '&@0#000;', '01000', '00001', '00000')
            transport.gather(); transport.sort(transport.saved)
            before_source, before_saved = transport.source.inspect(), transport.saved.inspect()
            child = protocol(); bound = BoundCore(codec, child, ())
            try:
                with forbid_observers(B, C):
                    bound.run(transport)
            except ValueError:
                controls.append(name)
            else:
                raise ValueError('partial transaction failure accepted')
            need(transport.source.inspect() == before_source
                 and transport.saved.inspect() == before_saved and transport.phase == 'saved',
                 'failed native transaction changed original or sparse pre-copy')
            need(not child.pending and not codec.active and not codec.pending
                 and not codec.input_armed, 'failed transaction retained pending ownership')
            need(all(t.inspect() == '' for t in codec.work)
                 and all(x == blank for x in codec.input.cells), 'failed transaction retained payload')

        cost_rows = []
        for n in (1, 2, 4, 8, 16, 32, 64):
            fmt = Format(27, 24, 80, 72, 3); codec.reconfigure(fmt)
            original = B.Tape('linear scan field', (sigmag(-7, 27) + sigmag(11, 27) + '#') * n)
            returned = C(); native_emit(returned, [(-7 << 48), (11 << 48)] * n, 80)
            start = bill(codec)
            def borrowed_bill():
                return sum(original.actions[k] for k in ('read', 'write', 'move')) + sum(
                    getattr(returned.meter, k) for k in ('reads', 'writes', 'moves'))
            borrowed_start = borrowed_bill()
            codec.prepare_input(original); codec.prepare_return(returned, original)
            codec.commit(SimpleNamespace(source=original, phase='saved'))
            actions = bill(codec) - start
            borrowed_actions = borrowed_bill() - borrowed_start
            allowance = 300 * (n + 1) * (fmt.native_bits + fmt.external_bits + fmt.drop + fmt.lift + 1)
            need(actions + borrowed_actions <= allowance, 'complete bridge linear primitive allowance')
            cost_rows.append({'records': n, 'bridge_owned_primitive_actions': actions,
                              'borrowed_port_primitive_actions': borrowed_actions,
                              'complete_bridge_primitive_actions': actions + borrowed_actions,
                              'conservative_loop_allowance': allowance, 'retained_cells': backing(codec)})
            returned.clear(); erase(returned)
        old_backing = backing(codec)
        codec.reconfigure(Format(2, 0, 3, 0, 0))
        need(backing(codec) >= old_backing, 'shorter configuration forgot old backing')
        need(tuple(map(id, (*codec.templates, *codec.work, codec.input))) == ids,
             'reconfiguration allocated roles')

        receipt = {'status': 'PASS_CORE_HALO_SOURCE_CODEC',
                   'input_and_return_cases': rows, 'separate_native_return_cases': return_cases,
                   'control_categories': sorted(set(controls)), 'rejected_or_detected_controls': len(controls),
                   'exact_output_sha256': digest.hexdigest(), 'cost_rows': cost_rows,
                   'owned_roles': len(ids), 'retained_backing_after_short_reconfigure': backing(codec),
                   'scope': 'actual retained B and C tape models; identity protocol is an explicit test double; no full physical Core invocation or all-size admission from finite tests',
                   'public_core_commit': authenticate()['core_public_commit'],
                   'no_new_kappa': True}
        print(json.dumps(receipt, sort_keys=True))
        print('PASS_CORE_HALO_SOURCE_CODEC')


if __name__ == '__main__':
    main()
