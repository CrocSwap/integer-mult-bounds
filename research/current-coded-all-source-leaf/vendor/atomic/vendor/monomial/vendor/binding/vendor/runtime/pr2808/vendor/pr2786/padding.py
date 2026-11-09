"""Compatible fresh-row padding on the retained sequential binary tapes.

The caller supplies canonical positive Count operands and a completed callee.
Only finite flags, not decoded cardinalities or payloads, control these scans.
"""

from cardinal_counts import Count, positive
from records import Tape
from stream import Counter
from words import BLANK, ONE, ZERO, need


def plan_rows(rows, stock):
    """Return owned Counts (ceil(rows/stock)*stock, added), requiring rows>=stock.

    Each main iteration consumes one of rows. Each final iteration consumes
    one of fewer than stock unused group positions. No payload is accessed.
    """
    positive(rows)
    positive(stock)
    remaining, group = Counter(rows), Counter(stock)
    padded, added = Count.literal(0), Count.literal(0)
    completed_group = False
    try:
        while not remaining.finished:
            remaining.decrement()
            group.decrement()
            padded.increment()
            if group.finished:
                completed_group = True
                if not remaining.finished:
                    group.close()
                    group = Counter(stock)
        need(completed_group, "row capacity must cover at least one stock group")
        while not group.finished:
            group.decrement()
            padded.increment()
            added.increment()
        return padded, added
    except BaseException:
        padded.close()
        added.close()
        raise
    finally:
        remaining.close()
        group.close()


def scan_rows(source, output, rows, body, mode):
    """Process exactly rows*body cells at the current prefix, using three modes."""
    need(mode in ("copy", "zero", "discard"), "finite row-scan mode")
    outer = Counter(rows)
    try:
        while not outer.finished:
            inner = Counter(body)
            try:
                while not inner.finished:
                    if mode == "zero":
                        output.append(ZERO)
                    else:
                        bit = source.read()
                        need(bit in (ZERO, ONE), "complete binary row payload")
                        if mode == "copy":
                            output.append(bit)
                        else:
                            need(bit == ZERO, "callee must leave added rows zero")
                        source.step(1)
                    inner.decrement()
            finally:
                inner.close()
            outer.decrement()
    finally:
        outer.close()


def transform(source, prefixes, rows, added, body, restricting=False):
    """Pad or restrict [prefixes][rows][body], returning a fresh owned tape.

    Source enters at its first cell. Every count loop has its encoded finite
    bound. For restriction the source instead has rows+added rows per prefix.
    """
    for count in (prefixes, rows, body):
        positive(count)
    need(isinstance(added, Count), "encoded padding count")
    need(source.head == 1, "row scan enters at its local left boundary")
    output, outer = Tape(), Counter(prefixes)
    try:
        while not outer.finished:
            scan_rows(source, output, rows, body, "copy")
            scan_rows(source, output, added, body, "discard" if restricting else "zero")
            outer.decrement()
        need(source.read() == BLANK, "exact complete row extent")
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        outer.close()
        source.rewind()


def complete(source, prefixes, rows, stock, body, callee):
    """Invoke a source-preserving, row-pointwise callee on compatible fresh rows.

    The callee borrows the padded input and row count, returns a DISTINCT owned
    output, restores all heads, and closes its own work even on failure. Its
    endpoint must preserve genuine row ordinals and permute within each row.
    Runtime zero checks do not establish that semantic callee premise.
    """
    padded_rows, added = plan_rows(rows, stock)
    padded = returned = None
    try:
        padded = transform(source, prefixes, rows, added, body)
        candidate = callee(padded, padded_rows)
        need(
            candidate is not padded and candidate is not source,
            "callee returns distinct owned output, never a borrowed input",
        )
        returned = candidate
        need(isinstance(returned, Tape), "callee returns a payload tape")
        need(
            padded.head == returned.head == padded_rows.tape.head == 1,
            "completed callee restores borrowed and output heads",
        )
        padded.clear()
        padded = None
        return transform(returned, prefixes, rows, added, body, restricting=True)
    finally:
        if returned is not None and isinstance(returned, Tape):
            returned.clear()
        if padded is not None:
            padded.clear()
        padded_rows.close()
        added.close()
