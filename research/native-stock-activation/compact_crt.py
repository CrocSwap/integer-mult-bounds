"""Execute a compact CRT switch on a tape of arbitrary fixed-width records."""

from collections import Counter

from streaming_routes import copy_bytes, erase, read_exact, work_tapes


def binary_swap(source, target, bits, prefix, gap, suffix_bytes):
    """Use four digit buckets for the complete ordinary base case."""
    count = 1 << bits
    volume = prefix * count * gap * count * suffix_bytes
    with work_tapes(6) as (a, b, *buckets):
        copy_bytes(source, a, volume)
        for i in range(bits):
            a.seek(0)
            before = prefix << i
            after = suffix_bytes << (bits - 1 - i)
            between = gap << (bits - 1)
            for _ in range(before):
                for head in range(2):
                    for _ in range(between):
                        for tail in range(2):
                            copy_bytes(a, buckets[2 * head + tail], after)
                for bucket in buckets:
                    bucket.seek(0)
                for tail in range(2):
                    for _ in range(between):
                        for head in range(2):
                            copy_bytes(buckets[2 * head + tail], b, after)
                for bucket in buckets:
                    erase(bucket)
            erase(a)
            a, b = b, a
        a.seek(0)
        copy_bytes(a, target, volume)


class CompactSwitch:
    """Control digits occupy the high two fields. The back field is least significant."""

    def __init__(self, high, body, digit, guard, positions, switches):
        self.high = high
        self.body = body
        self.digit = digit
        self.guard = guard
        self.positions = tuple(positions)
        self.switches = switches
        if (
            not positions
            or high < digit * len(positions)
            or min(high, body, digit) < 1
            or guard <= digit + 2
            or min(positions) < 0
            or max(positions) + guard > body
            or any(b - a < guard for a, b in zip(sorted(positions), sorted(positions)[1:]))
        ):
            raise ValueError("The compact fields must have complete disjoint guard intervals")
        self.rows = 1 << high
        self.ys = 1 << body
        self.key_bytes = (2 * high + body + 7) // 8
        self.stats = Counter()
        # Open upper guard excludes its two extreme bit strings.
        self.y_checks = tuple((body - pos - guard, body - pos - digit - 2) for pos in positions)
        self.control_checks = tuple(
            (high - (i + 1) * digit, high - i * digit) for i in range(len(positions))
        )

    def good(self, u, t, y):
        for value in (u, t):
            word = format(value, f"0{self.high}b")
            if any("0" not in word[a:b] for a, b in self.control_checks):
                return False
        word = format(y, f"0{self.body}b")
        return all("0" in word[a:b] and "1" in word[a:b] for a, b in self.y_checks)

    def delta(self, step, u, t, y):
        amount = 0
        if step in ("load", "unload"):
            for i, bit in enumerate(self.switches(y)):
                amount += bit << (i * self.digit)
            return amount if step == "load" else -amount
        mask = (1 << self.digit) - 1
        for i, pos in enumerate(self.positions):
            offset = i * self.digit
            z = (u >> offset) & 1
            value = (t >> offset) & mask
            bit = (y >> pos) & 1
            if step == "first-y":
                amount += (2 * z * value) << pos
            elif step == "plus-t":
                amount += bit << offset
            elif step == "second-y":
                amount += (z * (1 - 2 * value)) << pos
            else:
                amount -= (bit ^ z) << offset
        return amount

    # The forward and reverse control maps use these same arithmetic steps.
    F = (("first-y", 2), ("plus-t", 1), ("second-y", 2), ("minus-t", 1))
    WORD = F + (("load", 0),) + F + (("unload", 0),)

    def repair_key(self, u, t, y):
        coords = [u, t, y]
        moduli = (self.rows, self.rows, self.ys)
        for op, dest in reversed(self.WORD):
            coords[dest] = (coords[dest] - self.delta(op, *coords)) % moduli[dest]
        u, t, y = coords
        for bit, pos in zip(self.switches(y), self.positions, strict=True):
            y ^= bit << pos
        return (u * self.rows + t) * self.ys + y

    @staticmethod
    def rotation(src, dst, tmp, count, part, change):
        shift = change % count
        n = (count - shift) * part
        copy_bytes(src, tmp, n)
        copy_bytes(src, dst, shift * part)
        tmp.seek(0)
        copy_bytes(tmp, dst, n)
        erase(tmp)

    def raw(self, source, target, size, swap):
        rows, ys = self.rows, self.ys
        with work_tapes(3) as (a, b, tmp):
            copy_bytes(source, a, rows**3 * ys * size)

            def pass_(operation):
                nonlocal a, b
                a.seek(0)
                operation(a, b)
                erase(a)
                a, b = b, a

            def shuttle(dest):
                gap = ys if dest == 1 else self.rows * ys
                prefix = self.rows if dest == 1 else 1
                pass_(lambda s, d: swap(s, d, self.high, prefix, gap, size))
                self.stats["whole_field_swaps"] += 1

            for op, dest in self.WORD:
                if dest == 2:

                    def y_pass(s, d):
                        for u in range(rows):
                            for t in range(rows):
                                self.rotation(s, d, tmp, ys, rows * size, self.delta(op, u, t, 0))

                    pass_(y_pass)
                else:
                    shuttle(dest)

                    def back_pass(s, d):
                        # The old back field occupies the selected front slot.
                        for first in range(rows):
                            for _ in range(rows):
                                for y in range(ys):
                                    self.rotation(
                                        s, d, tmp, rows, size, self.delta(op, first, 0, y)
                                    )

                    pass_(back_pass)
                    shuttle(dest)
            a.seek(0)
            copy_bytes(a, target, rows**3 * ys * size)

    def repair(self, source, target, size):
        rows, ys = self.rows, self.ys
        piece = rows * size
        width = self.key_bytes
        with work_tapes(5) as (marked, keys, sorted_keys, left, right):
            count = 0
            for u in range(rows):
                for t in range(rows):
                    for y in range(ys):
                        if self.good(u, t, y):
                            marked.write(b"G")
                            copy_bytes(source, marked, piece)
                        else:
                            marked.write(b"H")
                            keys.write(self.repair_key(u, t, y).to_bytes(width, "little"))
                            copy_bytes(source, keys, piece)
                            count += 1
            self.stats["repaired_records"] += count * rows
            for bit in range(2 * self.high + self.body):
                keys.seek(0)
                bytes_in_right = 0
                for _ in range(count):
                    key = read_exact(keys, width)
                    high = key[bit // 8] >> (bit % 8) & 1
                    bank = right if high else left
                    bytes_in_right += high * (width + piece)
                    bank.write(key)
                    copy_bytes(keys, bank, piece)
                for bank, length in (
                    (left, count * (width + piece) - bytes_in_right),
                    (right, bytes_in_right),
                ):
                    bank.seek(0)
                    copy_bytes(bank, sorted_keys, length)
                    erase(bank)
                erase(keys)
                keys, sorted_keys = sorted_keys, keys
            keys.seek(0)
            marked.seek(0)
            for address in range(rows * rows * ys):
                if read_exact(marked, 1) == b"G":
                    copy_bytes(marked, target, piece)
                else:
                    if int.from_bytes(read_exact(keys, width), "little") != address:
                        raise ArithmeticError("The sorted key did not reach its original hole")
                    copy_bytes(keys, target, piece)

    def apply(self, source, target, record_bytes, swap):
        with work_tapes(1) as (intermediate,):
            self.raw(source, intermediate, record_bytes, swap)
            intermediate.seek(0)
            self.repair(intermediate, target, record_bytes)
