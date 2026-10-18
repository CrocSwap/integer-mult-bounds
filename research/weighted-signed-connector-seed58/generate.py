"""Deterministic nomination; independent verifier imports none of this code."""
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf"
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))


def source_words(repeated=None):
    labels = [0, 0, 1, 1, 2, 2]
    if repeated is not None:
        labels += [repeated, repeated]
    for order in sorted(set(itertools.permutations(labels))):
        sign_options = []
        for j in range(3):
            n = order.count(j)
            sign_options.append(sorted(set(itertools.permutations([-1] * (n // 2) + [1] * (n // 2)))))
        for signs in itertools.product(*sign_options):
            indices = [0, 0, 0]
            word = []
            for j in order:
                word.append((j, signs[j][indices[j]]))
                indices[j] += 1
            yield word


def nominate(repeated):
    feasible = 0
    nominated = None
    count = 0
    for moves in source_words(repeated):
        count += 1
        q = [0, 0, 0]
        vertices = [tuple(q)]
        for j, sign in moves:
            q[j] += sign
            vertices.append(tuple(q))
        readouts = {}
        for a, u in enumerate(vertices):
            for b, v in enumerate(vertices):
                readouts.setdefault(tuple(v[j] - u[j] for j in range(3)), (a, b))
        if not all(row in readouts for row in M):
            continue
        feasible += 1
        if nominated is not None:
            continue
        at = [[] for _ in vertices]
        for i, row in enumerate(M):
            a, b = readouts[row]
            at[a].append(["A", i, -1])
            at[b].append(["A", i, 1])
        word = []
        for t in range(len(vertices)):
            word.extend(at[t])
            if t < len(moves):
                word.append(["B", *moves[t]])
        nominated = word
    return nominated, {"paths": count, "feasible": feasible}


def main():
    witnesses = {}
    census = {}
    for j in range(3):
        word, receipt = nominate(j)
        witnesses[f"B{j}"] = word
        # M is symmetric. Chronological reversal followed by exchange of the
        # two query kinds transposes the product coefficient matrix.
        witnesses[f"A{j}"] = [["A" if k == "B" else "B", i, s] for k, i, s in reversed(word)]
        census[f"B{j}"] = receipt
        census[f"A{j}"] = receipt
    lengths = [4, 5, 6, 7, 2, 3]
    factors = {name: [f"{name}f{k}" for k in range(n)]
               for name, n in zip(["B0", "B1", "B2", "A0", "A1", "A2"], lengths)}

    def inverse(word):
        return [[f, s, t, -e] for f, s, t, e in reversed(word)]

    def child(fs, source, target, depth=0):
        if len(fs) == 1:
            return [[fs[0], source, target, 1]]
        middle = len(fs) // 2
        connector = 7 + depth
        right = child(fs[:middle], source, connector, depth + 1)
        left = child(fs[middle:], connector, target, depth + 1)
        return right + left + inverse(right) + inverse(left)

    leaves = {}
    for name, word in witnesses.items():
        leaves[name] = []
        for kind, index, sign in word:
            source, target = (index, 6) if kind == "B" else (6, 3 + index)
            lowered = child(factors[f"{kind}{index}"], source, target)
            leaves[name].extend(lowered if sign == 1 else inverse(lowered))
    data = {"format": "weighted-signed-connector-v1", "base": BASE, "seed": 58,
            "matrix": M, "witnesses": witnesses, "census": census,
            "lengths_B_then_A": lengths, "factors": factors, "leaves": leaves,
            "chosen": "A1",
            "scope": "positive sign-symmetric complete-query prices; fixed one-connector alphabet; no new kappa"}
    (ROOT / "CERTIFICATE.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("GENERATED_WEIGHTED_SIGNED_CONNECTOR witnesses=6")


if __name__ == "__main__":
    main()
