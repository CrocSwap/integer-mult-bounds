"""Exercise the dispatcher on complete, nonconstant address streams."""

from itertools import product
from math import isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from interchange import (Port, Request, Slabs, block_word, close_cycle, elementary,
                         exchange_range, fixed_block_word)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def region(port, left, right, width):
    """Keep the whole stream and expose two contiguous subfields."""
    q, e = port.q, port.width
    require(0 <= left <= e-width and 0 <= right <= e-width, "field outside port")
    return Port(q, width, port.prefix*q**left,
                port.gap*q**(e-left-width+right), port.suffix*q**(e-right-width))


def lower(port, data, coefficient, sign=1):
    """Apply tail = sign * tail + coefficient * head on complete fibres."""
    out = []
    reader = iter(data)
    for _ in range(port.prefix):
        for head in range(port.side):
            for _ in range(port.gap):
                rows = [[next(reader) for _ in range(port.suffix)] for _ in range(port.side)]
                for tail in range(port.side):
                    out.extend(rows[(sign*(tail-coefficient*head)) % port.side])
    return out


def address_oracle(port, source, action):
    output = [None]*port.volume
    side = port.side
    offset = 0
    for prefix, head, gap, tail in product(range(port.prefix), range(side),
                                            range(port.gap), range(side)):
        new_head, new_tail = action(head, tail)
        dst = (((prefix*side + new_head)*port.gap + gap)*side + new_tail)*port.suffix
        output[dst:dst+port.suffix] = source[offset:offset+port.suffix]
        offset += port.suffix
    return output


def swap(head, tail):
    return tail, head


def reversed_body(port, data, atom):
    count = port.width//atom
    for i in range(count):
        part = region(port, i*atom, (count-1-i)*atom, atom)
        data = yield Request(part, data)
    return data


def ordinary_fixture(port, source):
    """Use the five source operations with an executable sequential body."""
    q, e = port.q, port.width
    atom = isqrt(e-1) + 1
    high = (1 if q > 2 else 2) if e >= 5 else 0
    divisor = (2 if q > 2 else 3) if high else 1
    high_side = q**high
    padded = -(-high_side//divisor)*divisor
    data = []
    span = port.volume//port.prefix
    for prefix in range(port.prefix):
        data.extend(source[prefix*span:(prefix+1)*span])
        data.extend([0]*((padded-high_side)*(span//high_side)))
    working = Port(q, e-high, port.prefix*padded, port.gap*high_side, port.suffix)
    body_size = working.width//atom*atom
    body = region(working, 0, 0, body_size)
    for coefficient, sign in ((-1, 1), (1, 1), (1, -1)):
        for pos in range(0, body_size, atom):
            data = lower(region(body, pos, pos, atom), data, coefficient, sign)
        if sign == 1:
            data = yield from reversed_body(body, data, atom)
    if body_size < working.width:
        rest = region(working, body_size, body_size, working.width-body_size)
        data = elementary(rest, data)
    unpadded = []
    block = working.volume//port.prefix
    for prefix in range(port.prefix):
        start = prefix*block
        unpadded.extend(data[start:start+span])
        require(all(value == 0 for value in data[start+span:start+block]), "padding leaked")
    return elementary(region(port, 0, 0, high), unpadded)


def run_tests():
    seen = []
    words = (ordinary_fixture, block_word(1, 2))
    def ordinary(port, data, entry=0):
        stack = []
        def visit(tag, local, depth):
            require(tag == (entry+depth) % len(words), "wrong ordinary entry")
            if depth:
                require(2*local.volume <= stack[depth-1], "noncontracting live frame")
            stack[depth:] = [local.volume]
            seen.append((local.width, local.volume, depth))
        return close_cycle(words, entry, port, data, cutoff=2, fanout=5, observe=visit)

    totals = 0
    for q, e, prefix, gap, suffix in ((3, 0, 2, 5, 3), (3, 2, 2, 3, 5),
                                      (3, 4, 1, 3, 2), (3, 5, 1, 1, 1),
                                      (2, 6, 2, 1, 3), (2, 7, 1, 2, 1)):
        port = Port(q, e, prefix, gap, suffix)
        source = list(range(1, port.volume+1))
        before = tuple(source)
        out = ordinary(port, source)
        require(out == address_oracle(port, source, swap), "complete ordinary endpoint")
        require(ordinary(port, source, 1) == out, "second public entry")
        require(tuple(source) == before, "borrowed input changed")
        totals += len(out)
    require(max(depth for _, _, depth in seen) >= 2, "single-stage run")

    # Exercise four ordinary moves of a weighted leaf at a nonunit-width modulus.
    p = Port(3, 3, 1, 2, 3)
    src = list(range(p.volume))
    for a in (2, 5, 11):
        inverse = pow(a, -1, p.side)
        result = src
        for index, coefficient in enumerate((a, -inverse, a)):
            if index == 1:
                result = lower(p, result, coefficient)
            else:
                result = ordinary(p, lower(p, ordinary(p, result), coefficient))
        result = lower(p, result, 0, -1)
        wanted = address_oracle(p, src, lambda h, d: (a*d % p.side, inverse*h % p.side))
        require(result == wanted, "weighted leaf or signed unit inversion")
    # A right-column transposition swaps the two entries in each high-matrix row.
    high = 3**2
    bits = list(range(high**4))
    out = ordinary(Port(3, 2, 1, 1, high**2), bits)
    out = ordinary(Port(3, 2, high**2, 1, 1), out)
    expected = [((b*high+a)*high+d)*high+c
                for a,b,c,d in product(range(high), repeat=4)]
    require(out == expected, "right route or complete cover fibre")
    require(ordinary(Port(3, 0, 1, 1, 3), [6, 9, 8]) == [6, 9, 8], "empty high cube")

    shards = 0
    for p in (Port(3, 1, 11, 2, 3), Port(3, 1, 2, 13, 3), Port(3, 1, 2, 3, 17)):
        source = list(range(p.volume))
        slabs = Slabs(p, 5)
        pieces = slabs.split(source)
        output = slabs.merge([elementary(s, b) for s, b in zip(slabs.ports, pieces, strict=True)])
        require(output == address_oracle(p, source, swap), "ragged spectator reassembly")
        require(sum(len(b) for b in pieces) == p.volume, "lost arbitrary data")
        shards += len(pieces)
    for size in (1, 5, 8, 17):
        source = list(range(2*size**2*3*2))
        answer = exchange_range(words, 0, 3, size, 2, 3, 2, source,
                                cutoff=2, fanout=5)
        expected = [(((p*size+d)*3+g)*size+h)*2+s
                    for p,h,g,d,s in product(range(2), range(size), range(3),
                                             range(size), range(2))]
        require(answer == expected, "non-power public range or binary padding")
    fixed_positions = 0
    for counts in ((2,), (2, 3)):
        stages = tuple(fixed_block_word(k) for k in counts) + (ordinary_fixture,)
        for q, width, prefix, gap, suffix in ((2, 5, 3, 2, 3), (2, 7, 1, 1, 3), (3, 4, 2, 1, 1)):
            port = Port(q, width, prefix, gap, suffix)
            labels = tuple(range(port.volume))
            expected = address_oracle(port, labels, swap)
            for entry in range(len(stages)):
                output = close_cycle(stages, entry, port, labels, cutoff=2, fanout=5)
                require(output == expected, "fixed block count, ragged tail or successor tag")
                fixed_positions += port.volume
    return totals, max(d for _, _, d in seen), shards, fixed_positions


if __name__ == "__main__":
    entries, depth, shards, fixed = run_tests()
    print(f"PASS_STREAM_CLOSURE entries={entries} nested_depth={depth} ragged_slabs={shards} "
          f"fixed_block_positions={fixed}")
