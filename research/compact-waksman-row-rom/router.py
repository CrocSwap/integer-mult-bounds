"""Compact recursive permutation controls and dense-row access.

Produced by Nick Petalas. Apache-2.0.
The bypass topology is classical Waksman; see PROOF.md for attribution.
"""

MAX_HEIGHT = 12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(height):
    require(type(height) is int and 1 <= height <= MAX_HEIGHT,
            "height must be an integer from 1 through 12")
    n = 1 << height
    return n, 2 * height - 1, n * height - n + 1


def row_start(height, layer):
    n, layers, _ = dimensions(height)
    require(type(layer) is int and 0 <= layer < layers, "layer out of range")
    half = n // 2
    if layer < height:
        return layer * half
    return (layer - 1) * half + (1 << (2 * height - 1 - layer))


def address(height, layer, wire):
    """Return the stored bit index, or None for a fixed bypass control."""
    n, layers, _ = dimensions(height)
    require(type(wire) is int and 0 <= wire < n, "wire out of range")
    start = row_start(height, layer)
    depth = min(layer, layers - 1 - layer)
    stride = 1 << depth
    pair = (wire >> (depth + 1)) * stride + (wire & (stride - 1))
    if layer >= height and pair >= n // 2 - stride:
        return None
    return start + pair


def validate_rom(height, rom):
    _, _, size = dimensions(height)
    require(type(rom) in (tuple, list) and len(rom) == size,
            "wrong compact ROM length")
    require(all(type(bit) is int and bit in (0, 1) for bit in rom),
            "ROM must contain binary integers")


def query(height, rom, layer, wire):
    """Validated access. Batch callers can validate once and use address."""
    validate_rom(height, rom)
    index = address(height, layer, wire)
    return 0 if index is None else rom[index]


def pack_rom(height, rom):
    """Serialize controls least-significant-bit first, with zero tail padding."""
    validate_rom(height, rom)
    data = bytearray((len(rom) + 7) // 8)
    for index, bit in enumerate(rom):
        data[index // 8] |= bit << (index % 8)
    return bytes(data)


def query_packed(height, data, layer, wire):
    """Read a dense control without unpacking the canonical byte payload."""
    _, _, size = dimensions(height)
    require(type(data) is bytes and len(data) == (size + 7) // 8,
            "wrong packed ROM type or length")
    require(size % 8 == 0 or data[-1] >> (size % 8) == 0,
            "nonzero unused packed tail bits")
    index = address(height, layer, wire)
    return 0 if index is None else (data[index // 8] >> (index % 8)) & 1


def inverse_permutation(permutation):
    n = len(permutation)
    require(all(type(x) is int and 0 <= x < n for x in permutation),
            "permutation entries out of range")
    inverse = [-1] * n
    for x, y in enumerate(permutation):
        require(inverse[y] == -1, "duplicate permutation image")
        inverse[y] = x
    return inverse


def colors(permutation, inverse):
    """Color the alternating path first, then the remaining even cycles."""
    n = len(permutation)
    color = [-1] * n
    queue = [0] * n
    starts = [inverse[n - 2]] + list(range(n))
    for start in starts:
        if color[start] != -1:
            continue
        color[start] = 0
        queue[0] = start
        used, tail = 0, 1
        for _ in range(n):
            if used == tail:
                break
            x = queue[used]
            used += 1
            neighbors = [x ^ 1]
            if permutation[x] < n - 2:
                neighbors.append(inverse[permutation[x] ^ 1])
            for other in neighbors:
                opposite = color[x] ^ 1
                if color[other] == -1:
                    require(tail < n, "color worklist capacity")
                    color[other] = opposite
                    queue[tail] = other
                    tail += 1
                else:
                    require(color[other] == opposite, "inconsistent cycle")
        require(used == tail, "unfinished color component")
    require(color[inverse[n - 1]] == 1, "bypass endpoints must differ")
    return color


def split_node(height, depth, node, permutation, rom):
    n = len(permutation)
    inverse = inverse_permutation(permutation)
    color = colors(permutation, inverse)
    children = [[-1] * (n // 2), [-1] * (n // 2)]
    for pair in range(n // 2):
        wire = ((2 * pair) << depth) | node
        index = address(height, depth, wire)
        require(index is not None, "input switch is stored")
        rom[index] = color[2 * pair]
        if pair < n // 2 - 1:
            index = address(height, 2 * height - 2 - depth, wire)
            require(index is not None, "non-bypass output switch is stored")
            rom[index] = color[inverse[2 * pair]]
    for x in range(n):
        child = children[color[x]]
        position = x // 2
        require(child[position] == -1, "duplicate child input")
        child[position] = permutation[x] // 2
    for child in children:
        inverse_permutation(child)
    return children


def compile_rom(permutation):
    """Compile an input-to-output permutation, without mutating its input."""
    require(type(permutation) in (tuple, list), "permutation must be a sequence")
    n = len(permutation)
    require(2 <= n <= 1 << MAX_HEIGHT and n & (n - 1) == 0,
            "wire count must be a supported power of two")
    height = n.bit_length() - 1
    _, _, size = dimensions(height)
    inverse_permutation(permutation)
    rom = [-1] * size
    stack = [(0, 0, tuple(permutation))]
    for _ in range(n - 1):
        require(bool(stack), "missing routing node")
        depth, node, current = stack.pop()
        if len(current) == 2:
            index = address(height, depth, node)
            require(index is not None, "leaf switch is stored")
            rom[index] = current[0]
        else:
            upper, lower = split_node(height, depth, node, current, rom)
            stack.append((depth + 1, node | (1 << depth), lower))
            stack.append((depth + 1, node, upper))
    require(not stack, "too many routing nodes")
    validate_rom(height, rom)
    return tuple(rom)


def apply_rom(height, rom, values):
    """Apply the standard dense layer topology using compact controls."""
    n, layers, _ = dimensions(height)
    validate_rom(height, rom)
    require(type(values) in (tuple, list) and len(values) == n,
            "payload must have one value per wire")
    result = list(values)
    for layer in range(layers):
        depth = min(layer, layers - 1 - layer)
        stride = 1 << depth
        for wire in range(n):
            if wire & stride:
                continue
            index = address(height, layer, wire)
            if index is not None and rom[index]:
                other = wire | stride
                result[wire], result[other] = result[other], result[wire]
    return tuple(result)
