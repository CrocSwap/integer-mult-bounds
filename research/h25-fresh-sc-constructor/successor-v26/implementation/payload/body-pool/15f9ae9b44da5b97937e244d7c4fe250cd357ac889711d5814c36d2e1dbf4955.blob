"""Bounded lossless exact-native-data codec; no object hooks or foreign formatting.

Canonical tags match literal_protocol_v1 for its admitted domain. A separate
'l' tag preserves unexpected exact lists in raw evidence. They are never equal
to tuples. This module must be admitted with the complete original source graph.
"""
from hashlib import sha256 as _sha256

MAX_DEPTH = 32
MAX_NODES = 200000
MAX_CONTAINER = 16384
MAX_STRING_CHARS = 65536
MAX_BYTES = 16777216
MAX_INTEGER_BITS = 128
MAX_ENCODED = 64 * 1024 * 1024


def encode(value, limit=MAX_ENCODED, allow_lists=True):
    if type(limit) is not int or not 1 <= limit <= 16 * 1024 * 1024 or type(allow_lists) is not bool:
        raise RuntimeError('typed codec bound argument')
    pending, pieces, active = [(0, value, 0)], [], set()
    count = size = 0
    while pending:
        operation, item, depth = pending.pop()
        if operation == 1:
            active.remove(item)
            continue
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise RuntimeError('typed codec node/depth limit')
        kind = type(item)
        if item is None:
            raw = b'n'
        elif kind is bool:
            raw = b'y' if item else b'z'
        elif kind is int:
            if int.bit_length(item) > MAX_INTEGER_BITS:
                raise RuntimeError('typed codec integer bound')
            raw = b'i' + str(item).encode('ascii') + b';'
        elif kind is str:
            if len(item) > MAX_STRING_CHARS:
                raise RuntimeError('typed codec string bound')
            payload = str.encode(item, 'utf-8')
            raw = b's' + str(len(payload)).encode('ascii') + b':' + payload
        elif kind is bytes:
            if len(item) > MAX_BYTES:
                raise RuntimeError('typed codec byte value bound')
            raw = b'b' + str(len(item)).encode('ascii') + b':' + item
        elif kind is tuple or kind is list or kind is dict:
            if kind is list and not allow_lists:
                raise RuntimeError('typed codec list outside literal input domain')
            if len(item) > MAX_CONTAINER or id(item) in active:
                raise RuntimeError('typed codec collection/cycle bound')
            active.add(id(item))
            pending.append((1, id(item), depth))
            if kind is dict:
                # No lookup, sorting, hash or equality uses a foreign key.
                keys = []
                for key in dict.__iter__(item):
                    if type(key) is not str:
                        raise RuntimeError('typed codec foreign dictionary key')
                    if len(key) > MAX_STRING_CHARS:
                        raise RuntimeError('typed codec dictionary key bound')
                    keys.append(key)
                keys.sort()
                raw = b'd' + str(len(keys)).encode('ascii') + b':'
                for key in reversed(keys):
                    pending.append((0, dict.__getitem__(item, key), depth + 1))
                    pending.append((0, key, depth + 1))
            else:
                raw = (b't' if kind is tuple else b'l') + str(len(item)).encode('ascii') + b':'
                for child in reversed(item):
                    pending.append((0, child, depth + 1))
        else:
            # Keep foreign values opaque in the caller; never inspect their type name.
            raise RuntimeError('typed codec unsupported exact type')
        size += len(raw)
        if size > limit:
            raise RuntimeError('typed codec encoded byte bound')
        pieces.append(raw)
    return b''.join(pieces)


def fingerprint(value, limit=MAX_ENCODED):
    return _sha256(encode(value, limit, False)).hexdigest()


def equal(left, right, limit=MAX_ENCODED):
    # Full canonical bytes are compared, not merely hashes or ordinary containers.
    return encode(left, limit, True) == encode(right, limit, True)


def mutable_container_ids(value):
    """Return source-owned integer identities after full exact-type admission."""
    encode(value, MAX_ENCODED, False)
    pending, output, visited = [value], set(), set()
    while pending:
        item = pending.pop()
        kind = type(item)
        if kind is dict or kind is tuple:
            identity = id(item)
            if identity in visited:
                continue
            visited.add(identity)
            if kind is dict:
                output.add(identity)
                pending.extend(dict.values(item))
            else:
                pending.extend(item)
    return output


def decode(raw, limit=MAX_ENCODED):
    """Portable bounded readback of .typed evidence; no target modules involved."""
    if type(raw) is not bytes or type(limit) is not int or not 1 <= limit <= 16 * 1024 * 1024 or len(raw) > limit:
        raise RuntimeError('typed decode input bound')
    cursor, nodes = 0, 0

    def number(terminal):
        nonlocal cursor
        start = cursor
        while cursor < len(raw) and raw[cursor] != terminal:
            if cursor - start > 40:
                raise RuntimeError('typed decode number bound')
            cursor += 1
        if cursor == len(raw):
            raise RuntimeError('typed decode incomplete number')
        value = raw[start:cursor]
        cursor += 1
        if not value or any(x < 48 or x > 57 for x in value) or (len(value) > 1 and value[0] == 48):
            raise RuntimeError('typed decode noncanonical count')
        return int(value)

    def item(depth):
        nonlocal cursor, nodes
        nodes += 1
        if depth > MAX_DEPTH or nodes > MAX_NODES or cursor >= len(raw):
            raise RuntimeError('typed decode shape limit')
        tag = raw[cursor]
        cursor += 1
        if tag == 110:
            return None
        if tag == 121:
            return True
        if tag == 122:
            return False
        if tag == 105:
            negative = cursor < len(raw) and raw[cursor] == 45
            if negative:
                cursor += 1
            value = number(59)
            if int.bit_length(value) > MAX_INTEGER_BITS or (negative and value == 0):
                raise RuntimeError('typed decode integer bound')
            return -value if negative else value
        if tag == 115 or tag == 98:
            size = number(58)
            if size > 4 * MAX_STRING_CHARS or cursor + size > len(raw):
                raise RuntimeError('typed decode string size')
            value = raw[cursor:cursor + size]
            cursor += size
            if tag == 98:
                if size > MAX_BYTES:
                    raise RuntimeError('typed decode bytes bound')
                return value
            value = value.decode('utf-8')
            if len(value) > MAX_STRING_CHARS:
                raise RuntimeError('typed decode characters bound')
            return value
        if tag == 100 or tag == 116 or tag == 108:
            size = number(58)
            if size > MAX_CONTAINER:
                raise RuntimeError('typed decode collection size')
            if tag == 100:
                output, previous = {}, None
                for _ in range(size):
                    key = item(depth + 1)
                    if type(key) is not str or (previous is not None and key <= previous):
                        raise RuntimeError('typed decode dictionary ordering')
                    previous = key
                    output[key] = item(depth + 1)
                return output
            output = [item(depth + 1) for _ in range(size)]
            return tuple(output) if tag == 116 else output
        raise RuntimeError('typed decode unknown tag')

    result = item(0)
    if cursor != len(raw):
        raise RuntimeError('typed decode trailing data')
    return result
