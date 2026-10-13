"""Independent sparse-Fraction replay of every primitive denominator depth.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
The common-denominator integer-row engine is not used here. Input binding and
the pinned circuits are shared proof objects, not independent authorship.
"""

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bound_inputs", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def run(events, word, orientation, lower, reverse):
    n = 2*word["v"]+word["R"]
    state = {("L", i): {i: Q(1)} for i in range(n)}
    state.update({("C", i): {n+i: Q(1)} for i in range(len(word["centers"]))})
    state["W", 0] = {n+len(word["centers"]): Q(1)}
    stream = hashlib.sha256()
    peak, count = 0, 0
    for event in events:
        if event[0] != "scalar":
            continue
        for op in lower.choose(event[1], reverse=reverse)[1]:
            tag, target = op[:2]
            if tag == "clear":
                state[target] = {}
            elif tag == "copy":
                state[target] = dict(state[op[2]])
            elif tag in ("double", "halve", "negate"):
                factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
                state[target] = {k: factor*a for k, a in state[target].items()}
            elif tag in ("add", "subtract"):
                dest = dict(state[target])
                sign = 1 if tag == "add" else -1
                for k, a in state[op[2]].items():
                    value = dest.get(k, Q(0)) + sign*a
                    if value:
                        dest[k] = value
                    else:
                        dest.pop(k, None)
                state[target] = dest
            else:
                raise ValueError("unknown primitive")
            depth = max((a.denominator.bit_length()-1 for a in state[target].values()), default=0)
            v.need(all(a.denominator & (a.denominator-1) == 0 for a in state[target].values()), "non-dyadic row")
            peak = max(peak, depth)
            stream.update(v.canonical([depth, tag, list(target)]).encode()+b"\n")
            count += 1
    for i in range(n):
        expected = {i: Q(1)}
        if orientation == "forward" and word["v"] <= i < 2*word["v"]:
            expected[i-word["v"]] = Q(1)
        elif orientation == "backward" and i < word["v"]:
            expected[i+word["v"]] = Q(-1)
        v.need(state["L", i] == expected, "rational full endpoint mismatch")
    v.need(all(not row for reg, row in state.items() if reg[0] != "L"), "rational private stream remains")
    return peak, stream.hexdigest(), 2*count


def main():
    v.source_pins()
    expected = v.read(HERE / "EXPECTED.json")
    lower = v.load(HERE / "vendor/pr837/lower.py", "pinned_circuits")
    checked, primitives = 0, 0
    for provider, specification, parts in v.inputs():
        for name, raw in parts.items():
            v.need(hashlib.sha256(raw).hexdigest() == specification["artifact_semantic_sha256"][name], "rational input binding")
        word = json.loads(parts["CANONICAL-WORD.json.gz"])
        for orientation, events in sorted(json.loads(parts["LOCAL-PROGRAMS.json.gz"]).items()):
            v.need(v.digest(events) == specification["program_hashes"][orientation], "rational program binding")
            record = expected["programs"][provider+"/"+orientation]
            for reverse, label in ((False, "forward_best"), (True, "bidirectional")):
                depth, digest, cost = run(events, word, orientation, lower, reverse)
                row = record[label]
                v.need((depth, digest, cost) == (row["scalar_projection_guard_bits"], row["depth_stream_sha256"], row["real_primitives"]),
                       "integer/Fraction depth trace mismatch")
                checked += 1
                primitives += cost//2
    print("PASS_FRACTION_GRID_CROSSCHECK complete_traces="+str(checked)+" scalar_primitives="+str(primitives))


if __name__ == "__main__":
    main()
