"""Finite fixture preparation and observations, separate from literal action."""
from fractions import Fraction as Q
from hashlib import sha256
import time
import pages as preparation
import independent_forward


def need(condition, message):
    if not condition:
        raise ValueError(message)


def body(tape):
    from session import borrowed_tape
    raw = bytes(borrowed_tape(tape).cells)
    end = raw.find(bytes((4,)), 1)
    if end < 0:
        end = len(raw)
    need(all(x == 4 for x in raw[end:]), 'blank observer backing suffix')
    return raw[1:end]


def snapshots(tapes):
    from session import borrowed_tape
    return tuple((bytes(borrowed_tape(t).cells), borrowed_tape(t).head) for t in tapes)


def decoded(raw, width, precision):
    need(len(raw) % width == 0, 'complete observer words')
    return [Q(sum(v << i for i, v in enumerate(raw[k:k+width]))
              -(raw[k+width-1] << width), 1 << precision)
            for k in range(0, len(raw), width)]


def erased(owner):
    need(all(t.head == 1 and all(x == 4 for x in t.cells) for t in owner.forbidden()),
         'all forward-action owned roles and retained extents erased')


def case(owner, all_tapes, matrix, *, block=4, precision=20, width=28, columns=3, controls=True):
    from cardinal_counts import Count
    from check_support import no_decode
    from records import Tape
    from ring_words import Signed, write_signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, initialize_marker, erase_marker, sealed_constructors
    from boundary_pages import prepare_pages
    from words import BLANK
    n = len(matrix)
    rhs = tuple(tuple(Q(((3*i+5*j+2) % 9)-4, 16) for j in range(columns)) for i in range(n))
    pool = ScratchPool(96)
    scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape)
        initialize_marker(tape)
    source, spectator = Tape(), Tape()
    spectator.append(1); spectator.append(0); spectator.append(1); spectator.rewind()
    metadata = tuple(Count.literal(x) for x in (n, columns, block, width, precision))
    pages = (); matrices = ()
    def meter():
        return tuple(sum(getattr(t.meter, key) for t in all_tapes) for key in ('reads', 'writes', 'moves'))
    def delta(before):
        return tuple(x-y for x, y in zip(meter(), before))
    start = time.monotonic()
    try:
        before = meter()
        with sealed_constructors(), scope.installed():
            matrices = preparation.physical_factors(matrix, block, precision, pool)
            with no_decode():
                pages = prepare_pages(*matrices, *metadata[2:], pool)
            for owner_matrix in matrices:
                owner_matrix.close()
            matrices = ()
        setup_bill = delta(before)
        expected = preparation.expected_pages(matrix, block, precision)
        need(expected == preparation.expected_pages(matrix, block, precision, pre_round=False),
             'pre-rounding exact page equality')
        need(tuple(tuple(decoded(body(t), width, precision)) for t in pages) == expected,
             'actual physical prepare_pages bytes')
        independent_pages = independent_forward.check_pages(matrix, block, precision)
        need(tuple(tuple(int(x*(1 << precision)) for x in bank) for bank in expected)
             == independent_pages, 'independent inverse-block and pre-round page oracle')
        padded = ((n+block-1)//block)*block
        packing_before = meter()
        for start_column in range(0, columns, block):
            for row in range(padded):
                for column in range(start_column, start_column+block):
                    value = rhs[row][column] if row < n and column < columns else Q()
                    integer = int(value*(1 << precision))
                    with owned(Signed(Count.literal(abs(integer)), integer < 0)) as encoded:
                        write_signed(encoded[0], source, metadata[3])
        source.rewind()
        packing_bill = delta(packing_before)
        ports = (source, *pages, *(value.tape for value in metadata), spectator)
        saved = snapshots(ports)
        before = meter(); leaves = owner.child.kernel.leaves; products = owner.child.products
        with no_decode():
            output = owner.run(source, pages, *metadata)
        raw = body(output)
        while output.read() != BLANK:
            output.step(1)
        pending = snapshots((output,))
        try:
            with no_decode():
                owner.run(source, pages, *metadata)
        except ValueError as error:
            need(str(error) == 'consume prior band-action return', 'specific protected-return guard')
        else:
            raise ValueError('pending action output overwritten')
        need(snapshots((output,)) == pending, 'pending output and moved head unchanged')
        with no_decode():
            owner.consume()
        bill = delta(before)
        need(snapshots(ports) == saved, 'all borrowed source, pages, descriptors and spectator preserved')
        erased(owner)
        value_rows = preparation.rounded_oracle(matrix, rhs, block, precision)
        packed_expected = []
        for start_column in range(0, columns, block):
            for row in range(padded):
                packed_expected.extend(value_rows[row][column] if row < n and column < columns else Q()
                                       for column in range(start_column, start_column+block))
        need(decoded(raw, width, precision) == packed_expected, 'completed rounded forward action')
        exact = preparation.multiply(matrix, rhs)
        error = max(abs(x-y) for row, ideal in zip(value_rows, exact) for x, y in zip(row, ideal))
        sparsity = max(sum(bool(x) for x in row) for row in matrix)
        radius = max(sum(map(abs, row), Q()) for row in zip(*rhs))
        admitted = max(Q(1), radius)
        allowance = Q(sparsity*admitted+6, 1 << precision)
        need(error <= allowance, 'exact original forward error allowance')
        independent = independent_forward.check_return(matrix,
            tuple(tuple(int(value*(1 << precision)) for value in row) for row in rhs),
            raw, block, precision, width, admitted)
        expected_products = 2*(2*((2*n+block-1)//block)-1)*((columns+block-1)//block)
        used_products = owner.child.products-products
        used_leaves = owner.child.kernel.leaves-leaves
        need(used_products == expected_products and used_leaves == expected_products*7**(block.bit_length()-1),
             'complete ceiling and actual leaf invoice')
        rejected = ['pending output']
        if controls:
            def reject(src, bank, meta, message):
                current = snapshots(ports)
                try:
                    with no_decode():
                        owner.run(src, bank, *meta)
                except ValueError as problem:
                    need(str(problem) == message, 'specific action guard: '+str(problem))
                else:
                    raise ValueError('accepted malformed forward call')
                need(snapshots(ports) == current, 'rejection preserves borrowed inputs')
                owner.idle(); erased(owner)
            reject(pages[0], pages, metadata, 'external distinct band-action ports')
            reject(owner.child.kernel.word.product.word.pool.tapes[-1], pages, metadata,
                   'external distinct band-action ports')
            rejected.extend(('source/page alias', 'inactive deep-owned alias'))
            with owned(Count.literal(3)) as (three,):
                reject(source, pages, (*metadata[:2], three, *metadata[3:]), 'dyadic fast-boundary block size')
            rejected.append('non-dyadic block')
            if n % block:
                location = n*block*width
                source.rewind()
                for _ in range(location): source.step(1)
                need(source.read() == 0, 'known input row pad')
                source.write(1); source.rewind()
                reject(source, pages, metadata, 'zero band-action padding')
                for _ in range(location): source.step(1)
                source.write(0); source.rewind()
                rejected.append('nonzero padded input row')
            if columns % block:
                location = columns*width
                source.rewind()
                for _ in range(location): source.step(1)
                need(source.read() == 0, 'known inactive column pad')
                source.write(1); source.rewind()
                reject(source, pages, metadata, 'zero incomplete row/RHS padding')
                for _ in range(location): source.step(1)
                source.write(0); source.rewind()
                rejected.append('nonzero inactive RHS column')
            if body(pages[1]):
                coupling = pages[1]; location = len(body(coupling))-1
                for _ in range(location): coupling.step(1)
                old = coupling.read(); coupling.write(BLANK); coupling.rewind()
                completed = owner.child.kernel.calls
                reject(source, pages, metadata, 'complete opaque binary payload')
                need(owner.child.kernel.calls == completed+1, 'failure occurs after one completed matrix child')
                for _ in range(location): coupling.step(1)
                coupling.write(old); coupling.rewind()
                rejected.append('short coupling after completed child')
            need(snapshots(ports) == saved, 'all control mutations restored')
        return dict(rows=n, columns=columns, block=block, precision=precision, width=width,
                    physical_setup_actions=setup_bill, initial_payload_packing_actions=packing_bill,
                    transaction_actions=bill, products=used_products, scalar_products=used_leaves,
                    page_bits=[len(body(t)) for t in pages], output_sha256=sha256(raw).hexdigest(),
                    output=[str(x) for x in decoded(raw, width, precision)],
                    original_error=str(error), error_allowance=str(allowance), controls=rejected,
                    independent_review=independent,
                    retained_owner_cells=sum(len(t.cells) for t in owner.forbidden()),
                    seconds=time.monotonic()-start)
    finally:
        if owner.pending: owner.consume()
        for matrix_owner in matrices: matrix_owner.close()
        for page in pages: page.clear()
        for value in metadata: value.close()
        source.clear(); spectator.clear(); pool.empty()
