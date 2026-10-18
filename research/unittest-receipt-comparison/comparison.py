"""Byte-preserving comparison keys for standard unittest stderr trailers.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
Only a syntactically recognized final elapsed-time value may differ. This
does not authenticate the producer of the bytes or establish that tests pass.
"""
import re

POLICY = "unittest-final-elapsed-bytes-v1"

# TextTestResult.printErrors and TextTestRunner.run in CPython use this
# separator and a three-decimal elapsed value. Preserve the line ending,
# count, status, all diagnostics and all other bytes. An unfamiliar/custom
# trailer is compared raw; it never gets a more permissive fallback.
TRAILER = re.compile(
    rb"(?m)^-{70}(?P<nl>\r?\n)"
    rb"Ran (?P<count>0|[1-9][0-9]*) (?P<noun>tests?) in "
    rb"(?P<elapsed>[0-9]+\.[0-9]{3})s(?P=nl)(?P=nl)"
    rb"(?:OK|FAILED)(?: \([^\r\n]*\))?(?P=nl)\Z"
)


def elapsed_span(data):
    """Return the recognized final timing span, or None; never decode bytes."""
    if type(data) is not bytes:
        raise TypeError("captured stderr must be bytes")
    match = TRAILER.search(data)
    if match is None:
        return None
    count = match.group("count")
    noun = b"test" if count == b"1" else b"tests"
    if match.group("noun") != noun:
        return None
    return match.span("elapsed")


def comparison_key(data):
    """An injective encoding of every byte outside the permitted timing span.

    Distinct raw/summary tags prevent an unrecognized literal marker from
    colliding with normalized output. The prefix length keeps the two retained
    slices unambiguous even if diagnostics contain arbitrary marker bytes.
    """
    span = elapsed_span(data)
    if span is None:
        return b"raw\0" + data
    start, end = span
    return b"summary\0" + start.to_bytes(8, "big") + data[:start] + data[end:]
