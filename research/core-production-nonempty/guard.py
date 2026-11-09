"""Exact target-window admission for the retained capped Gaussian carve.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This is input-independent source geometry, not an online payload primitive.
"""
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


def ceil_div(numerator, denominator):
    need(type(numerator) is int and type(denominator) is int and denominator > 0,
         'exact integer ceiling division')
    return -((-numerator) // denominator)


@dataclass(frozen=True)
class Window:
    source_size: int
    excess: int
    start: int
    length: int

    def __post_init__(self):
        need(all(type(x) is int for x in self.__dict__.values()), 'integer source geometry')
        need(0 < self.excess < self.source_size, 'retained source/excess domain')
        need(self.length > 0 and 0 <= self.start < self.start + self.length
             <= self.source_size + self.excess, 'ordinary original target window')


def phase_cut(source_size, excess, phase):
    need(0 <= phase <= excess + 1, 'original source phase cut')
    if phase == 0:
        return 0
    if phase == excess + 1:
        return source_size
    return ceil_div(source_size * (2 * phase - 1), 2 * excess)


def longest_run(window):
    """Maximum phase-pure selected run in the original target interval.

    Uses a fixed number of integer operations; source periods and phase cells
    are never enumerated. Returns exact source endpoints as a reviewable witness.
    """
    s, e, a, length = (window.source_size, window.excess, window.start, window.length)
    target = s + e
    first = ceil_div(s * (2 * a - 1), 2 * target)
    stop = ceil_div(s * (2 * (a + length) - 1), 2 * target)
    need(0 <= first <= stop <= s, 'inverse selected-index interval')
    if first == stop:
        return {'maximum': 0, 'first_source': first, 'stop_source': stop,
                'first_phase': None, 'last_phase': None, 'complete_middle_cells': 0}
    left_phase = (2 * e * first + s) // (2 * s)
    right_phase = (2 * e * (stop - 1) + s) // (2 * s)
    if left_phase == right_phase:
        maximum = stop - first
        middle_cells = 0
    else:
        left_end = phase_cut(s, e, left_phase + 1)
        right_start = phase_cut(s, e, right_phase)
        maximum = max(left_end - first, stop - right_start)
        middle_cells = right_phase - left_phase - 1
        if middle_cells:
            lower = s // e
            middle_total = right_start - left_end
            need(middle_cells * lower <= middle_total <= middle_cells * (lower + 1),
                 'two possible complete interior phase lengths')
            maximum = max(maximum, lower + int(middle_total > middle_cells * lower))
    return {'maximum': maximum, 'first_source': first, 'stop_source': stop,
            'first_phase': left_phase, 'last_phase': right_phase,
            'complete_middle_cells': middle_cells}


def has_interior(window, width, cap):
    need(type(width) is int and width >= 1, 'positive retained physical carve width')
    need(type(cap) is int and cap >= 1 and cap & (cap - 1) == 0
         and 2 * cap <= window.source_size, 'admitted dyadic source interior cap')
    return longest_run(window)['maximum'] > 6 * width


def uniform_guard(source_size, excess, width, length, cap):
    """Sufficient for every original start; no per-context scan or cache."""
    Window(source_size, excess, 0, length)
    need(type(width) is int and width >= 1, 'positive retained physical carve width')
    need(type(cap) is int and cap >= 1 and cap & (cap - 1) == 0
         and 2 * cap <= source_size, 'admitted dyadic source interior cap')
    return source_size >= excess * (6 * width + 1) and length >= 12 * width + 2
