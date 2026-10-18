#!/usr/bin/env python3
"""Both implementations must reject proof-relevant certificate corruption.

Hanson Sun, substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    original = json.loads((HERE / "CERTIFICATE.json").read_text())
    changes = []

    def mutation(name, edit):
        candidate = copy.deepcopy(original)
        edit(candidate)
        changes.append((name, candidate))

    mutation("missing_shortest_word", lambda c: c["census"]["words_by_length_0_through_7"].__setitem__(7, 215))
    mutation("lost_positive_class", lambda c: c["census"]["shortest_positive_histogram"].pop())
    mutation("changed_word_digest", lambda c: c["census"].__setitem__("shortest_word_sha256", "0" * 64))
    mutation("false_peak", lambda c: c["eight_gate_witness"].__setitem__("forward", 3))
    mutation("missing_restoration", lambda c: c["eight_gate_witness"]["gates"].pop(4))
    mutation("false_positive_matrix", lambda c: c["eight_gate_witness"]["positive_reverse"][0].__setitem__(1, 0))
    mutation("false_support_floor", lambda c: c.__setitem__("positive_support_lower_bound", 3))
    mutation("false_frontier", lambda c: c.__setitem__("pareto_gate_count_bidirectional_peak", [[7, 4]]))
    mutation("free_self_xor", lambda c: c["eight_gate_witness"]["gates"].__setitem__(0, [0, 0]))
    rejected = 0
    with tempfile.TemporaryDirectory(prefix="j3-certificate-controls-") as work:
        for name, candidate in changes:
            path = Path(work) / (name + ".json")
            path.write_text(json.dumps(candidate))
            for script in ("verify.py", "independent.py"):
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / script),
                                         "--certificate", str(path)],
                                        cwd=work, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 or "ValueError:" not in result.stderr:
                    raise ValueError(f"{script} failed to reject {name}: {result.stderr}")
                rejected += 1
    print(f"PASS_J3_PACKAGE_CONTROLS mutations={len(changes)} independent_rejections={rejected}")


if __name__ == "__main__":
    main()
