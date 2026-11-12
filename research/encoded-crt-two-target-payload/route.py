"""Tape adapter for a two-target encoded CRT root. Apache-2.0."""

HEADER_NAMES = ('h', 'modulus', 'selected_layer', 'offsets')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def open_root(iterator):
    """Find the root by the encoded node cursor and the lease's suffix flag."""
    meters = []
    while (lease := iterator.next()) is not None:
        meters.append(lease.actual.context.arena.meter)
        if iterator.counters['axis'].read() == iterator.r.STEP and lease.actual.last:
            return lease, meters
        lease.close()
    raise ValueError('encoded root lease missing')


def emit_axis(m, iterator, guide, header, width, combined):
    """Consume the next physical right record and emit its width and modulus."""
    leaf = m.route
    w, r, source = iterator.w, iterator.r, iterator.source
    leaf.zero_header(header['h'], guide, w)
    leaf.zero_header(header['selected_layer'], guide, w)
    need(source.read() == r.ROOT, 'ordered right source record')
    source.step(1)
    need(source.read() == w.ONE, 'positive right source width')
    width.emit('L')
    while source.read() == w.ONE:
        width.emit('1')
        combined.emit('1')
        need(not leaf.increment(header['h']), 'source width fits precision guide')
        source.step(1)
    need(source.read() == r.WORD_END, 'right source width delimiter')
    source.step(1)
    leaf.end_word(width)

    modulus = header['modulus']
    modulus.emit('L')
    width.step(1)
    while width.read() == '1':
        bit = source.read()
        need(bit in (w.ZERO, w.ONE) and guide.read() == w.ONE,
             'right modulus fits precision guide')
        modulus.emit('1' if bit == w.ONE else '0')
        source.step(1)
        guide.step(1)
        width.step(1)
    need(width.read() == 'R' and source.read() == r.WORD_END, 'right modulus delimiter')
    width.rewind()
    source.step(1)
    while guide.read() == w.ONE:
        modulus.emit('0')
        guide.step(1)
    need(guide.read() == w.BLANK, 'modulus padding delimiter')
    leaf.end_word(modulus)
    guide.rewind()

    width.step(1)
    while width.read() == '1':
        need(source.read() in (w.ZERO, w.ONE), 'right coordinate bit')
        source.step(1)
        width.step(1)
    need(width.read() == 'R' and source.read() == r.RECORD_END,
         'complete padded right source record')
    width.rewind()
    source.step(1)


def emit_root_headers(m, iterator, lease, headers, widths, combined):
    """Copy ordered headers, consuming both fields of each live result record."""
    w, r, source = iterator.w, iterator.r, iterator.source
    axis, half = iterator.counters['axis'], iterator.counters['half']
    guide, result = lease.actual.guide, lease.actual.result['stream']
    need(axis.read() == r.STEP and lease.actual.last, 'complete root interval')
    while half.read() == w.ONE:
        iterator._record()
        half.step(1)
    need(half.read() == w.RIGHT, 'complete left half')
    half.rewind()

    combined.emit('L')
    for header, width in zip(headers, widths, strict=True):
        need(half.read() == w.ONE, 'two encoded right targets')
        emit_axis(m, iterator, guide, header, width, combined)
        need(result.read() == r.ROOT, 'ordered right result record')
        result.step(1)
        m.join.copy_numeric_field(result, header['offsets'], guide, w, r.WORD_END, '|')
        m.join.skip_numeric_field(result, guide, w, r.WORD_END)
        need(result.read() == r.RECORD_END, 'both right result fields consumed')
        result.step(1)
        half.step(1)
    need(half.read() == w.RIGHT and source.read() == w.RIGHT and result.read() == w.RIGHT,
         'all right source and result records consumed')
    half.rewind()
    source.rewind()
    result.rewind()
    m.route.end_word(combined)


def initialize_index(leaf, index, width):
    index.emit('L')
    width.step(1)
    while width.read() == '1':
        index.emit('0')
        width.step(1)
    need(width.read() == 'R', 'complete encoded position width')
    width.rewind()
    leaf.end_word(index)


def skip_key_field(record, width):
    width.step(1)
    while width.read() == '1':
        need(record.matches('0') or record.matches('1'), 'untouched key field bit')
        record.move_word(1)
        width.step(1)
    need(width.read() == 'R', 'complete untouched key field')
    width.rewind()


def rekey_axis(m, record, layers, widths, indices, scratch, target, reverse):
    """Assign this target's field using current physical positions as inputs."""
    leaf = m.route
    address, countdown, row = scratch
    slow, fast = indices
    for index, width in zip(indices, widths, strict=True):
        initialize_index(leaf, index, width)
    need(record.matches('<'), 'physical payload frame origin')
    record.move_word(1)
    while True:
        record.pass_payload()
        if target == 1:
            skip_key_field(record, widths[0])
        leaf.copy_bits(indices[target], address)
        leaf.route_address(m.join, layers, widths[target], address, countdown, row, reverse)
        record.rekey(address)
        address.erase()
        if target == 0:
            skip_key_field(record, widths[1])
        if leaf.increment(fast) and leaf.increment(slow):
            break
    need(record.matches('>'), 'payload occupies precisely the padded right rectangle')
    while not record.matches('<'):
        record.move_word(-1)
    for index in indices:
        index.erase()
