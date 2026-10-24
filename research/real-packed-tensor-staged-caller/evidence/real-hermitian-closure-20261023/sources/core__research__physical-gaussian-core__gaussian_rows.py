"""Linear sequential row movement preserving every bit within each record."""
from gaussian_sources import active
active()
from cardinal_counts import Count
from compact_counts import copy_bits
from router_metadata import indices, owned
from words import BLANK, need


def reverse_records(source, destination, length, record_bits):
    source.rewind()
    try:
        with owned(Count.product(length, record_bits)) as (total,):
            for _ in indices(total):
                need(source.read() in (0, 1), "complete reversal source")
                source.step(1)
        need(source.read() == BLANK, "exact reversal source extent")
        for _ in indices(length):
            for _ in indices(record_bits):
                source.step(-1)
            copy_bits(source, destination, record_bits)
            for _ in indices(record_bits):
                source.step(-1)
    finally:
        source.rewind()
        destination.rewind()


def magnitude_length(value):
    from words import RIGHT
    result = Count.literal(0)
    value.rewind()
    try:
        while value.read() != RIGHT:
            need(value.read() in (0, 1), "canonical measured magnitude")
            result.increment()
            value.step(1)
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()
