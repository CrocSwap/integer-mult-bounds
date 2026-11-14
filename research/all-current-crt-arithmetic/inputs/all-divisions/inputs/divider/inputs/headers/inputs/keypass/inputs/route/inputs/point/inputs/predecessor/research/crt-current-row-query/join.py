"""Paid current-row numerical output -> existing ROM -> physical row query.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Topology is compiled data; runtime numeric values are never decoded.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Tape:
    def __init__(self, cells=None):
        self.cells = ['_'] if cells is None else cells
        self.head = 0
        self.actions = 0

    def read(self):
        self.actions += 1
        return self.cells[self.head]

    def write(self, value):
        need(value in ('_', 'L', 'R', '|', '0', '1'), 'fixed symbol')
        self.actions += 1
        self.cells[self.head] = value

    def step(self, direction):
        need(direction in (-1, 1) and self.head+direction >= 0, 'unit move')
        self.actions += 1
        self.head += direction
        if self.head == len(self.cells):
            self.cells.append('_')

    def emit(self, value):
        self.write(value)
        self.step(1)

    def rewind(self):
        while self.read() != 'L':
            self.step(-1)

    def erase(self):
        self.rewind()
        self.step(1)
        while self.read() != 'R':
            self.write('_'); self.step(1)
        self.write('_'); self.rewind(); self.write('_')


def padded_constant(target, bits, guide, w):
    target.emit('L')
    for bit in bits:  # A compile-time constant, never an encoded input integer.
        need(guide.read() == w.ONE, 'constant fits encoded width')
        target.emit('1' if bit else '0'); guide.step(1)
    while guide.read() == w.ONE:
        target.emit('0'); guide.step(1)
    need(guide.read() == w.BLANK, 'guide terminator')
    target.write('R'); target.rewind(); guide.rewind()


def copy_numeric_field(source, target, guide, w, delimiter, suffix='R'):
    target.emit('L')
    while guide.read() == w.ONE:
        bit = source.read()
        need(bit in (w.ZERO, w.ONE), 'numeric field bit')
        target.emit('1' if bit == w.ONE else '0')
        source.step(1); guide.step(1)
    need(source.read() == delimiter and guide.read() == w.BLANK, 'exact P-bit field')
    source.step(1); guide.rewind()
    if suffix == '|':
        target.emit('|')
    target.write('R'); target.rewind()


def skip_numeric_field(source, guide, w, delimiter):
    while guide.read() == w.ONE:
        need(source.read() in (w.ZERO, w.ONE), 'skipped numeric bit')
        source.step(1); guide.step(1)
    need(source.read() == delimiter and guide.read() == w.BLANK, 'skipped exact width')
    source.step(1); guide.rewind()


def select_row_bit(rom, countdown, fault=None):
    """Scan the produced row; index is an encoded countdown, not a host cursor."""
    enabled, answer, seen = True, '0', False
    rom.step(1)
    while rom.read() != 'R':
        value = rom.read(); need(value in ('0', '1'), 'ROM row bit')
        if enabled:
            zero = True
            countdown.step(1)
            while countdown.read() != 'R':
                zero = zero and countdown.read() == '0'
                countdown.step(1)
            countdown.rewind()
            if zero:
                answer, seen, enabled = value, True, False
            else:
                countdown.step(1)
                while countdown.read() == '0':
                    countdown.write('1'); countdown.step(1)
                need(countdown.read() == '1', 'countdown underflow')
                countdown.write('0'); countdown.rewind()
        rom.step(1)
    need(seen, 'current coordinate outside complete row')
    rom.rewind(); countdown.erase()
    return '0' if fault == 'suppress_query' else answer


class RowQuery:
    def __init__(self, w, records, entry_module, numeric, row_module, rom_module,
                 program, source, dirty, widths, ell, level, start, row, fault=None):
        self.w, self.records, self.source = w, records, source
        self.fault = fault
        self.entry = row_module.RowEntry(w, records, entry_module, numeric,
                                        source, dirty, widths, ell, level, start, row)
        self.output = None
        self.ports = []
        self.service = None
        self.producer_steps = 0
        self.invocations = 0
        self.closed = False
        if not self.entry.active:
            return
        # All variable-width initialization is driven by the existing unary guide.
        guide = self.entry.guide
        names = ('h', 'modulus', 'selected_layer', 'offsets')
        headers = {name: Tape() for name in names}
        coordinate, countdown, output = Tape(), Tape(), Tape()
        self.ports = [*headers.values(), coordinate, countdown, output]
        self.output = output
        output.emit('L')
        self.program = program
        self.service = {name: ['_'] for name in rom_module.REGS+('arena','spool','layers','rom')}
        self.service.update({name: headers[name].cells for name in names})
        self.produced_rom = Tape(self.service['rom'])
        self.produced_layers = Tape(self.service['layers'])
        self.ports.extend((self.produced_rom, self.produced_layers))
        result = self.entry.result['stream']
        size = 1 << level
        middle, stop = start+size//2, start+size
        precision = 1 + sum(widths[start:stop])  # Compiled topology only.
        for axis, h in enumerate(widths):
            chosen = middle <= axis < stop
            active = chosen and (h == ell or row not in (ell-1, ell))
            need(source.read() == records.ROOT, 'axis tag'); source.step(1)
            for _ in range(h):
                need(source.read() == w.ONE, 'compiled axis width'); source.step(1)
            need(source.read() == records.WORD_END, 'width delimiter'); source.step(1)
            if active:
                headers['modulus'].emit('L')
            for _ in range(h):
                bit=source.read(); need(bit in (w.ZERO,w.ONE), 'modulus bit')
                if active:
                    need(guide.read()==w.ONE,'modulus fits guide')
                    headers['modulus'].emit('1' if bit==w.ONE else '0');guide.step(1)
                source.step(1)
            if active:
                while guide.read()==w.ONE:
                    headers['modulus'].emit('0');guide.step(1)
                need(guide.read()==w.BLANK,'guide end');guide.rewind()
                headers['modulus'].write('R');headers['modulus'].rewind()
            need(source.read()==records.WORD_END,'modulus delimiter');source.step(1)
            if chosen:
                coordinate.emit('L')
                if active:countdown.emit('L')
            for _ in range(h):
                bit=source.read();need(bit in (w.ZERO,w.ONE),'coordinate bit')
                if chosen:
                    symbol='1' if bit==w.ONE else '0';coordinate.emit(symbol)
                    if active:countdown.emit(symbol)
                source.step(1)
            need(source.read()==records.RECORD_END,'axis end');source.step(1)
            if not chosen:
                continue
            coordinate.write('R');coordinate.rewind()
            need(result.read()==records.ROOT,'offset record');result.step(1)
            if active:
                countdown.write('R');countdown.rewind()
                local=row if h==ell or row<ell-1 else row-2
                selected=0 if fault=='wrong_local_row' else local
                # These constants belong to the compiled topology.
                hbits=tuple((h>>j)&1 for j in range(h.bit_length()))
                rowbits=tuple((selected>>j)&1 for j in range(max(1,selected.bit_length())))
                padded_constant(headers['h'],hbits,guide,w)
                padded_constant(headers['selected_layer'],rowbits,guide,w)
                copy_numeric_field(result,headers['offsets'],guide,w,records.WORD_END,'|')
                if fault=='zero_offset':
                    tape=headers['offsets'];tape.step(1)
                    while tape.read()!='|':tape.write('0');tape.step(1)
                    tape.rewind()
                # Proven producer bound, compiled from topology, not input values.
                budget=2*10**6*precision**2*((1<<h)+1)**3*(h+1)**4
                run=rom_module.execute(self.program,self.service,max_steps=budget)
                need(run['status']=='accept','unchanged ROM producer accepts')
                need(all(head==0 for head in run['heads'].values()),'ROM heads returned')
                self.producer_steps+=run['steps'];self.invocations+=1
                bit=select_row_bit(self.produced_rom,countdown,fault)
                target=min(local,2*h-2-local)
                coordinate.step(1)
                for _ in range(target):coordinate.step(1)
                old=coordinate.read();coordinate.write('1' if (old=='1')!=(bit=='1') else '0')
                coordinate.rewind()
                if fault!='omit_layers_disposal':self.produced_layers.erase()
                self.produced_rom.erase()
                for tape in headers.values():tape.erase()
            else:
                skip_numeric_field(result,guide,w,records.WORD_END)
            # The numerical whole-rotation field is consumed, never used as a row update.
            skip_numeric_field(result,guide,w,records.WORD_END)
            need(result.read()==records.RECORD_END,'offset record end');result.step(1)
            coordinate.step(1)
            while coordinate.read()!='R':
                output.emit(coordinate.read());coordinate.step(1)
            coordinate.rewind();coordinate.erase();output.emit('|')
        need(source.read()==w.RIGHT and result.read()==w.RIGHT,'complete joined streams')
        source.rewind();result.rewind();output.write('R');output.rewind()
        need(all(tape.head==0 for tape in self.ports),'all physical heads returned')

    def close(self):
        need(not self.closed,'single retirement')
        if self.output is not None:self.output.erase()
        self.entry.close()
        self.closed=True
