#!/usr/bin/env python3
"""Reuse PR589's validated geometry while retaining its complete word checks.

Cinna Davis (1337isnot1337), with substantial OpenAI Codex assistance.
Apache-2.0. The frozen checker retains eumemic's original attribution.
"""
import copy
import hashlib
import json
from pathlib import Path
import types


CHECKER_SHA256 = "af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e"
GATE_KEYS = frozenset(("D", "A", "B", "C"))


class CheckerIntegrityError(RuntimeError):
    """The prepared path is valid only for the reviewed checker bytes."""


def _signature(word):
    # Conservatively include every other field, even annotations the owner
    # currently ignores. JSON list order and scalar types are preserved.
    return json.dumps({k: v for k, v in word.items() if k not in GATE_KEYS},
                      sort_keys=True, separators=(",", ":"), allow_nan=False)


class PreparedBitChecker:
    """One immutable geometry template; no cache of candidate word results.

    Inputs are JSON trees. A different non-gate field invokes the original full
    checker. Its Reject exceptions and H/C flags have their original meaning;
    callers must inspect those flags rather than equating no exception with
    interface admission. Returned Word objects and receipts may be mutated
    without contaminating later checks. Instances are intended for serial use.
    """

    def __init__(self, checker_path, template):
        self._path = Path(checker_path).resolve()
        source = self._assert_source()
        self._owner = types.ModuleType("_prepared_bit_owner")
        # Execute the bytes we actually hashed; do not consult .pyc caches.
        exec(compile(source, str(self._path), "exec"), self._owner.__dict__)
        snapshot = copy.deepcopy(template)
        self._signature = _signature(snapshot)
        self._geometry = self._owner.Word(snapshot)
        self._labels = self._geometry.labels()
        self.geometry_hits = 0
        self.full_fallbacks = 0

    def _assert_source(self):
        source = self._path.read_bytes()
        if hashlib.sha256(source).hexdigest() != CHECKER_SHA256:
            raise CheckerIntegrityError("frozen PR589 checker SHA256 mismatch")
        return source

    @property
    def reject_type(self):
        """Reject class from this instance's pinned checker module."""
        return self._owner.Reject

    def check(self, word):
        self._assert_source()
        candidate = copy.deepcopy(word)
        if _signature(candidate) != self._signature:
            self.full_fallbacks += 1
            return self._owner.check(candidate)
        self.geometry_hits += 1
        W = copy.deepcopy(self._geometry)
        W.w = candidate
        # Exactly the original check(w) tail: nothing about a candidate's
        # gates, totals, endpoints or interface is taken from the template.
        fl = W.full()
        fl["totals"] = W.totals()
        H, C, info = W.interface()
        return W, copy.deepcopy(self._labels), fl, H, C, info
