"""Joined one-target CRT repair on fixed tape roles (marker-driven, finite control).

Chain: unary geometry -> producer (#4208) -> stencil -> scanner (#4201) -> owned BAD mask
-> THIS FILE: split by that mask / key subroutine at marked addresses only / L full-key
stable radix passes / mask-driven reinsertion / physical erasure of every consumed or private
role and return of every head.

The tape program touches tapes only through read/write/move and branches only on read
symbols and fixed finite control. It never reads a host length, head coordinate, cell list,
action counter, address integer, hole list or inverse table.

THE ONE UNPAID POINT is ``evaluate_key``: it pays tape actions to read the address cells and
write the key cells, but the address -> key arithmetic is the caller's ``key_function`` (the
explicit "one key costs E" premise of CRT.md section 4). It is Python integer arithmetic, NOT
a tape evaluator.

Cells: markers LEFT/END/BLANK; bits "0"/"1" (counter, mask where 1 = bad, keys);
record cells ("R", payload) of 12 bits. Credit: Cinna Davis (#4100/#4088), kumagi (#4169),
ToikY (#4201, #4208), jmbarrancoml (PR2250 sparse repair), Ryanson Jonathan (#4328),
unpaidmoon (#4377). Apache-2.0.
"""

LEFT, END, BLANK = "<", ">", "_"


def is_record(symbol):
    return type(symbol) is tuple and symbol[0] == "R"


def is_bit(symbol):
    return symbol == "0" or symbol == "1"


def rewind(tape):
    while tape.read() != LEFT:
        tape.move(-1)


def erase(tape):
    """Blank every data cell and the END marker; keep permanent LEFT; return head."""
    rewind(tape)
    tape.move(1)
    while True:
        symbol = tape.read()
        tape.write(BLANK)
        if symbol == END:
            break
        tape.move(1)
    rewind(tape)


def init_counter(stencil, counter):
    """One '0' per stencil atom (the stencil is the length ruler); heads return to LEFT."""
    stencil.move(1)
    counter.move(1)
    while True:
        symbol = stencil.read()
        if symbol == END:
            counter.write(END)
            break
        counter.write("0")
        stencil.move(1)
        counter.move(1)
    rewind(stencil)
    rewind(counter)


def advance(counter, mask, increment):
    """Counter head LEFT -> END, then the scanner's binary carry (head returns to LEFT).
    The counter wraps exactly when the mask cell under the head is END."""
    counter.move(1)
    while counter.read() != END:
        counter.move(1)
    more = increment(counter, False)
    following = mask.read()
    if more == (following == END):
        raise ValueError("mask length differs from the stencil address space")


def evaluate_key(counter, out, key_function, meter):
    """Interface actions are paid; ``key_function`` arithmetic is the explicit premise."""
    before = counter.actions + out.actions
    counter.move(1)
    bits = []
    while True:
        symbol = counter.read()
        if symbol == END:
            break
        bits.append(symbol)
        counter.move(1)
    rewind(counter)
    key = key_function("".join(bits))
    for symbol in key:
        out.write(symbol)
        out.move(1)
    meter["calls"] += 1
    meter["interface_actions"] += counter.actions + out.actions - before


def split(mask, data, counter, good, bad, b0, key_function, increment, meter, flags):
    for tape in (mask, data, good, bad):
        tape.move(1)
    if "eval_good" in flags:  # negative control only: b0 borrowed as key scratch
        b0.move(1)
    while True:
        flag = mask.read()
        if flag == END:
            break
        record = data.read()
        if not is_record(record):
            raise ValueError("payload stream shorter than mask")
        if flag == "0":
            good.write(record)
            good.move(1)
            if "eval_good" in flags:  # negative control only
                evaluate_key(counter, b0, key_function, meter)
        elif flag == "1":
            bad.write(record)
            bad.move(1)
            evaluate_key(counter, bad, key_function, meter)
        else:
            raise ValueError("mask alphabet")
        mask.move(1)
        data.move(1)
        advance(counter, mask, increment)
    if data.read() != END:
        raise ValueError("payload stream longer than mask")
    good.write(END)
    bad.write(END)
    for tape in (mask, data, good, bad):
        rewind(tape)
    if "eval_good" in flags:
        b0.write(END)
        erase(b0)


def copy_until_end(source, destination):
    while True:
        symbol = source.read()
        if symbol == END:
            return
        destination.write(symbol)
        destination.move(1)
        source.move(1)


def one_pass(bad, b0, b1, flags):
    """Stable split by the LAST key bit; that bit is rotated to the front of its key.
    Pass i therefore splits on original key bit (LSB+i-1); after L passes the keys are in
    their original orientation, ordered by the full key (stable LSD radix)."""
    bad.move(1)
    b0.move(1)
    b1.move(1)
    while True:
        record = bad.read()
        if record == END:
            break
        if not is_record(record):
            raise ValueError("pair block must begin with its payload cell")
        bad.move(1)
        while is_bit(bad.read()):
            bad.move(1)
        bad.move(-1)
        last = bad.read()
        while not is_record(bad.read()):
            bad.move(-1)
        target = b1 if last == "1" else b0
        target.write(record)
        target.move(1)
        target.write(last)
        target.move(1)
        bad.move(1)
        held = bad.read()
        bad.move(1)
        while is_bit(bad.read()):
            target.write(held)
            target.move(1)
            held = bad.read()
            bad.move(1)
    b0.write(END)
    b1.write(END)
    for tape in (bad, b0, b1):
        rewind(tape)
    bad.move(1)
    b0.move(1)
    b1.move(1)
    copy_until_end(b0, bad)
    copy_until_end(b1, bad)
    bad.write(END)
    for tape in (bad, b0, b1):
        rewind(tape)
    if "keep_buckets" not in flags:
        erase(b0)
        erase(b1)


def sort_passes(stencil, bad, b0, b1, flags):
    stencil.move(1)
    while stencil.read() != END:
        one_pass(bad, b0, b1, flags)
        stencil.move(1)
    rewind(stencil)


def reinsert(mask, counter, data, good, bad, increment):
    """The counter is all-zero at LEFT: the split's last increment wrapped it."""
    for tape in (mask, data, good, bad):
        tape.move(1)
    while True:
        flag = mask.read()
        if flag == END:
            break
        if flag == "0":
            record = good.read()
            if not is_record(record):
                raise ValueError("good stream exhausted")
            good.move(1)
        else:
            record = bad.read()
            if not is_record(record):
                raise ValueError("keyed hole stream exhausted")
            bad.move(1)
            counter.move(1)
            while True:
                bit = counter.read()
                if bit == END:
                    break
                if bad.read() != bit:
                    raise ValueError("sorted key does not name the current hole")
                bad.move(1)
                counter.move(1)
            rewind(counter)
        data.write(record)
        data.move(1)
        mask.move(1)
        advance(counter, mask, increment)
    if good.read() != END or bad.read() != END:
        raise ValueError("reinsertion streams not exhausted together")
    for tape in (mask, good, bad):
        rewind(tape)


def finish(tape, keep):
    if keep:  # negative control: skipped clear
        rewind(tape)
    else:
        erase(tape)


def repair(stencil, mask, counter, data, good, bad, b0, b1,
           key_function, increment, meter, flags=frozenset(), mark=None):
    """Consume the scanner-owned ``mask`` directly. Return heads; erase every private or
    consumed role (mask, stencil, good, bad, counter; buckets inside each pass). ``data``
    ends holding the repaired payload stream, head at LEFT. ``mark`` is an observer hook
    called between phases by the verifier (never read by the tape program);
    ``flags`` select named faulty programs for negative controls only."""
    init_counter(stencil, counter)
    if mark is not None:
        mark("init_counter")
    split(mask, data, counter, good, bad, b0, key_function, increment, meter, flags)
    if mark is not None:
        mark("split_and_keys")
    if "skip_sort" not in flags:
        sort_passes(stencil, bad, b0, b1, flags)
    if mark is not None:
        mark("sort")
    reinsert(mask, counter, data, good, bad, increment)
    if mark is not None:
        mark("reinsert")
    finish(mask, "keep_mask" in flags)
    finish(stencil, "keep_stencil" in flags)
    finish(good, "keep_good" in flags)
    finish(bad, "keep_bad" in flags)
    finish(counter, "keep_counter" in flags)
    if "omit_head_return" not in flags:
        rewind(data)
    if mark is not None:
        mark("erase_and_return")
