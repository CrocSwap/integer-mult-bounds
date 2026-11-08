"""Independent literal union parser, lockstep layout and lifecycle checks.

Raw-bit fixtures/permutations are external observers. Executed helpers use
sealed constructors and disabled host decoding. Prepared for @CubeJerry with
separate source-aware OpenAI AI verification. Apache-2.0.
"""


def run(engine):
    from cardinal_counts import Count
    from check_support import no_decode
    from records import Tape
    from session import initialize_marker, erase_marker, sealed_constructors
    from words import BLANK, need
    import window_tapes as T

    def raw(bits):
        tape = Tape()
        for digit in bits: tape.append(int(digit))
        tape.rewind()
        return tape

    def word(value, width):
        need(-(1 << (width-1)) <= value < 1 << (width-1), 'review signed range')
        return tuple((value >> bit) & 1 for bit in range(width))

    def visible(tape):
        data = tuple(tape.cells[1:])
        return data[:data.index(BLANK)] if BLANK in data else data

    def snapshot(tapes):
        return tuple((bytes(t.cells), t.head) for t in tapes)

    def header(x, y):
        exposed = (0, 1, 4, 5, 6, 7)
        point = (x, y)
        flags = tuple(int(v in exposed) for v in point)
        ranks = tuple(exposed.index(v) if flag else 0 for v, flag in zip(point, flags))
        return tuple(map(int, '01'+''.join(format(v, '03b') for v in point)
                            +''.join(map(str, flags))
                            +''.join(format(v, '03b') for v in ranks)
                            +format(sum(flags), '02b')+'01'))

    def empty_owner():
        engine.idle()
        need(not engine.pool.live and engine.closed and not engine.pending,
             'independent idle union owner')
        need(all(t.head == 1 and all(x == BLANK for x in t.cells)
                 for t in engine.forbidden()), 'independent complete owned erasure')

    def helper(call):
        for tape in engine.pool.tapes: initialize_marker(tape)
        try:
            with no_decode(), sealed_constructors(), engine.scope.installed():
                call(); engine.pool.empty()
        finally:
            engine.pool.empty()
            for tape in engine.pool.tapes: erase_marker(tape)

    empty_owner()
    counts = tuple(Count.literal(v) for v in (2,3,2,1,0,6,4,4,8,2,8))
    axes,h,tb,axis,round_index,length,selected,block,width,precision,rows = counts
    e = (0,1,4,5,6,7)
    pairs = tuple(((-128 if i == 0 else (i*17)%255-127), (i*23)%255-127)
                  for i in range(12))
    headers = tuple(header(x,y) for x in (2,3) for y in e)
    bits = tuple(v for hd,pair in zip(headers,pairs) for v in (*hd,*word(pair[0],8),*word(pair[1],8)))
    source = raw(bits); etable = raw(v for x in e for v in format(x,'03b'))
    mask = raw((1,0,0,1,1,1))
    archive, real, imaginary = Tape(), Tape(), Tape()
    extra = [source,etable,mask,archive,real,imaginary]
    controls = []
    try:
        descriptors = tuple(c.tape for c in counts)
        before = snapshot((etable,mask,*descriptors))
        for which in range(2):
            helper(lambda:T.line(source,archive,real,imaginary,etable,mask,
                       axes,h,tb,axis,round_index,length,selected,width,engine.pool))
            need(visible(real) == tuple(v for pair in pairs[which*6:which*6+6] for v in word(pair[0],8))
                 and visible(imaginary) == tuple(v for pair in pairs[which*6:which*6+6] for v in word(pair[1],8)),
                 'independent two complex columns across prefix boundary')
            real.clear(); imaginary.clear()
        need(source.read() == BLANK and visible(archive) == bits, 'immutable complete raw archive')
        need(snapshot((etable,mask,*descriptors)) == before, 'borrowed catalogues and counts')
        controls.extend(('two literal complete lines across prefixes2/3',
                         'negative minimum signed payload', 'raw headers archived exactly'))
        source.rewind(); archive.clear()
        columns = tuple(tuple((c*53+r*17)%255-127 for r in range(8)) for c in range(4))
        packed = raw(v for col in columns for z in col for v in word(z,8))
        matrix, returned = Tape(), Tape(); extra.extend((packed,matrix,returned))
        saved = snapshot((packed,*descriptors))
        helper(lambda:T.transpose(packed,matrix,rows,block,width,engine.pool))
        expected = tuple(v for r in range(8) for c in range(4) for v in word(columns[c][r],8))
        need(visible(matrix) == expected, 'independent direct row-major permutation')
        helper(lambda:T.transpose(matrix,returned,rows,block,width,engine.pool,inverse=True))
        need(visible(returned) == visible(packed) and snapshot((packed,*descriptors)) == saved,
             'literal inverse transpose and borrowed preservation')
        controls.extend(('B4 forward lockstep transpose', 'B4 inverse lockstep transpose'))
        # Empty numerical pages suffice: each rejection precedes child work.
        pages = tuple(Tape() for _ in range(8)); extra.extend(pages)
        ports = (source,etable,mask,*pages,*(c.tape for c in counts[:10]))

        def call(src=source):
            return engine.run(src,etable,mask,pages[:4],pages[4:],*counts[:10])

        def rejects(function, message):
            saved = snapshot(ports)
            try:
                with no_decode(): function()
            except ValueError as error:
                need(message in str(error), 'specific independent rejection: '+str(error))
            else: raise ValueError('missing union rejection: '+message)
            need(snapshot(ports) == saved, 'rejection preserves external bodies and entry heads')
            empty_owner(); controls.append(message)

        rejects(lambda:call(etable),'external distinct union-window sources')
        private = engine.forbidden()[-1]
        need(private not in engine.pool.tapes, 'deep descendant alias fixture')
        rejects(lambda:call(private),'external distinct union-window sources')
        source.step(1)
        rejects(call,'canonical fast-boundary borrowed origin')
        source.rewind()
        # Incorrect final ordinal exercises partially allocated parser state.
        bad = list(bits)
        header_width = len(headers[0]); record_width = header_width+16
        ordinal_axis1 = 2+2*3+2+3
        bad[5*record_width+ordinal_axis1+2] ^= 1
        source.clear()
        for digit in bad: source.append(digit)
        source.rewind()
        rejects(call,'consecutive complete union E-line ordinals')
        source.clear()
        for digit in bits[:-1]: source.append(digit)
        source.rewind()
        rejects(call,'complete')
        initialize_marker(engine.output);engine.output.append(1);engine.pending=True
        saved = snapshot(ports)
        try:
            with no_decode():call()
        except ValueError as error:
            need('consume prior union-window return' in str(error), 'explicit moved pending guard')
        else:raise ValueError('pending union return accepted at blank terminator')
        need(snapshot(ports) == saved and engine.pending, 'pending rejection preserves ownership')
        engine.consume();empty_owner();controls.append('moved pending return')
        return dict(controls=controls, literal_lines=2, prefix_values=[2,3],
                    transpose_rows=8, transpose_columns=4, fixed_owned_roles=len(engine.forbidden()))
    finally:
        for tape in extra: tape.clear(); erase_marker(tape)
        for count in counts: count.close(); erase_marker(count.tape)
