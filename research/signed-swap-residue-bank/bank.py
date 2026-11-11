"""Signed-exchange dispatch for zxv's paired DDG. Apache-2.0.

The 21 source tables are supplied by the caller. No source sampler is changed.
"""

REPRESENTATIVES = tuple((a, b) for a in range(1, 7) for b in range(a, 7))
STATES = 312
TABLE_BYTES = 702
SELECTORS = 144
BANK_BYTES = SELECTORS + len(REPRESENTATIVES) * TABLE_BYTES


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def pair_index(a: int, b: int) -> int:
    require(type(a) is int and type(b) is int, "integer residue pair")
    require(1 <= a <= 12 and 1 <= b <= 12, "nonzero residue pair")
    return (a - 1) * 12 + b - 1


def selector(a: int, b: int) -> int:
    _ = pair_index(a, b)  # Validate the pair; its input index is not needed here.
    left, right = min(a, 13 - a), min(b, 13 - b)
    flags = 2 * int(a > 6) + int(b > 6)
    if left > right:
        left, right = right, left
        flags += 4
    return 8 * REPRESENTATIVES.index((left, right)) + flags


def output_map(flags: int, output: int) -> int:
    require(type(flags) is int and 0 <= flags < 8, "output flags")
    require(type(output) is int and 0 <= output < 4, "output label")
    left, right = output >> 1, output & 1
    if flags & 4:
        left, right = right, left
    return 2 * (left ^ ((flags >> 1) & 1)) + (right ^ (flags & 1))


def pack(tables: tuple) -> bytes:
    require(len(tables) == 21, "canonical table count")
    payload = bytearray(BANK_BYTES)
    for a in range(1, 13):
        for b in range(1, 13):
            payload[pair_index(a, b)] = selector(a, b)
    for table_id, table in enumerate(tables):
        require(len(table) == STATES, "source state count")
        base = SELECTORS + table_id * TABLE_BYTES
        for state, row in enumerate(table):
            require(len(row) == 2, "binary transition row")
            for coin, target in enumerate(row):
                require(type(target) is int and 0 <= target < 316, "table target")
                position = 9 * (2 * state + coin)
                byte, shift = divmod(position, 8)
                word = target << shift
                payload[base + byte] |= word & 255
                payload[base + byte + 1] |= word >> 8
    return bytes(payload)


def transition(payload: bytes, code: int, state: int, coin: int) -> int:
    require(type(payload) is bytes and len(payload) == BANK_BYTES, "bank length")
    require(type(code) is int and 0 <= code < 168, "selector code")
    require(type(state) is int and 0 <= state < STATES, "pending state")
    require(type(coin) is int and coin in (0, 1), "binary coin")
    table_id, flags = divmod(code, 8)
    byte, shift = divmod(9 * (2 * state + coin), 8)
    offset = SELECTORS + table_id * TABLE_BYTES + byte
    target = ((payload[offset] | (payload[offset + 1] << 8)) >> shift) & 511
    require(target < 316, "packed target")
    if target >= STATES:
        return STATES + output_map(flags, target - STATES)
    return target


def run(payload: bytes, a: int, b: int, coins: tuple) -> tuple:
    index = pair_index(a, b)
    require(type(payload) is bytes and len(payload) == BANK_BYTES, "bank length")
    require(type(coins) is tuple and len(coins) <= 4096, "finite tape limit")
    require(all(type(coin) is int and coin in (0, 1) for coin in coins), "binary tape")
    state, code = 0, payload[index]
    for used, coin in enumerate(coins, 1):
        state = transition(payload, code, state, coin)
        if state >= STATES:
            return state - STATES, used
    return None, len(coins)
