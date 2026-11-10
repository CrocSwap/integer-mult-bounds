# SPDX-License-Identifier: GPL-3.0-or-later
# Source-derived translation of GCC 13.3 gcc/gcc.cc:for_each_path.
# Original GCC source Copyright (C) 1987-2023 Free Software Foundation, Inc.
# Retained source identity and definite Ubuntu patch comparison are recorded in
# SOURCE-COMPARISON-v1.json. See COPYING3 for license and warranty terms.
"""Bounded, pure ordered prefix spellings; no configuration constructor.

The private configuration/relocation phase must independently construct the
stable prefix tuple, its insertion/priority order, phase, suffixes and multilib
selection from authenticated applied source and generated configured data.
This primitive neither constructs nor authenticates that state. A caller's
supplied tuple is never accepted as a complete effective configuration.

No filesystem queries, callbacks, access outcomes, source selection, pathname
normalization, deduplication or execution occur here. A separate source-bound
consumer must stop at its first successful candidate and retain actual failed
access outcomes without treating every failure as absence. Early and late
driver prefix states and Ubuntu file_at_path filename expansion stay separate.

Input strings stand for the private state's exact C-string spellings; the
upstream construction must establish that character/byte representation.
Literal '..', repeated separators, duplicate visits, None versus '', and the
source's distinct compiler/OS multilib skip flags are preserved.
"""

MAX_TEXT = 8192
MAX_PREFIXES = 1024
MAX_VISITS = 1024
MAX_AGGREGATE_TEXT = 524288


class QueryFrontierLimit(ValueError):
    """Input or output is outside the explicitly bounded partial component."""


def _text(value):
    if type(value) is not str or len(value) > MAX_TEXT or "\0" in value:
        raise QueryFrontierLimit("exact bounded non-NUL query text required")
    return value


def _join(*parts):
    # Check total length before allocating the concatenated spelling.
    length = 0
    for part in parts:
        length += len(part)
        if length > MAX_TEXT:
            raise QueryFrontierLimit("expanded query exceeds per-string bound")
    return "".join(parts)


def gcc13_prefix_visits(
    prefixes, machine_suffix, just_machine_suffix,
    multilib_dir, multilib_os_dir, multiarch_dir, do_multi,
):
    """Return ordered visits conditional on privately constructed driver state.

    `prefixes` is an exact tuple of exact tuples:
        (prefix_text, require_machine_suffix, use_os_multilib)
    require_machine_suffix is integer 0, 1, or 2. use_os_multilib and do_multi
    are exact booleans. Optional directory suffixes use None for a null C
    pointer; an empty string is a non-null pointer and remains consequential.

    Validation of all input rows is eager. Emission bounds are checked before
    allocating each result. QueryFrontierLimit is an unresolved frontier, not
    successful exhaustion. Exhaustion alone establishes no selected file or
    effective configuration and never establishes full C05.
    """
    if type(prefixes) is not tuple or len(prefixes) > MAX_PREFIXES:
        raise QueryFrontierLimit("bounded private stable prefix tuple required")
    if type(do_multi) is not bool:
        raise QueryFrontierLimit("do_multi must be an exact boolean")
    _text(machine_suffix)
    _text(just_machine_suffix)
    total = len(machine_suffix) + len(just_machine_suffix)
    for value in (multilib_dir, multilib_os_dir, multiarch_dir):
        if value is not None:
            _text(value)
            total += len(value)
    for row in prefixes:
        if type(row) is not tuple or len(row) != 3:
            raise QueryFrontierLimit("prefix row shape differs")
        prefix, require, use_os = row
        _text(prefix)
        if type(require) is not int or require not in (0, 1, 2):
            raise QueryFrontierLimit("machine-suffix policy differs")
        if type(use_os) is not bool:
            raise QueryFrontierLimit("OS-multilib policy differs")
        total += len(prefix)
        if total > MAX_AGGREGATE_TEXT:
            raise QueryFrontierLimit("private prefix input aggregate bound")
    if total > MAX_AGGREGATE_TEXT:
        raise QueryFrontierLimit("private suffix input aggregate bound")

    multi = None
    if do_multi and multilib_dir is not None and multilib_dir != ".":
        multi = _join(multilib_dir, "/")
    os_multi = None
    if do_multi and multilib_os_dir is not None and multilib_os_dir != ".":
        os_multi = _join(multilib_os_dir, "/")
    arch = None if multiarch_dir is None else _join(multiarch_dir, "/")

    def visits():
        nonlocal multi, os_multi
        skip_multi, skip_os = False, False
        count, emitted_text = 0, 0

        def emit(*parts):
            nonlocal count, emitted_text
            length = sum(len(part) for part in parts)
            if length > MAX_TEXT:
                raise QueryFrontierLimit("expanded query exceeds per-string bound")
            if count >= MAX_VISITS or emitted_text + length > MAX_AGGREGATE_TEXT:
                raise QueryFrontierLimit("ordered query output bound")
            count += 1
            emitted_text += length
            return "".join(parts)

        while True:
            for prefix, require, use_os in prefixes:
                if not skip_multi:
                    yield emit(prefix, machine_suffix, multi if multi is not None else "")
                if not skip_multi and require == 2:
                    yield emit(prefix, just_machine_suffix, multi if multi is not None else "")
                if not skip_multi and require == 0 and arch is not None:
                    yield emit(prefix, arch)
                skip_base = skip_os if use_os else skip_multi
                if require == 0 and not skip_base:
                    selected = os_multi if use_os else multi
                    yield emit(prefix, selected if selected is not None else "")
            if multi is None and os_multi is None:
                return
            if multi is None:
                skip_multi = True
            multi = None
            if os_multi is None:
                skip_os = True
            os_multi = None

    return visits()
