"""Finite corroboration on unchanged PhysicalArena and numerical consumers.

These are component/geometry executions, not a complete GL64 payload run.
Checker decoding is confined to evidence and never supplies runtime answers.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch
from margin_sources import need


def value(word):
    from words import LEFT, RIGHT
    need(word.head == 1 and word.cells[0] == LEFT, 'restored checker word')
    digits = list(word.cells[1:])
    end = digits.index(RIGHT)
    need(all(x in (0, 1) for x in digits[:end]), 'checker binary extent')
    return sum(bit << i for i, bit in enumerate(digits[:end]))


def extent(word):
    from words import RIGHT
    return list(word.cells[1:]).index(RIGHT)


def count_value(count):
    from words import RIGHT
    count.rewind()
    result, bit = 0, 0
    while count.read() != RIGHT:
        result |= count.read() << bit
        bit += 1
        count.step(1)
    count.rewind()
    return result


def bank(maximum, capacity=96):
    from cardinal_counts import Count
    from physical_words import PhysicalArena
    encoded = Count.literal(maximum)
    arena = PhysicalArena(capacity)
    arena.prepare(encoded)
    need(extent(arena.template) == maximum.bit_length()+1, 'actual minimal template')
    need(not hasattr(arena, 'bits'), 'no decoded width in physical bank')
    encoded.close()
    return arena


def dispose(arena):
    for slot in tuple(arena.live):
        arena.free(arena.words[slot])
    arena.erase_owned()


def rejected(action, text):
    try:
        action()
    except ValueError as exc:
        need(text in str(exc), 'intended width/domain rejection: ' + str(exc))
    else:
        raise ValueError('expected rejection: ' + text)


def index_cases():
    from numeric import Geometry
    from plan import Plan
    from words import Unsigned
    roots = sorted({64, 65, 127, 128, 129, 191, 255, 256, 257, 1023, 1024,
                    2**20-1, 2**20, 2**20+1, 2**600-1, 2**600, 2**600+1})
    digest, cases, points = sha256(), 0, 0
    for n0 in roots:
        arena = bank(n0)
        raw = Unsigned(arena)
        for n in sorted({64, n0}):
            f = n//64
            size, cols = arena.literal(n), arena.literal(f)
            generation = arena.literal(n0-n)
            page = Geometry(Plan(64, 42, True, ()), arena, cols, generation, 0, None)
            total = raw.times_small(size, 2)
            need(value(total) == 2*n, 'complete one-past body endpoint')
            expected_depth = page.plus(generation, page.one)
            need(value(expected_depth) == n0-n+1, 'admissible maximum depth extension')
            for row in (0, 1, 63, 64, 65, 126, 127):
                for j in sorted({0, f-1}):
                    column = arena.literal(j)
                    point = page.point(row, column)
                    expected = row*f+(j if row<64 else f-1-j)
                    need(value(point) == expected and expected < 128*f, 'actual compact point')
                    digest.update(str((n0, n, row, j, expected)).encode())
                    arena.free_many(column, point)
                    points += 1
            for denominator in (2, 64, f):
                divisor = arena.literal(denominator)
                quotient, remainder = raw.divmod(total, divisor)
                need((value(quotient), value(remainder)) == divmod(2*n, denominator),
                     'top-bit numerator with genuine high-zero divisor')
                arena.free_many(divisor, quotient, remainder)
            terminal = arena.literal(f-1)
            raw.increment_in_place(terminal)
            need(value(terminal) == f, 'last column increment')
            arena.free_many(total, expected_depth, terminal)
            page.close()
            arena.free_many(size, cols, generation)
            need(not arena.live, 'geometry component owns no remaining words')
            cases += 1
        dispose(arena)
    return dict(roots=[str(n) for n in roots], cases=cases, points=points,
                includes_601_bit_root=True, digest=digest.hexdigest())


def projected_chunks():
    from cardinal_counts import Count
    from layout import Layout
    from numeric import Geometry
    from plan import Plan
    from words import Ring
    receipts = []
    for n in (64, 65, 127, 128, 191):
        indices, residues = bank(n), bank(3)
        modulus = residues.literal(3)
        ring = Ring(modulus)
        size, columns, depth = indices.literal(n), indices.literal(n//64), indices.zero()
        page = Geometry(Plan(64, 42, True, ()), indices, columns, depth, 0, None)
        before, gap, suffix = (Count.literal(x) for x in (2, 5, 3))
        layout = Layout(page, size, ring, 3, before, gap, suffix)
        f, delta = n//64, n%64
        cases = [(0, 86*f, 42*f), (63*f, 64*f, f), (126*f, 127*f, f)]
        if f//2:
            cases.extend([(63*f, 64*f-f//2, f//2), (127*f, 128*f-f//2, f//2)])
        for first, second, width in cases:
            args = [indices.literal(v) for v in (first, second, width)]
            actual = layout.child_extents(*args, before=before)
            a = first + (2*delta if first>=64*f else 0)
            b = second + (2*delta if second>=64*f else 0)
            expected = [2*3**a, 3**(b-a-width), 3*3**(2*n-b-width)]
            region = 0 if a>=n else 2 if b+width<=n else 1
            expected[region] *= 5
            need([count_value(v) for v in actual] == expected, 'actual original-gap projected Counts')
            for v in actual:
                v.close()
            indices.free_many(*args)
            receipts.append([n, first, second, width, region])
        layout.close()
        page.close()
        indices.free_many(size, columns, depth)
        ring.close()
        residues.free(modulus)
        for v in (before, gap, suffix):
            v.close()
        need(not indices.live and not residues.live, 'projected chunk word cleanup')
        dispose(indices)
        dispose(residues)
    return dict(cases=receipts, complete_cardinality_execution=True)


def route_cursor():
    from cardinal_counts import Count
    from directory import Context
    from records import Tape
    from routes import Route
    import routes
    from words import Ring, BLANK
    receipts = []
    for q in (3, 5):
        arena = bank(q*q, 160)
        modulus = arena.literal(q*q)
        ring = Ring(modulus)
        context = Context(ring, SimpleNamespace(q=q, dimension=1))
        route = Route(q, 1, ((1,),), ((q-1,),), ((Fraction(-1),),))
        source, fibre = Tape(), Count.literal(3)
        bits = [(j*5+j//2)&1 for j in range(3*q)]
        for bit in bits:
            source.append(bit)
        source.rewind()
        masks = []
        original = routes.partition
        def observe(source, coordinate, cursor, context, fibre, factory):
            masks.append(value(cursor))
            return original(source, coordinate, cursor, context, fibre, factory)
        with patch.object(routes, 'partition', observe):
            out = routes.route_cube(source, route, context, fibre)
        expected = [b for j in reversed(range(q)) for b in bits[3*j:3*j+3]]
        observed = []
        while out.read() != BLANK:
            observed.append(out.read())
            out.step(1)
        out.rewind()
        need(observed == expected, 'nonidentity complete reduced high route')
        need(masks == [1<<j for j in range((q*q).bit_length()+1)],
             'actual route reaches and stops at top physical mask')
        need(masks[-1] > q*q, 'terminal cursor is not a canonical residue')
        receipts.append(dict(q=q, dimension=1, records=q, masks=masks,
                             output_sha256=sha256(bytes(observed)).hexdigest()))
        out.clear()
        source.clear()
        fibre.close()
        context.close()
        ring.close()
        arena.free(modulus)
        need(not arena.live, 'reduced route numerical cleanup')
        dispose(arena)
    return dict(scope='complete dimension1 routes on the unchanged generic helper; not GL64', cases=receipts)


def parking():
    from bank_codec import BankParking
    receipts = []
    for n0, m in ((64, 3), (127, 9), (2**600+1, 25)):
        residue, index = bank(m, 12), bank(n0, 12)
        rwords = [residue.literal(x) for x in (m, m-1, 1<<m.bit_length())]
        iwords = [index.literal(x) for x in (n0, 2*n0, n0-63)]
        original = [(w, tuple(w.cells), w.head) for w in (*rwords, *iwords)]
        codec = BankParking(residue, index)
        codec.park()
        need(not residue.live and not index.live, 'actual physical parent parked')
        for arena in (residue, index):
            scratch = [arena.literal(i) for i in range(5)]
            for i in (1, 3, 0, 4, 2):
                arena.free(scratch[i])
        codec.restore()
        for word, cells, head in original:
            need(word is word.arena.words[word.slot] and tuple(word.cells) == cells and word.head == head,
                 'original full-width Word and slot restored')
        receipts.append(dict(root=str(n0), modulus=m, index_bits=n0.bit_length()+1,
                             residue_bits=m.bit_length()+1, restored_words=len(original)))
        dispose(residue)
        dispose(index)
    return receipts


def generated_records():
    """Actual unit_program/children.extend on one compiled selected rank42.

    Raw fields are canonical fixture records, not a complete GL64 directory.
    Both the producer and original incoming-program parser run unchanged.
    """
    from catalogue import Catalogue, Specifications
    from children import extend
    from controller import Callback
    from macro_binding import SelectedBinding
    from ordinary import unit_program
    from plan import Request
    from records import Fields
    from words import Ring
    import oracle
    catalogue = Catalogue(3)
    binding = SelectedBinding(Specifications(catalogue))
    identifier = next(i for i, request in enumerate(catalogue.requests)
                      if request.kind == 'IDLE' and request.base.rank == 42)
    template = catalogue.template_for(identifier, False)
    low = tuple(map(tuple, oracle.inverse(oracle.reduce_rational(template.preparation, 3), 3)))
    definition = binding.residual(identifier, False, low, 0)
    need(definition.plan.good and definition.plan.rank == 42, 'actual selected good rank42 source')
    receipts = []
    for n0, levels in ((64, 1), (256, 3), (2**20+1, 3), (2**600+1, 2)):
        indices, residues = bank(n0, 96), bank(3, 96)
        modulus = residues.literal(3)
        ring = Ring(modulus)
        root_size, root_depth = indices.literal(n0), indices.zero()
        program = unit_program(indices, ring, root_size, root_depth, binding.codes.bits)
        width = n0
        for level in range(levels):
            need(width>=64, 'fixture reaches internal parent')
            fields = Fields.fixture(indices, residues,
                                    [(definition.code, [[0]*64 for _ in range(64)])]*(level+1),
                                    binding.codes.bits)
            original_fields = tuple(fields.tape.cells)
            original_program = tuple(program.tape.cells)
            frame = Callback(ring, indices, program, fields, binding.specifications,
                             definition.code, allow_fallback=True)
            zero = indices.zero()
            child = extend(frame, Request('child', zero, child_kind='good'))
            frame.close()
            indices.free(zero)
            width = 42*(width//64)
            # This is the original incoming parser: no new current field yet.
            incoming = Callback(ring, indices, child, fields, binding.specifications,
                                definition.code, allow_fallback=True, leaf=True)
            need(value(incoming.root_size) == n0 and value(incoming.depth) == level+1
                 and value(incoming.final_size) == width,
                 'actual emitted child width/depth and preserved root')
            need(extent(incoming.root_size) == n0.bit_length()+1,
                 'descendants retain minimal original template')
            incoming.close()
            need(tuple(fields.tape.cells) == original_fields and fields.tape.head == 1
                 and tuple(program.tape.cells) == original_program and program.tape.head == 1,
                 'actual child producer preserves borrowed full records')
            receipts.append(dict(root=str(n0), depth=level+1, width=str(width),
                                 program_sha256=sha256(bytes(child.tape.cells)).hexdigest()))
            program.tape.clear()
            fields.tape.clear()
            program = child
        program.tape.clear()
        indices.free_many(root_size, root_depth)
        ring.close()
        residues.free(modulus)
        need(not indices.live and not residues.live, 'generated-record numerical cleanup')
        dispose(indices)
        dispose(residues)
    return dict(source_identifier=identifier, rank=42, q=3, cases=receipts,
                scope='actual selected unit ROOT, recursive STEP producer and incoming parser; no payload or full high cube')


def guards():
    from words import Unsigned
    labels = []
    short = bank(32)
    x = short.literal(64)
    rejected(lambda: Unsigned(short).times_small(x, 2), 'index multiplication margin')
    labels.append('omit_extra_root_bit')
    dispose(short)
    normal = bank(64)
    a, d = normal.literal(127), normal.literal(128)
    rejected(lambda: Unsigned(normal).divmod(a, d), 'binary divisor has the high-bit margin')
    labels.append('top_bit_divisor')
    dispose(normal)
    route = bank(9)
    top = route.literal(16)
    rejected(lambda: Unsigned(route).shift_add_bit(top, 0), 'reserved high-bit margin')
    labels.append('shift_terminal_route_mask')
    dispose(route)
    normal = bank(64)
    full = normal.literal(255)
    rejected(lambda: Unsigned(normal).increment_in_place(full), 'ripple increment has space')
    labels.append('unbounded_increment')
    dispose(normal)
    from cardinal_counts import Count
    from layout import Layout
    from numeric import Geometry
    from plan import Plan
    from words import Ring
    indices, residues = bank(65), bank(3)
    modulus = residues.literal(3)
    ring = Ring(modulus)
    size, columns, depth = indices.literal(65), indices.literal(1), indices.zero()
    page = Geometry(Plan(64, 42, True, ()), indices, columns, depth, 0, None)
    counts = [Count.literal(x) for x in (1, 2, 3)]
    layout = Layout(page, size, ring, 3, *counts)
    invalid = [indices.literal(x) for x in (63, 126, 2)]
    rejected(lambda: layout.child_extents(*invalid, before=counts[0]),
             'each recursive child chunk is physically contiguous')
    labels.append('chunk_crosses_original_gap')
    indices.free_many(*invalid)
    layout.close()
    page.close()
    indices.free_many(size, columns, depth)
    for count in counts:
        count.close()
    ring.close()
    residues.free(modulus)
    dispose(indices)
    dispose(residues)
    return dict(rejections=labels, cleanup='checker disposal after rejection; no transactional claim')


def run():
    return dict(indices=index_cases(), projected=projected_chunks(),
                route=route_cursor(), parking=parking(), records=generated_records(), controls=guards())
