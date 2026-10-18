#!/usr/bin/env python3
"""Independent finite lifetime census using integer array identities.

No source runner, primary verifier or predecessor checker is imported. This
enumerates the explicitly stated allocation/lifetime model; it is algebraic
corroboration, not a runtime trace, formal proof or native action-scratch bound.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Ledger:
    """Lengths indexed by fresh integers; aliases share one integer."""

    def __init__(self):
        self.lengths = {}
        self.roots = {}
        self.cuts = 0
        self.caller_peak = self.joint_peak = 0
        self.prefix_peak = self.copy_peak = 0

    def fresh(self, length):
        require(length >= 1, "every array contains LEFT")
        identity = len(self.lengths) + 1
        self.lengths[identity] = length
        return identity

    def grow(self, identity):
        self.lengths[identity] += 1

    def observe(self, phase, pending=(), private=()):
        caller = {identity for identity in self.roots.values()
                  if identity is not None} | set(pending)
        owned = set(private)
        require(not caller & owned, "action storage excludes caller identities")
        caller_size = sum(self.lengths[identity] for identity in caller)
        joint_size = caller_size + sum(self.lengths[identity] for identity in owned)
        self.cuts += 1
        self.caller_peak = max(self.caller_peak, caller_size)
        self.joint_peak = max(self.joint_peak, joint_size)
        if phase == "prefix_return":
            self.prefix_peak = max(self.prefix_peak, caller_size)
        if phase == "copy_complete":
            self.copy_peak = max(self.copy_peak, caller_size)


def simulate(n, f, q, passes, source_pad, directory_pad, scratch, alignment):
    """Perform structural states, retaining lengths across clear operations.

    Synthetic private scratch is one S-cell array coexisting with the complete
    result at either the final call or only the very first call. S=0 omits it.
    Old entries in lengths are merely model history, not counted live roots.
    """
    require(n >= 1 and f >= 1 and q >= 2 and passes >= 2, "positive domain")
    require(source_pad >= 0 and directory_pad >= 0 and scratch >= 0, "padding")
    require(alignment in ("final", "first"), "scratch placement")
    ledger = Ledger()
    roots = ledger.roots
    roots["source"] = ledger.fresh(n * f + 1 + source_pad)
    roots["directory"] = ledger.fresh(n * (q - 1) + 1 + directory_pad)
    roots["first"] = ledger.fresh(q)
    roots["current"] = roots["source"]
    ledger.observe("entry")
    for turn in range(passes):
        output = ledger.fresh(1)
        # Previous output remains bound, but is an alias of current.
        ledger.observe("output_factory_return", pending=(output,))
        roots["output"] = output
        ledger.observe("output_store")
        for prefix in range(n):
            fields = ledger.fresh(1)
            ledger.observe("prefix_reader_entry", pending=(fields,))
            for _ in range(q - 1):
                ledger.grow(fields)
                ledger.observe("prefix_reader_append", pending=(fields,))
            ledger.observe("prefix_return", pending=(fields,))
            roots["fields"] = fields
            ledger.observe("fields_store")
            local = ledger.fresh(1)
            # Both preceding local and changed survive RHS evaluation.
            ledger.observe("local_factory_return", pending=(local,))
            roots["local"] = local
            ledger.observe("local_store")
            roots["changed"] = None
            ledger.observe("changed_reset")
            for _ in range(f):
                ledger.grow(local)
                ledger.observe("local_copy")
            result = ledger.fresh(1)
            ledger.observe("action_result_constructor", private=(result,))
            for _ in range(f):
                ledger.grow(result)
                ledger.observe("action_result_append", private=(result,))
            aligned = (turn, prefix) == (passes - 1, n - 1)
            early = (turn, prefix) == (0, 0)
            if scratch and (aligned if alignment == "final" else early):
                temporary = ledger.fresh(scratch)
                ledger.observe("action_scratch", private=(result, temporary))
                # Private temporary loses its last model owner before return.
                ledger.observe("action_scratch_release", private=(result,))
            ledger.observe("action_return", pending=(result,))
            roots["changed"] = result
            ledger.observe("changed_store")
            for _ in range(f):
                ledger.grow(output)
                ledger.observe("output_copy")
            ledger.observe("copy_complete")
            # Clear changes symbols, never array length or root identity.
            for phase in ("changed_clear", "local_clear", "fields_clear"):
                ledger.observe(phase)
        require(ledger.lengths[output] == n * f + 1, "complete output extent")
        if roots["current"] != roots["source"]:
            ledger.observe("current_clear")
        roots["current"] = output
        ledger.observe("current_store")
    ledger.observe("return")
    return ledger


def check_all():
    cases = runs = cuts = 0
    prefix_failures = overcharges = unaligned_strict = 0
    comparisons = {"F<Q": 0, "F=Q": 0, "F>Q": 0}
    for n, f, q, passes, source_pad, directory_pad in itertools.product(
            range(1, 6), range(1, 8), range(2, 8), (2, 3), (0, 5), (0, 3)):
        k = n * f + 1 + source_pad
        d = n * (q - 1) + 1 + directory_pad
        reader = k + (2 * n + 1) * f + 4 + d + 3 * q
        copier = k + (2 * n + 2) * f + 4 + d + 2 * q
        structural = k + (2 * n + 1) * f + 4 + d + 2 * q + max(q, f)
        action_base = k + 2 * n * f + 3 + d + 2 * q
        for scratch in (0, 1, max(f, q) + 5):
            cases += 1
            comparisons["F<Q" if f < q else "F=Q" if f == q else "F>Q"] += 1
            allowance = f + 1 + scratch
            joined = max(structural, action_base + allowance)
            final = simulate(n, f, q, passes, source_pad, directory_pad,
                             scratch, "final")
            first = simulate(n, f, q, passes, source_pad, directory_pad,
                             scratch, "first")
            for ledger in (final, first):
                runs += 1
                cuts += ledger.cuts
                require(ledger.prefix_peak == reader, "prefix-return identity")
                require(ledger.copy_peak == copier, "copy-completion identity")
                require(ledger.caller_peak == structural, "whole caller maximum")
                require(ledger.joint_peak <= joined, "uniform private allowance")
            require(final.joint_peak == joined, "aligned private peak attains bound")
            require(structural - reader == max(0, f - q), "prefix-only deficit")
            if f > q:
                require(reader < final.caller_peak, "reject prefix-only maximum")
                prefix_failures += 1
            # Adding private A to the caller maximum combines different cuts.
            require(structural + allowance > final.joint_peak,
                    "reject max-plus-A as an exact maximum")
            overcharges += 1
            if scratch > max(f, q):
                require(first.joint_peak < joined,
                        "upper-bound allowance need not attain its joint bound")
                unaligned_strict += 1
    return {
        "status": "PASS_INDEPENDENT_LIFETIME_CENSUS",
        "scope": "finite integer-identity model; no native runtime or formal proof",
        "parameter_cases": cases,
        "simulated_runs": runs,
        "observed_model_cuts": cuts,
        "comparison_cases": comparisons,
        "controls": {
            "prefix_only_underestimates": prefix_failures,
            "max_plus_A_strict_overcharges": overcharges,
            "unaligned_peak_strict_upper_bounds": unaligned_strict,
        },
    }


if __name__ == "__main__":
    print(json.dumps(check_all(), sort_keys=True))
