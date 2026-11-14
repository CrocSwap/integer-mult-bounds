"""Join an encoded CRT leaf to the existing physical payload mover. Apache-2.0."""

BITS = ('0', '1')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def end_word(tape):
    tape.write('R')
    tape.rewind()


def increment(tape):
    """Increment a framed little-endian binary word, returning its carry."""
    tape.step(1)
    carry = True
    while tape.read() != 'R':
        bit = tape.read()
        need(bit in BITS, 'binary counter bit')
        if carry:
            tape.write('0' if bit == '1' else '1')
            carry = bit == '1'
        tape.step(1)
    tape.rewind()
    return carry


def copy_bits(source, target):
    target.emit('L')
    source.step(1)
    while source.read() != 'R':
        bit = source.read()
        need(bit in BITS, 'framed binary word')
        target.emit(bit)
        source.step(1)
    source.rewind()
    end_word(target)


def zero_header(target, guide, words):
    target.emit('L')
    while guide.read() == words.ONE:
        target.emit('0')
        guide.step(1)
    need(guide.read() == words.BLANK, 'precision guide terminator')
    guide.rewind()
    end_word(target)


def selected_leaf(iterator, lease):
    half, axis = iterator.counters['half'], iterator.counters['axis']
    words = iterator.w
    need(half.read() == words.ONE, 'nonempty current half')
    half.step(1)
    one = half.read() == words.RIGHT
    half.rewind()
    return one and lease.actual.last and axis.read() != iterator.r.STEP


def emit_headers(join, iterator, lease, headers, width):
    words, records, source = iterator.w, iterator.r, iterator.source
    axis = iterator.counters['axis']
    guide = lease.actual.guide
    result = lease.actual.result['stream']
    zero_header(headers['h'], guide, words)
    zero_header(headers['selected_layer'], guide, words)
    while axis.read() != records.STEP:
        need(axis.read() == words.ONE, 'encoded nonroot prefix')
        iterator._record()
        axis.step(1)
    iterator._record()  # The admitted leaf has exactly one left record.

    need(source.read() == records.ROOT, 'right axis record')
    source.step(1)
    width.emit('L')
    while source.read() == words.ONE:
        width.emit('1')
        need(not increment(headers['h']), 'encoded width fits precision guide')
        source.step(1)
    need(source.read() == records.WORD_END, 'right width delimiter')
    source.step(1)
    end_word(width)

    modulus = headers['modulus']
    modulus.emit('L')
    width.step(1)
    while width.read() == '1':
        bit = source.read()
        need(bit in (words.ZERO, words.ONE) and guide.read() == words.ONE,
             'right modulus fits precision guide')
        modulus.emit('1' if bit == words.ONE else '0')
        source.step(1)
        guide.step(1)
        width.step(1)
    need(width.read() == 'R' and source.read() == records.WORD_END,
         'right modulus delimiter')
    width.rewind()
    source.step(1)
    while guide.read() == words.ONE:
        modulus.emit('0')
        guide.step(1)
    need(guide.read() == words.BLANK, 'modulus padding terminator')
    end_word(modulus)
    guide.rewind()

    width.step(1)
    while width.read() == '1':
        need(source.read() in (words.ZERO, words.ONE), 'right coordinate bit')
        width.step(1)
        source.step(1)
    need(width.read() == 'R' and source.read() == records.RECORD_END,
         'right coordinate delimiter')
    source.step(1)
    need(source.read() == words.RIGHT, 'selected right axis is last')
    source.rewind()
    axis.rewind()
    width.rewind()

    need(result.read() == records.ROOT, 'actual offset record')
    result.step(1)
    join.copy_numeric_field(result, headers['offsets'], guide, words, records.WORD_END, '|')
    result.rewind()


def toggle_target(width, address, switch):
    # The physical mark records the current target. Both counters are scanned
    # by their symbols, and the width head returns to the marked bit.
    need(width.read() == '1', 'target is a width cell')
    width.write('|')
    width.rewind()
    width.step(1)
    address.step(1)
    while width.read() == '1':
        width.step(1)
        address.step(1)
    bit = address.read()
    need(width.read() == '|' and bit in BITS and switch in BITS, 'target bit')
    if switch == '1':
        address.write('1' if bit == '0' else '0')
    width.write('1')
    address.rewind()


def next_target(width, ascending):
    width.step(1 if ascending else -1)
    if ascending and width.read() == 'R':
        width.step(-1)
        width.step(-1)
        ascending = False
    need(width.read() == '1', 'more layers than encoded target positions')
    return ascending


def previous_delimiter(layers):
    layers.step(-1)
    while layers.read() in BITS:
        layers.step(-1)
    need(layers.read() in ('L', '|'), 'physical layer prefix')


def route_address(join, layers, width, address, countdown, row, reverse):
    """Follow all physical rows using the retained selected-row query."""
    layers.step(1)
    if reverse:
        while layers.read() != 'R':
            need(layers.read() in (*BITS, '|'), 'complete layer tape')
            layers.step(1)
        layers.step(-1)
    width.step(1)
    ascending = True
    while True:
        if reverse:
            need(layers.read() == '|', 'reverse layer end')
            previous_delimiter(layers)
            layers.step(1)
        row.emit('L')
        seen = False
        while layers.read() in BITS:
            seen = True
            row.emit(layers.read())
            layers.step(1)
        need(seen and layers.read() == '|', 'nonempty delimited ROM row')
        end_word(row)
        copy_bits(address, countdown)
        switch = join.select_row_bit(row, countdown)
        toggle_target(width, address, switch)
        row.erase()

        if reverse:
            previous_delimiter(layers)
            done = layers.read() == 'L'
        else:
            layers.step(1)
            done = layers.read() == 'R'
        if done:
            break
        ascending = next_target(width, ascending)
    if ascending:
        width.step(1)
        need(width.read() == 'R', 'missing descending ROM layers')
        width.step(-1)
    width.step(-1)
    need(width.read() == 'L', 'complete palindromic target sequence')
    layers.rewind()


class RecordTape:
    """Paid scans and writes on the retained literal radix ABI."""
    def __init__(self, binary, tape):
        self.tape = tape
        self.codes = {symbol: binary.bits(symbol) for symbol in ('<', '>', '0', '1')}

    def move_word(self, direction):
        for _ in self.codes['<']:
            self.tape.move(direction)

    def matches(self, symbol):
        equal = True
        for bit in self.codes[symbol]:
            actual = self.tape.read()
            equal = equal and actual == bit
            self.tape.move(1)
        self.move_word(-1)
        return equal

    def emit(self, symbol):
        for bit in self.codes[symbol]:
            self.tape.write(bit)
            self.tape.move(1)

    def pass_payload(self):
        # Twelve opaque bits and one tag, in the pinned 13-bit ABI.
        for _ in range(12):
            self.tape.move(1)
        need(self.tape.read() == 1, 'actual opaque payload codeword')
        self.tape.move(1)

    def rekey(self, address):
        address.step(1)
        while address.read() in BITS:
            address.step(1)
        need(address.read() == 'R', 'destination key terminator')
        address.step(-1)
        while address.read() != 'L':
            bit = address.read()
            need(bit in BITS and (self.matches('0') or self.matches('1')),
                 'one allocated key bit')
            self.emit(bit)
            address.step(-1)


def prepare_keys(join, record, layers, width, index, address, countdown, row, reverse):
    need(record.matches('<'), 'physical payload frame begins at origin')
    record.move_word(1)
    index.emit('L')
    width.step(1)
    while width.read() == '1':
        index.emit('0')
        width.step(1)
    need(width.read() == 'R', 'encoded payload width')
    width.rewind()
    end_word(index)
    while True:
        record.pass_payload()
        copy_bits(index, address)
        route_address(join, layers, width, address, countdown, row, reverse)
        record.rekey(address)
        address.erase()
        if increment(index):
            break
    need(record.matches('>'), 'payload occupies precisely the padded rectangle')
    while not record.matches('<'):
        record.move_word(-1)
    index.erase()
