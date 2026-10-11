"""Bind generated gzip words to their exact, separately verified plain bytes."""
import zlib


def single_member_payload(blob, expected):
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    payload = decoder.decompress(blob, len(expected) + 1)
    assert not decoder.unconsumed_tail, 'Oversized or unconsumed gzip data'
    assert decoder.eof, 'Incomplete gzip member'
    assert not decoder.unused_data, 'Extra gzip member or trailing bytes'
    assert payload == expected, 'Exact plain word bytes differ'
    return payload


def assert_word_identity(left, right):
    plain_left = left.with_name('word.json').read_bytes()
    plain_right = right.with_name('word.json').read_bytes()
    assert plain_left == plain_right, 'Exact plain source words differ'
    assert single_member_payload(left.read_bytes(), plain_left) == single_member_payload(
        right.read_bytes(), plain_right
    ), 'Exact word payloads differ'
