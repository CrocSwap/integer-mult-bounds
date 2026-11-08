"""Independent physical mask/guard review of the full periodic caller.

Prepared for @CubeJerry by a separate source-aware OpenAI verifier.
Host integers, lists and Tape observers below belong only to verification.
The executed helpers run with sealed constructors and decoding disabled.
Apache-2.0.
"""
from types import SimpleNamespace


def run(engine, need):
    from cardinal_counts import Count
    from check_support import no_decode
    from periodic_tapes import emit
    from records import Tape
    from session import erase_marker, initialize_marker, sealed_constructors
    from words import BLANK

    def body(t):
        return bytes(t.cells)

    def snapshot(tapes):
        return tuple((body(t), t.head) for t in tapes)

    def blank_owned():
        engine.idle()
        need(engine.closed and not engine.pending and not engine.pool.live,
             'independent closed periodic owner')
        need(all(t.head == 1 and all(x == BLANK for x in t.cells)
                 for t in engine.forbidden()), 'independent all-role physical erasure')

    def words(values, width):
        t = Tape(); emit(values, t, width); t.rewind(); return t

    def mask(values):
        t = Tape()
        for value in values: t.append(value)
        t.rewind(); return t

    def decode(t, count, width):
        values = []
        for _ in range(count):
            value = 0
            for i in range(width):
                digit = t.read(); need(digit in (0, 1), 'review payload digit')
                value |= digit << i; t.step(1)
            values.append(value - (1 << width) if value >> (width - 1) else value)
        need(t.read() == BLANK, 'review complete payload')
        t.rewind(); return tuple(values)

    controls = []
    blank_owned()
    counts = tuple(Count.literal(v) for v in (4, 7, 2, 1, 1, 6, 2, 6, 2))
    extra = []
    raw = ((-8, 3), (-3, -1), (0, 4), (7, -7), (1, 0), (-2, 2), (3, -3))
    selection = (1, 0, 1, 0, 1, 1, 0)
    chosen = tuple(i for i, flag in enumerate(selection) if flag)
    rhs = words(tuple(v for pair in raw for v in pair), counts[5]); extra.append(rhs)
    selected = mask(selection); extra.append(selected)
    real = Tape(); imag = Tape(); extra.extend((real, imag))
    try:
        before = snapshot((rhs, selected, *(c.tape for c in counts)))
        for tape in engine.pool.tapes: initialize_marker(tape)
        try:
            with no_decode(), sealed_constructors(), engine.scope.installed():
                engine.extract(rhs, selected, real, imag, counts[0], counts[1], counts[5])
                engine.pool.empty()
            need(snapshot((rhs, selected, *(c.tape for c in counts))) == before,
                 'extract preserves original mask and complex input')
            need(decode(real, 4, 6) == tuple(raw[i][0] for i in chosen)
                 and decode(imag, 4, 6) == tuple(raw[i][1] for i in chosen),
                 'direct selected-coordinate extraction')
        finally:
            engine.pool.empty()
            for tape in engine.pool.tapes: erase_marker(tape)
        controls.append('direct masked extraction')
        for tape in (real, imag): tape.clear()
        solved = ((20, 15), (-20, -15), (16, 9), (-16, -9))
        emit(tuple(x[0] for x in solved), real, counts[5]); real.rewind()
        emit(tuple(x[1] for x in solved), imag, counts[5]); imag.rewind()
        before = snapshot((rhs, selected, real, imag, *(c.tape for c in counts)))
        for tape in (*engine.pool.tapes, engine.output): initialize_marker(tape)
        try:
            with no_decode(), sealed_constructors(), engine.scope.installed():
                engine.merge(rhs, selected, real, imag, counts[1], counts[5])
                engine.pool.empty()
            engine.output.rewind()
            actual = decode(engine.output, 14, 6)
            expected = list(raw)
            for coordinate, value in zip(chosen, solved): expected[coordinate] = value
            need(actual == tuple(v for pair in expected for v in pair),
                 'direct original-coordinate merge and exact holes')
            need(snapshot((rhs, selected, real, imag, *(c.tape for c in counts))) == before,
                 'merge preserves all four borrowed bodies and origins')
            # A same-cardinality but semantically different mask is outside the
            # prepared-page contract. This oracle must detect its wrong mapping.
            wrong_positions = (0, 1, 4, 5)
            wrong = list(raw)
            for coordinate, value in zip(wrong_positions, solved): wrong[coordinate] = value
            need(actual != tuple(v for pair in wrong for v in pair),
                 'independent mask-coordinate substitution control')
        finally:
            engine.output.clear(); erase_marker(engine.output)
            engine.pool.empty()
            for tape in engine.pool.tapes: erase_marker(tape)
        controls.extend(('direct hole-preserving merge', 'same-cardinality wrong-map oracle'))
        blank_owned()

        # The malformed body is rejected in run's extraction, before child work.
        # Every other external role is distinct and has a valid Count origin.
        other = [Tape() for _ in range(12)]; extra.extend(other)
        pages = SimpleNamespace(counts=counts, target_mask=selected,
                 boundary_mask=other[0], headers=other[1], streams=tuple(other[2:8]),
                 sb=other[8], k=other[9], lower=other[10], upper=other[11])
        ports = (rhs, selected, *other, *(v.tape for v in counts))

        def rejects(call, message):
            saved = snapshot(ports)
            try:
                with no_decode(): call()
            except ValueError as error:
                need(message in str(error), 'specific physical guard: '+str(error))
            else:
                raise ValueError('missing physical rejection: '+message)
            need(snapshot(ports) == saved, 'failed call restores borrowed bodies/origins')
            blank_owned(); controls.append(message)

        alias = SimpleNamespace(**vars(pages)); alias.target_mask = rhs
        rejects(lambda: engine.run(rhs, alias), 'distinct external periodic ports')
        # Pick the last complete forbidden-role entry, which belongs to a deep
        # descendant in the public inventory, rather than an active parent lease.
        private = engine.forbidden()[-1]
        need(private not in engine.pool.tapes and private is not engine.output,
             'review uses a descendant owned role')
        rejects(lambda: engine.run(private, pages), 'distinct external periodic ports')
        rhs.step(1)
        moved = snapshot(ports)
        try:
            with no_decode(): engine.run(rhs, pages)
        except ValueError as error:
            need('canonical folded input origin' in str(error), 'moved-origin guard')
        else: raise ValueError('moved original input accepted')
        need(snapshot(ports) == moved, 'origin rejection preserves entry heads')
        rhs.rewind(); blank_owned(); controls.append('moved external input origin')

        selected.clear()
        for value in (1, 0, 1, 0, 1, 0, 0): selected.append(value)
        selected.rewind()
        rejects(lambda: engine.run(rhs, pages), 'selected mask cardinality')
        selected.clear()
        for value in selection[:-1]: selected.append(value)
        selected.rewind()
        rejects(lambda: engine.run(rhs, pages), 'complete periodic mask bit')
        selected.clear()
        for value in selection: selected.append(value)
        selected.rewind()

        # Construct precisely the public pending-output state and put the head
        # at its blank terminator. No long numerical call is claimed here.
        initialize_marker(engine.output); engine.output.append(1)
        engine.pending = True
        saved = snapshot(ports)
        try:
            with no_decode(): engine.run(rhs, pages)
        except ValueError as error:
            need('consume prior periodic output' in str(error), 'moved pending return guard')
        else: raise ValueError('pending output at blank accepted')
        need(snapshot(ports) == saved and engine.pending,
             'pending guard preserves borrowed tapes and ownership')
        engine.consume(); blank_owned(); controls.append('constructed moved pending output')
        return dict(controls=controls, target_records=7, selected_records=4,
                    identity_holes=3, fixed_owned_roles=len(engine.forbidden()))
    finally:
        for tape in extra:
            tape.clear(); erase_marker(tape)
        for count in counts:
            count.close(); erase_marker(count.tape)
