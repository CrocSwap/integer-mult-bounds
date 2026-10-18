"""Exact, all-column primitive replay of the two pinned JP8 scalar words.

The interpreter uses sparse Fraction rows and does not evaluate scalar macros as
an implementation shortcut.  Logical helpers enter arbitrarily and are restored;
eight centre registers and coefficient work enter arbitrarily and are erased.
Standard library only; checks stay active under ``python -I -O``.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json

from synth import lower, reference_lower

WORK = ("W", 0)
N = 716
V = 112
CENTRES = tuple(("C", i) for i in range(8))
PRIMITIVES = {"clear", "copy", "double", "halve", "negate", "add", "subtract"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def historical_lower(op):
    """Literal original clear/binary/Horner emitter, before PR696 copy removal."""
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        return [("copy", target, tuple(op[2]))]
    if tag == "scale":
        q = Q(op[2], op[3])
        a, b = abs(q.numerator), q.denominator
        require(a and a & (a - 1) == 0 and b & (b - 1) == 0,
                "historical scale must be signed power of two")
        shift = a.bit_length() - b.bit_length()
        return ([("double" if shift > 0 else "halve", target)] * abs(shift)
                + ([("negate", target)] if q < 0 else []))
    require(tag == "add", "unknown scalar macro")
    source, q = tuple(op[2]), Q(op[3], op[4])
    require(q and q.denominator & (q.denominator - 1) == 0,
            "historical addition must be nonzero dyadic")
    require(source != target and WORK not in (target, source), "scalar alias")
    word = [("clear", WORK)]
    for index, bit in enumerate(bin(abs(q.numerator))[2:]):
        if index:
            word.append(("double", WORK))
        if bit == "1":
            word.append(("add", WORK, source))
    word.extend([("halve", WORK)] * (q.denominator.bit_length() - 1))
    word.extend([("add" if q > 0 else "subtract", target, WORK),
                 ("clear", WORK)])
    return word


def baseline_count(op):
    tag = op[0]
    if tag in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if tag == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    if tag == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def initial_rows():
    rows = {("L", r): {r: Q(1)} for r in range(N)}
    rows.update({register: {N + i: Q(1)}
                 for i, register in enumerate((WORK,) + CENTRES)})
    return rows


class Interpreter:
    def __init__(self):
        self.rows = initial_rows()
        self.tags = Counter()
        self.denominator_exponent = 0
        self.maximum_row_l1 = Q(1)
        self.word_hash = hashlib.sha256()
        self.source_reads = 0
        self.all_register_reads = 0
        self.instructions = 0

    def step(self, primitive, frame, event_index, macro_source=None):
        tag, target = primitive[:2]
        target = tuple(target)
        require(tag in PRIMITIVES, "unknown primitive: " + str(tag))
        require(target in self.rows, "unknown target register")
        require(len(primitive) == (3 if tag in ("copy", "add", "subtract") else 2),
                "primitive arity")
        reads = []
        if tag != "clear":
            if tag != "copy":
                reads.append(target)
            if tag in ("copy", "add", "subtract"):
                source = tuple(primitive[2])
                require(source in self.rows, "unknown source register")
                require(source != target, "primitive source alias")
                reads.append(source)
        self.all_register_reads += len(reads)
        self.source_reads += reads.count(macro_source) if macro_source is not None else 0
        if tag == "clear":
            self.rows[target] = {}
        elif tag == "copy":
            self.rows[target] = self.rows[source].copy()
        elif tag in ("double", "halve", "negate"):
            q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            self.rows[target] = {j: q * x for j, x in self.rows[target].items()}
        else:
            target_row = self.rows[target]
            for j, x in self.rows[source].items():
                value = target_row.get(j, Q(0)) + (x if tag == "add" else -x)
                if value:
                    target_row[j] = value
                else:
                    target_row.pop(j, None)
        # Only the written row can introduce a denominator not already seen.
        for x in self.rows[target].values():
            denominator = x.denominator
            require(denominator & (denominator - 1) == 0, "nondyadic trace row")
            self.denominator_exponent = max(self.denominator_exponent,
                                            denominator.bit_length() - 1)
        # Initial basis rows have norm one. Only this written row can change
        # the maximum; this measures scalar coordinates, not physical frames.
        self.maximum_row_l1 = max(self.maximum_row_l1,
                                  sum((abs(x) for x in self.rows[target].values()), Q(0)))
        self.tags[tag] += 2  # same circuit separately on real and imaginary parts
        self.instructions += 1
        self.word_hash.update(canonical([event_index, frame, primitive]) + b"\n")

    def run_macro(self, op, word, frame, index):
        tag, target = op[0], tuple(op[1])
        source = tuple(op[2]) if tag in ("add", "copy") else None
        require(target in self.rows and (source is None or source in self.rows),
                "unknown scalar register")
        require(WORK not in (target, source), "coefficient work used by scalar macro")
        allowed_writes = {target, WORK} if tag == "add" else {target}
        allowed_reads = allowed_writes | ({source} if source is not None else set())
        for primitive in word:
            require(tuple(primitive[1]) in allowed_writes, "write outside scalar macro")
            if len(primitive) == 3:
                require(tuple(primitive[2]) in allowed_reads, "read outside scalar macro")
            self.step(primitive, frame, index, source)
        if tag == "add":
            require(not self.rows[WORK], "coefficient work survived addition macro")

    def endpoint(self, orientation):
        for r in range(N):
            expected = {r: Q(1)}
            if orientation == "forward" and V <= r < 2 * V:
                expected[r - V] = Q(1)
            elif orientation == "backward" and r < V:
                expected[r + V] = Q(-1)
            require(self.rows[("L", r)] == expected,
                    f"{orientation}: full exact input-column map at L{r}")
        require(all(not self.rows[r] for r in (WORK,) + CENTRES),
                "arbitrary private input columns survived endpoint")

    def receipt(self):
        return {
            "real_primitives": 2 * self.instructions,
            "primitive_tags": dict(sorted(self.tags.items())),
            "primitive_word_sha256": self.word_hash.hexdigest(),
            "maximum_fractional_denominator_exponent": self.denominator_exponent,
            "maximum_scalar_prefix_row_l1": str(self.maximum_row_l1),
            "real_macro_source_reads": 2 * self.source_reads,
            "real_total_register_reads": 2 * self.all_register_reads,
        }


def source_reads(word, op):
    if op[0] not in ("add", "copy"):
        return 0
    source = tuple(op[2])
    return sum(1 for primitive in word if len(primitive) == 3
               and tuple(primitive[2]) == source)


def replay_orientation(orientation, events, checks, inherited, entries):
    interpreters = {name: Interpreter() for name in ("historical", "pr696", "replacement")}
    paid = Counter()
    baseline = macros = additions = units = changed = 0
    non_scalar_hash = hashlib.sha256()
    replacement_non_scalar_hash = hashlib.sha256()
    frame_hash = hashlib.sha256()
    replacement_frame_hash = hashlib.sha256()
    non_scalar_count = 0
    env = {register: Q(1) for register in initial_rows()}
    peak = Q(1)
    changed_coefficients = {}
    boundary_comparisons = 0
    for index, event in enumerate(events):
        if event[0] != "scalar":
            require(event[0] in ("climb", "center", "phase", "adapter", "residual_adapter"),
                    "unknown event")
            if event[0] == "climb":
                paid[event[5]] += 1
            elif event[0] == "center":
                paid[event[4]] += 1
            payload = canonical([index, event]) + b"\n"
            non_scalar_hash.update(payload)
            # The transformed stream emits exactly the original event at this slot.
            replacement_event = event
            replacement_non_scalar_hash.update(canonical([index, replacement_event]) + b"\n")
            non_scalar_count += 1
            continue
        require(len(event) == 3, "scalar event arity")
        op, frame = event[1:]
        tag, target = op[0], tuple(op[1])
        words = {"historical": historical_lower(op), "pr696": reference_lower(op),
                 "replacement": lower(op, entries)}
        require(len(words["historical"]) == baseline_count(op), "historical emitter invoice")
        require(len(words["replacement"]) <= len(words["pr696"]), "replacement increased bill")
        baseline += 2 * baseline_count(op)
        macros += 1
        frame_hash.update(canonical([index, frame]) + b"\n")
        replacement_frame = frame
        replacement_frame_hash.update(canonical([index, replacement_frame]) + b"\n")
        if tag == "add":
            source, q = tuple(op[2]), Q(op[3], op[4])
            additions += 1
            units += abs(q) == 1
            peak = max(peak, abs(q.numerator) * env[source])
            env[target] += abs(q) * env[source]
        elif tag == "scale":
            env[target] *= abs(Q(op[2], op[3]))
        elif tag == "clear":
            env[target] = Q(0)
        elif tag == "copy":
            env[target] = env[tuple(op[2])]
        else:
            raise ValueError("unknown macro")
        peak = max(peak, env[target])
        if words["replacement"] != words["pr696"]:
            require(tag == "add", "changed non-addition macro")
            require(len(words["replacement"]) < len(words["pr696"]),
                    "changed word without strict saving")
            changed += 1
            coefficient = str(q)
            item = changed_coefficients.setdefault(coefficient, {
                "occurrences": 0,
                "pr696_real_primitives_per_macro": 2 * len(words["pr696"]),
                "replacement_real_primitives_per_macro": 2 * len(words["replacement"]),
                "pr696_real_source_reads_per_macro": 2 * source_reads(words["pr696"], op),
                "replacement_real_source_reads_per_macro": 2 * source_reads(words["replacement"], op),
            })
            item["occurrences"] += 1
        for name, interpreter in interpreters.items():
            interpreter.run_macro(op, words[name], frame, index)
        expected_row = interpreters["historical"].rows[target]
        for name in ("pr696", "replacement"):
            require(interpreters[name].rows[target] == expected_row,
                    f"{orientation} macro {index}: target differs from historical emitter")
            require(interpreters[name].rows[WORK] == interpreters["historical"].rows[WORK],
                    f"{orientation} macro {index}: coefficient work boundary differs")
        boundary_comparisons += 1
    for interpreter in interpreters.values():
        interpreter.endpoint(orientation)
    require(macros == checks["scalar_macros"], "source macro count")
    require(len(events) == checks["events"], "source event count")
    require(baseline == checks["real_component_primitive_bound"], "historical primitive receipt")
    require(dict(paid) == {int(k): value for k, value in checks["paid_profile"].items()},
            "paid profile changed")
    require(peak == Q(inherited["prefix_l1_upper"]), "inherited positive prefix envelope")
    require(non_scalar_hash.digest() == replacement_non_scalar_hash.digest(), "non-scalar event change")
    require(frame_hash.digest() == replacement_frame_hash.digest(), "scalar frame change")
    receipts = {name: interpreter.receipt() for name, interpreter in interpreters.items()}
    require(receipts["replacement"]["maximum_fractional_denominator_exponent"] <=
            receipts["pr696"]["maximum_fractional_denominator_exponent"] <=
            receipts["historical"]["maximum_fractional_denominator_exponent"],
            "scalar fractional guard increased")
    require(interpreters["replacement"].maximum_row_l1 <= interpreters["pr696"].maximum_row_l1
            <= interpreters["historical"].maximum_row_l1, "scalar prefix row-L1 maximum increased")
    require(peak < 2 ** inherited["charged_payload_bits"], "inherited payload bound exceeded")
    require(receipts["historical"]["real_primitives"] - receipts["pr696"]["real_primitives"]
            == 2 * (additions + units), "PR696 closed-form saving")
    return {
        "logical_input_columns": N,
        "arbitrary_private_input_columns": 9,
        "total_exact_input_columns": N + 9,
        "arbitrary_helper_columns_restored": N - 2 * V,
        "private_registers_erased": 9,
        "events": len(events),
        "scalar_macros": macros,
        "addition_macros": additions,
        "macro_boundaries_compared": boundary_comparisons,
        "addition_macros_with_coefficient_work_clear": additions,
        "changed_macros": changed,
        "changed_coefficients": dict(sorted(changed_coefficients.items(), key=lambda x: Q(x[0]))),
        "saved_real_primitives_vs_pr696": receipts["pr696"]["real_primitives"] - receipts["replacement"]["real_primitives"],
        "saved_real_primitives_vs_historical": baseline - receipts["replacement"]["real_primitives"],
        "extra_real_source_reads_vs_pr696": receipts["replacement"]["real_macro_source_reads"] - receipts["pr696"]["real_macro_source_reads"],
        "lowerings": receipts,
        "preserved_non_scalar_events": non_scalar_count,
        "non_scalar_event_indexed_sha256": non_scalar_hash.hexdigest(),
        "scalar_frame_indexed_sha256": frame_hash.hexdigest(),
        "paid_profile": {str(k): value for k, value in sorted(paid.items())},
        "retained_prefix_l1_upper": str(peak),
        "inherited_prefix_bits_upper": inherited["prefix_bits_upper"],
        "charged_payload_bits": inherited["charged_payload_bits"],
    }


def replay(programs, checks, inherited, entries):
    """Replay full forward/backward words; return deterministic evidence only."""
    require(set(programs) == {"forward", "backward"}, "source program orientations")
    local_inherited = inherited.get("local", inherited)
    return {orientation: replay_orientation(orientation, programs[orientation], checks[orientation],
                                           local_inherited[orientation], entries)
            for orientation in ("forward", "backward")}
