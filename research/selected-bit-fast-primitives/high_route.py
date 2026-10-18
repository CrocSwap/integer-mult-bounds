"""Complete canonical high cubes through fixed affine column factors."""
import stage_sources
stage_sources.activate()
from cardinal_counts import Count
from encoded import fixed_power
import kernels
from routes import copy_rows
from session import initialize_marker
from words import BLANK, Ring, need


def extents(modulus, fibre, dimension, first, second=None):
    fields = dimension*dimension
    if second is None:
        before = fixed_power(modulus, first)
        power = fixed_power(modulus, fields-first-1)
        try:
            return before, Count.product(power, fibre)
        finally:
            power.close()
    first, second = sorted((first, second))
    need(first != second, "two distinct high fields")
    before = fixed_power(modulus, first)
    middle = fixed_power(modulus, second-first-1)
    power = fixed_power(modulus, fields-second-1)
    try:
        return before, middle, Count.product(power, fibre)
    finally:
        power.close()


def apply(source, operation, route, ring, modulus, fibre, adapter, factory):
    kind, target, *arguments = operation
    if kind in ("swap", "add"):
        control = arguments[0]
        before, middle, suffix = extents(modulus, fibre, route.dimension, target, control)
        current = source
        try:
            if kind == "swap":
                return adapter.swap(source, ring, route.q, before, middle, suffix)
            reversed_fields = control > target
            if reversed_fields:
                current = adapter.swap(source, ring, route.q, before, middle, suffix)
            following = kernels.added(current, ring, before, middle, suffix, arguments[1])
            if current is not source:
                current.clear()
            current = following
            if reversed_fields:
                following = adapter.swap(current, ring, route.q, before, middle, suffix)
                current.clear()
                current = following
            result, current = current, None
            return result
        finally:
            before.close()
            middle.close()
            suffix.close()
            if current is not None and current is not source:
                current.clear()
    before, suffix = extents(modulus, fibre, route.dimension, target)
    try:
        if kind in ("double", "half"):
            return kernels.doubled(source, ring, before, suffix, factory, kind == "half")
        if kind == "negate":
            return kernels.negated(source, ring, route.q, before, suffix)
        need(kind == "translate", "closed high-factor vocabulary")
        return kernels.translated(source, ring, route.q, before, suffix, arguments[0])
    finally:
        before.close()
        suffix.close()


def execute(source, route, context, fibre, adapter, factory):
    need((route.q, route.dimension) == (context.q, context.dimension), "route/context binding")
    operations = adapter.registry.compile(route)
    current = factory()
    source.rewind()
    ring = modulus_word = None
    modulus = Count(context.cap)
    bank = adapter.high_bank
    try:
        copy_rows(source, current, context.highs, fibre)
        need(source.read() == BLANK, "complete source high cube")
        source.rewind()
        current.rewind()
        if context.raw.compare(context.cap, context.ring.one) > 0:
            for word in (*bank.words, bank.template):
                initialize_marker(word.tape)
            bank.prepare(modulus)
            modulus_word = bank.load(modulus)
            ring = Ring(modulus_word)
            for operation in operations:
                following = apply(current, operation, route, ring, modulus, fibre, adapter, factory)
                current.clear()
                current = following
        result, current = current, None
        return result
    finally:
        source.rewind()
        if current is not None:
            current.clear()
        if ring is not None:
            ring.close()
            bank.free(modulus_word)
            bank.erase_owned()
        modulus.close()
