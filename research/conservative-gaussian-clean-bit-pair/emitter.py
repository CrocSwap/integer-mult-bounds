"""Literal clean implementation of the credited conservative pair, via local templates."""


def require(ok, message):
    if not ok:
        raise ValueError(message)


def layout(width):
    require(type(width) is int and 6 <= width <= 256, 'width6..256')
    words = [tuple(range(i * width, (i + 1) * width)) for i in range(18)]
    return words[:4], words[4:8], words[8:], 18 * width, tuple(range(18 * width + 1, 18 * width + 6))


def templates(width, scalar):
    source = tuple(range(width)); target = tuple(range(width, 2 * width))
    add = scalar.adder(source, target, 2 * width)
    scalar.validate(width, add)
    half = scalar.circuit(width, 'scale', 1, 2, [('half', 0)], [])
    require(all(all(wire < width for wire in gate) for gate in half), 'half uses target-only local wires')
    return add, half


def renamed_add(local, source, target, carry):
    mapping = tuple(source) + tuple(target) + (carry,)
    require(len(set(mapping)) == len(mapping), 'injective local-template embedding')
    return [tuple(mapping[i] for i in gate) for gate in local]


def copies(source, target):
    require(len(source) == len(target) and not set(source).intersection(target), 'disjoint copy words')
    return list(zip(source, target))


def evaluation(width, sign, scalar):
    require(type(sign) is int and sign in (-1, 1), 'public compile-time orientation')
    data, _, work, carry, tags = layout(width)
    sr, si, dr, di, cr, ci, nr, ni, second_r, second_i = work
    parity, active_r, active_i, negative_r, negative_i = tags
    local_add, local_half = templates(width, scalar)
    gates = []

    def add(source, target, orientation=1):
        block = renamed_add(local_add, source, target, carry)
        gates.extend(block if orientation > 0 else reversed(block))

    for source, target in [(data[0], sr), (data[1], si), (data[0], dr), (data[1], di)]:
        gates.extend(copies(source, target))
    add(data[2], sr); add(data[3], si); add(data[2], dr, -1); add(data[3], di, -1)
    gates.extend([(sr[0], parity), (si[0], parity), (parity, sr[0], active_r),
                  (parity, si[0], active_i), (active_r, sr[-1], negative_r),
                  (active_i, si[-1], negative_i)])
    for active, negative, target in [(active_r, negative_r, cr), (active_i, negative_i, ci)]:
        gates.append((active, target[0]))
        gates.extend((negative, bit) for bit in target[1:])
    gates.extend(copies(sr, nr)); gates.extend(copies(si, ni))
    add(di, nr, -sign); add(cr, nr); add(ci, nr, sign)
    add(dr, ni, sign); add(ci, ni); add(cr, ni, -sign)
    gates.extend(tuple(nr[i] for i in gate) for gate in local_half)
    gates.extend(tuple(ni[i] for i in gate) for gate in local_half)
    gates.extend(copies(sr, second_r)); gates.extend(copies(si, second_i))
    add(nr, second_r, -1); add(ni, second_i, -1)
    return gates, [nr, ni, second_r, second_i]


def circuit(width, sign, scalar):
    data, buffer, _, _, _ = layout(width)
    forward, out = evaluation(width, sign, scalar)
    backward, inverse_out = evaluation(width, -sign, scalar)
    copy_out = [gate for source, target in zip(out, buffer) for gate in copies(source, target)]
    copy_inverse = [gate for source, target in zip(inverse_out, buffer) for gate in copies(source, target)]
    swap = [gate for a, b in zip(data, buffer) for x, y in zip(a, b)
            for gate in [(x, y), (y, x), (x, y)]]
    return forward + copy_out + list(reversed(forward)) + swap + backward + copy_inverse + list(reversed(backward))


def inventory(width, sign, gates):
    total = 18 * width + 6
    cnot = toffoli = 0
    for gate in gates:
        require(type(gate) in (list, tuple) and len(gate) in (2, 3), 'literal CX/CCX alphabet')
        require(all(type(i) is int and 0 <= i < total for i in gate) and len(set(gate)) == len(gate), 'gate wire inventory')
        cnot += len(gate) == 2
        toffoli += len(gate) == 3
    bits = (total - 1).bit_length()
    return {'width': width, 'sign': sign, 'data_bits': 4 * width, 'clean_bits': 14 * width + 6,
            'wires': total, 'cx': cnot, 'ccx': toffoli, 'x': 0,
            'gates': len(gates), 'selector_bits': bits,
            'address_occurrences': 2 * cnot + 3 * toffoli,
            'control_incidences': cnot + 2 * toffoli,
            'encoded_bits': 9 + 2 * len(gates) + bits * (2 * cnot + 3 * toffoli)}
