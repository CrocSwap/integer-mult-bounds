"""Independent exact fixtures for the formal normal-class implication.

No predecessor engine is imported. Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from fractions import Fraction
import hashlib
import itertools
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank_q(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    if not a:
        return 0
    need(all(len(row) == len(a[0]) for row in a), "rectangular matrix")
    pivot = 0
    for col in range(len(a[0])):
        found = next((j for j in range(pivot, len(a)) if a[j][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        d = a[pivot][col]
        a[pivot] = [x/d for x in a[pivot]]
        for j in range(len(a)):
            if j != pivot and a[j][col]:
                c = a[j][col]
                a[j] = [x-c*y for x, y in zip(a[j], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def rank_f2(matrix):
    basis = {}
    for row in matrix:
        value = sum((int(x) & 1) << j for j, x in enumerate(row))
        while value:
            lead = value.bit_length()-1
            if lead not in basis:
                basis[lead] = value
                break
            value ^= basis[lead]
    return len(basis)


def ident(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def residual(k):
    n = len(k)
    return [[int(i == j)-k[i][j] for j in range(n)] for i in range(n)]


def matmul(a, b):
    need(bool(b) and all(len(r) == len(b) for r in a), "product shape")
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def hypotheses(k, alpha, beta):
    return (all(a != b for a, b in zip(alpha, beta)) and
            all(not k[i][j] or beta[i] == alpha[j]
                for i in range(len(k)) for j in range(len(k))))


def census():
    options = [(a, b) for a in range(3) for b in range(3) if a != b]
    result = []
    digest = hashlib.sha256()
    for t in range(5):
        assignments = cases = sharp_q = sharp_f2 = 0
        q_hist, f2_hist = {}, {}
        for ends in itertools.product(options, repeat=t):
            assignments += 1
            alpha, beta = [a for a, _ in ends], [b for _, b in ends]
            slots = [(i, j) for i in range(t) for j in range(t) if beta[i] == alpha[j]]
            up = [i for i in range(t) if alpha[i] < beta[i]]
            down = [i for i in range(t) if alpha[i] > beta[i]]
            need(len(up)+len(down) == t, "partition")
            for bits in range(1 << len(slots)):
                k = [[0]*t for _ in range(t)]
                for z, (i, j) in enumerate(slots):
                    k[i][j] = (bits >> z) & 1
                need(hypotheses(k, alpha, beta), "generated hypotheses")
                m = residual(k)
                rq, rf = rank_q(m), rank_f2(m)
                need(t <= 2*rq and t <= 2*rf, "half-rank conclusion")
                # This tests the two actual principal-minor implications as well.
                for part in (up, down):
                    sub = [[m[i][j] for j in part] for i in part]
                    need(rank_q(sub) == rank_f2(sub) == len(part), "orientation minor")
                q_hist[str(t-rq)] = q_hist.get(str(t-rq), 0)+1
                f2_hist[str(t-rf)] = f2_hist.get(str(t-rf), 0)+1
                sharp_q += int(2*(t-rq) == t)
                sharp_f2 += int(2*(t-rf) == t)
                cases += 1
                digest.update(json.dumps([t, alpha, beta, bits, rq, rf], separators=(",", ":")).encode()+b"\n")
        result.append(dict(t=t, class_assignments=assignments, matrices=cases,
                           kernel_dimensions_q=q_hist, kernel_dimensions_f2=f2_hist,
                           sharp_q=sharp_q, sharp_f2=sharp_f2))
    return result, digest.hexdigest()


def rectangular_fixtures():
    out = []
    # A nontrivial fixed direction, including both ambient dimension inequalities.
    for t in (2, 3, 4):
        k = [[0]*t for _ in range(t)]
        k[0][1] = k[1][0] = 1
        alpha, beta = [0, 1]+list(range(2, t)), [1, 0]+list(range(3, t+1))
        need(hypotheses(k, alpha, beta), "cycle hypotheses")
        for n in (2, t, t+3):
            a = [[int(i == j) for j in range(t)] for i in range(n)]
            c = [[k[i][j] if j < t else ((i+2*j) % 3)-1 for j in range(n)] for i in range(t)]
            # Arbitrarily mix all ambient coordinates by exact invertible shears.
            # Update A <- S A, C <- C S^-1, so C A remains fixed.
            for dst in range(1, n):
                src = dst-1
                a[dst] = [x+y for x, y in zip(a[dst], a[src])]
                for row in c:
                    row[src] -= row[dst]
            need(matmul(c, a) == k, "rectangular source product")
            ac = matmul(a, c)
            dq, df = n-rank_q(residual(ac)), n-rank_f2(residual(ac))
            need(dq == t-rank_q(residual(k)) == 1, "Q fixed-space transfer")
            need(df == t-rank_f2(residual(k)) == 1, "F2 fixed-space transfer")
            need(2*dq <= t, "rectangular half bound")
            out.append(dict(ambient=n, terms=t, kernel_q=dq, kernel_f2=df,
                            A=a, C=c))
    return out


def replay():
    rows, digest = census()
    fixtures = rectangular_fixtures()
    controls = []
    k = [[1]]
    need(not hypotheses(k, [0], [0]) and rank_q(residual(k)) == 0, "equal-class counterexample")
    controls.append("distinct class endpoints cannot be omitted")
    k = [[int(i == j)-1 for j in range(3)] for i in range(3)]
    need(all(k[i][i] == 0 for i in range(3)), "zero-diagonal control")
    need(not hypotheses(k, [0]*3, [1]*3), "compatibility control")
    need(rank_q(residual(k)) == rank_f2(residual(k)) == 1, "zero diagonal does not give half rank")
    controls.append("zero diagonal cannot replace class compatibility")
    k = [[0, 1], [1, 0]]
    need(hypotheses(k, [0, 1], [1, 0]), "sharp cycle positive")
    d = 2-rank_q(residual(k))
    need(2*d == 2 and 3*d > 2, "one-third replacement is false")
    controls.append("half cannot be strengthened to one third")
    # Actual complete factorization I = AC + DE attains the abstract count bound.
    a, c = ident(2), k
    dmat, e = [[1], [-1]], [[1, -1]]
    ac, de = matmul(a, c), matmul(dmat, e)
    need([[ac[i][j]+de[i][j] for j in range(2)] for i in range(2)] == ident(2), "completed factorization")
    need(2*2 == 2*1+2 and 8*2+3*2 == 7*2+8*1, "attained abstract bill")
    return dict(status="PASS_NORMAL_CLASS_RANK_FINITE_ONLY", census=rows,
                census_sha256=digest, rectangular=fixtures, controls=controls,
                sharp_completed_factorization=dict(A=a, C=c, D=dmat, E=e),
                kernel_checked=False, physical_P112_premises_checked=False,
                new_kappa_claim=False)


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
