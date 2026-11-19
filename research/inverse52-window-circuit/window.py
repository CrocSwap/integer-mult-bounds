"""Generate a clean finite-window sampler circuit with an explicit censor flag.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas supplied the retained Boolean gate primitives.
"""
from collections import Counter
from sources import arithmetic as source

Q = 2704
STATE_WIDTH = 51


def bits(value, width):
    if type(value) is not int or type(width) is not int or width < 1 or not 0 <= value < 2**width:
        raise ValueError('constant does not fit its word')
    return tuple(bool(value & (1 << i)) for i in range(width))


class Circuit(source.Circuit):
    """Use the source gates with separately named wider word operations."""

    def __init__(self, first_scratch):
        self.gates = []
        self.next_wire = first_scratch

    def fresh(self):
        wire = self.next_wire
        self.next_wire += 1
        return wire

    def add_word(self, left, right, carry=False):
        if len(left) != len(right) or len(left) not in (12, 13):
            raise ValueError('invalid wide adder widths')
        result = []
        for x, y in zip(left[:-1], right[:-1], strict=True):
            difference = self.xor(x, y)
            result.append(self.xor(difference, carry))
            carry = self.xor(self.both(x, y), self.both(difference, carry))
        result.append(self.xor(self.xor(left[-1], right[-1]), carry))
        return tuple(result)

    def select_word(self, flag, low, high):
        if len(low) != len(high) or len(low) != 12:
            raise ValueError('invalid residue selector widths')
        return tuple(self.xor(x, self.both(flag, self.xor(x, y)))
                     for x, y in zip(low, high, strict=True))


def subtract(c, left, right):
    return c.add_word(left, tuple(c.xor(b, True) for b in right), carry=True)


def prepare(c, a, b):
    terms = [tuple([False]*i+[c.both(flag, x) for x in a]+[False]*(6-i))
             for i, flag in enumerate(b)]
    product = terms[0]
    for term in terms[1:]:
        product = c.add_word(product, term)

    def scale52(word):
        shifted = [tuple([False]*i+list(word)+[False]*(6-i)) for i in (2, 4, 5)]
        return c.add_word(c.add_word(shifted[0], shifted[1]), shifted[2])

    alpha, beta = scale52(a), scale52(b)
    w1, w2 = subtract(c, beta, product), subtract(c, alpha, product)
    w0 = c.add_word(subtract(c, subtract(c, bits(Q, 12), alpha), beta), product)
    deterministic = True
    for x in (*a, *b):
        deterministic = c.both(deterministic, c.xor(x, True))
    pending = c.xor(deterministic, True)
    r0 = tuple(c.both(pending, x) for x in w0)
    return (*r0, *w1, *w2, *product, False, False, deterministic)


def double_residue(c, word):
    doubled = (False, *word)
    reduced = c.add_word(doubled, bits(8192-Q, 13))
    digit = c.xor(reduced[12], True)
    residue = c.select_word(digit, doubled[:12], reduced[:12])
    return residue, digit


def advance(c, state, coin):
    residues, digits = [], []
    for i in range(4):
        residue, digit = double_residue(c, state[12*i:12*(i+1)])
        residues.extend(residue)
        digits.append(digit)
    starts, count = [], bits(0, 3)
    for digit in digits:
        starts.append(count)
        count = c.add(count, (digit, False, False))
    rank = (coin, *state[48:50])
    leaves = [c.both(digit, c.equal(rank, start)) for digit, start in zip(digits, starts, strict=True)]
    label = (c.xor(leaves[1], leaves[3]), c.xor(leaves[2], leaves[3]))
    stop = c.xor(c.xor(leaves[0], leaves[1]), c.xor(leaves[2], leaves[3]))
    node = c.add(rank, tuple(c.xor(x, True) for x in count), carry=True)[:2]
    packet = c.select(stop, node, label)
    output = c.select(state[50], packet, state[48:50])
    done = c.xor(state[50], c.both(c.xor(state[50], True), stop))
    return (*residues, *output, done)


def clean_oracle(c, targets, values):
    computation = tuple(c.gates)
    for target, signal in zip(targets, values, strict=True):
        c.toggle(target, signal)
    return (*c.gates, *reversed(computation))


def build(length):
    if type(length) is not int or length < 1:
        raise ValueError('window length must be a positive integer')
    depth_width = (length+1).bit_length()
    params = (tuple(range(6)), tuple(range(6, 12)))
    coins = tuple(range(12, 12+length))
    output = tuple(range(12+length, 15+length+depth_width))
    history_start = output[-1]+1
    states = [tuple(range(history_start+STATE_WIDTH*i, history_start+STATE_WIDTH*(i+1)))
              for i in range(length+1)]
    scratch_start = states[-1][-1]+1
    preparation = Circuit(scratch_start)
    prep = clean_oracle(preparation, states[0], prepare(preparation, *params))
    forward = list(prep)
    peak = preparation.next_wire
    step_count = None
    for t in range(length):
        c = Circuit(scratch_start)
        step = clean_oracle(c, states[t+1], advance(c, states[t], coins[t]))
        forward.extend(step)
        peak = max(peak, c.next_wire)
        if step_count is not None and len(step) != step_count:
            raise ValueError('step gate count changed')
        step_count = len(step)
    done = states[-1][50]
    copy = [(output[0], (done,)),
            (output[1], (done, states[-1][48])),
            (output[2], (done, states[-1][49]))]
    for i, bit in enumerate(bits(length+1, depth_width)):
        if bit:
            copy.append((output[3+i], ()))
    # The stopping flags are monotone. Adjacent depth labels telescope by XOR.
    for t, state in enumerate(states):
        for i, bit in enumerate(bits(t ^ (t+1), depth_width)):
            if bit:
                copy.append((output[3+i], (state[50],)))
    gates = (*forward, *copy, *reversed(forward))
    counts = Counter(len(controls) for _, controls in gates)
    if any(len(set((target, *controls))) != 1+len(controls) for target, controls in gates):
        raise ValueError('aliased gate wires')
    if any(target < output[0] for target, _ in gates):
        raise ValueError('read-only input changed')
    return {'gates': gates, 'wires': peak, 'params': params, 'coins': coins, 'output': output,
            'states': states, 'scratch_start': scratch_start,
            'bill': {'length': length, 'X': counts[0], 'CNOT': counts[1], 'Toffoli': counts[2],
                     'gates': len(gates), 'preparation_oracle_gates': len(prep),
                     'draw_oracle_gates': step_count, 'answer_oracle_gates': len(copy),
                     'history_bits': STATE_WIDTH*(length+1), 'temporary_bits': peak-scratch_start,
                     'clean_work_bits': peak-history_start, 'output_bits': len(output),
                     'input_bits': 12+length, 'total_wires': peak}}
