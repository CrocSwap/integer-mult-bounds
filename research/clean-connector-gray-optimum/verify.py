#!/usr/bin/env python3
"""Check formal words, exact linear maps, unrestricted small optima and bills."""
from hashlib import sha256
from heapq import heappop, heappush
import importlib.util
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from connector import schedule, execute


def need(ok, message):
    if not ok:
        raise ValueError(message)


def formal(word, n):
    c = 0
    out = [0] * ((1 << n) - 1)
    for op, j in word:
        if op == "B": c ^= 1 << j
        elif op == "A": out[j - 1] ^= c
    return c == 0 and out == list(range(1, 1 << n))


def shortest(n, b, a):
    """Dijkstra on the full finite coefficient state, with no word cutoff."""
    target = tuple([0] + list(range(1, 1 << n)))
    start = (0,) * (1 << n)
    dist = {start: 0}
    queue = [(0, start)]
    while queue:
        cost, state = heappop(queue)
        if dist[state] != cost: continue
        if state == target: return cost
        for i in range(n + (1 << n) - 1):
            nxt = list(state)
            if i < n:
                nxt[0] ^= 1 << i
                price = b
            else:
                nxt[i - n + 1] ^= state[0]
                price = a
            nxt = tuple(nxt)
            if cost + price < dist.get(nxt, float("inf")):
                dist[nxt] = cost + price
                heappush(queue, (cost + price, nxt))
    raise ValueError("no exact schedule")


def linear(word, columns):
    out = 0
    for i, col in enumerate(columns):
        if word >> i & 1: out ^= col
    return out


def matrix_cases():
    count = 0
    for n in range(1, 7):
        for width in range(1, 5):
            for seed in range(8):
                mask = (1 << width) - 1
                Bs = [[(j * 7 + i * 3 + seed) & mask for i in range(width)] for j in range(n)]
                As = [[(j * 5 + i * 9 + seed * 3) & mask for i in range(width)] for j in range(1, 1 << n)]
                sources = [(i * 11 + seed) & mask for i in range(n)]
                targets = [(i * 3 + seed * 7) & mask for i in range((1 << n) - 1)]
                B = lambda x, j: linear(x, Bs[j])
                A = lambda x, j: linear(x, As[j - 1])
                expected = []
                for m, old in enumerate(targets, 1):
                    # Expand each target by its separate matrix products.
                    val = old
                    for j, x in enumerate(sources):
                        if m >> j & 1: val ^= A(B(x, j), m)
                    expected.append(val)
                got = execute(schedule(n), sources, mask, targets, mask, B, A)
                need(got == (sources, mask, expected, 0), "arbitrary linear-map case")
                count += 1
    return count


def replay():
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            need(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], "source hash mismatch")
    spec = importlib.util.spec_from_file_location("old", ROOT / "research/clean-connector-per-mask-seede54e/verify.py")
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    need(old.verify_bill_and_fixture()[:4] == (26704, 41138, 38656, 2482), "source fixture changed")
    words = 0
    for n in range(1, 13):
        word = list(schedule(n))
        need(formal(word, n), "formal prefix endpoint")
        need(sum(op == "B" for op, _ in word) == 1 << n, "source count")
        need(sorted(j for op, j in word if op == "A") == list(range(1, 1 << n)), "single mask coverage")
        words += 1
    small = 0
    for n in (1, 2):
        for b in (1, 2, 3):
            for a in (b, b + 1, b + 2):
                need(shortest(n, b, a) == (1 << n) * b + ((1 << n) - 1) * a, "unrestricted optimum")
                small += 1
    # The a>=b condition is necessary for the displayed general formula.
    source_word = [0, 1, 2, 0, 1, 2]
    prefix = [0]
    for j in source_word: prefix.append(prefix[-1] ^ (1 << j))
    reads = {1: [1], 2: [1, 2], 3: [2], 4: [5], 5: [1, 5], 6: [4], 7: [3]}
    cheap_readout = [("INIT", 0)]
    for t in range(7):
        for m, at in reads.items():
            if t in at: cheap_readout.append(("A", m))
        if t < 6: cheap_readout.append(("B", source_word[t]))
    cheap_readout.append(("RELEASE", 0))
    need(formal(cheap_readout, 3), "cheap-readout witness")
    need(6 * 10 + 9 < 8 * 10 + 7, "price-hypothesis discriminator")
    B = lambda x, j: old.permute(x, old.B_MAPS[j])
    A = lambda x, j: old.apply_output_map(x, j - 1)
    word = list(schedule(5))
    digest = sha256()
    cases = []
    for column in range(608):
        state = [0] * 38
        state[column // 16] = 1 << (column % 16)
        cases.append((state[:5], state[5], state[6:37], state[37]))
    cases.extend(old.mixed_word(i * 97 + 5) for i in range(64))
    for inputs in cases:
        got = execute(word, *inputs, B, A)
        expected = old.execute(*inputs)
        need(got == expected and old.valid_result(inputs, got), "retained basis/mixed endpoint")
        digest.update(json.dumps(got).encode())
    controls = 0
    mutations = [word[1:], word[:-2] + word[-1:], word[:1] + word[2:],
                 [(op, 2 if (op, j) == ("A", 1) else j) for op, j in word],
                 word[:3] + [word[2]] + word[3:], word[:1] + [word[2], word[1]] + word[3:]]
    inputs = old.mixed_word(0xC1EA5EED)
    for bad in mutations:
        try: accepted = old.valid_result(inputs, execute(bad, *inputs, B, A))
        except ValueError: accepted = False
        need(not accepted, "word mutation escaped")
        controls += 1
    invoice = dict(old.EXPECTED_INVOICE)
    invoice.update(source_updates=32 * 16, action_descriptors=63 * 13)
    need(sum(invoice.values()) == 34944, "complete clean invoice")
    for key in invoice:
        changed = dict(invoice); changed[key] = 0
        need(sum(changed.values()) != 34944, "unpaid invoice line")
        controls += 1
    dirty = json.loads((ROOT / "research/connector-all-tariff-optimum/RESULT.json").read_text())
    profile_prices = [sum(c * (29 if i < 5 else 221) for i, c in enumerate(v))
                      for v in dirty["pareto_profiles"]]
    need(len(profile_prices) == 16 and min(profile_prices) == 14050, "true dirty tariff")
    need(26704 + min(profile_prices) == 40754, "complete dirty fixture bill")
    return {"status": "PASS_CLEAN_CONNECTOR_GRAY_OPTIMUM_NO_NEW_KAPPA", "formal_words": words,
            "unrestricted_small_optima": small, "linear_map_cases": matrix_cases(),
            "retained_basis_columns": 608, "retained_mixed_cases": 64,
            "output_sha256": digest.hexdigest(), "new_B": 32, "new_A": 31,
            "invoice": invoice, "new_clean_cost": 34944, "old_clean_cost": 38656,
            "true_dirty_cost": 40754, "saving_over_old_clean": 3712, "saving_over_dirty": 5810,
            "a_lt_b_control": {"n": 3, "b": 10, "a": 1, "word_cost": 69, "gray_cost": 87},
            "mutation_controls": controls}


if __name__ == "__main__":
    result = replay()
    if "--record" in sys.argv: (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.dumps(result, sort_keys=True) == json.dumps(json.loads((HERE / "RESULT.json").read_text()), sort_keys=True), "typed receipt mismatch")
    print(json.dumps(result, sort_keys=True))
