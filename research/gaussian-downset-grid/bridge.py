"""Bind the two unchanged Gaussian callers to the certified Full allocator.

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0.
"""
from types import FunctionType


def bind(gaussian, raw_gaussian, allocation):
    def function(original, **changes):
        namespace = dict(original.__globals__)
        namespace.update(changes)
        clone = FunctionType(original.__code__, namespace, original.__name__,
                             original.__defaults__, original.__closure__)
        clone.__kwdefaults__ = original.__kwdefaults__
        return clone

    # The method bodies and every inherited validation remain the original code.
    normalized = type('DownsetGaussian', (gaussian.Gaussian,), {
        'compile_root': function(gaussian.Gaussian.compile_root, allocation=allocation)})
    raw = type('DownsetRawGaussian', (raw_gaussian.RawGaussian,), {
        '__init__': function(raw_gaussian.RawGaussian.__init__, allocation=allocation,
                             Gaussian=normalized)})
    return normalized, raw
