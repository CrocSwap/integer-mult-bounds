"""KB3j class (3,3): complete small-space census of the (12,6) A-vanish (3,3)
shape (set level; no words).

Class (3,3) has no singleton absorption: the four PR 2933 L3 lines apply
directly to (A0, A1 u-sets, D0, D1 x-sets) of F2^k with 0 in A0, 0 in A1
(the residual half-translations (a,b): A0->A0+a, D0->D0+a, A1->A1+b,
D1->D1+b act on the four lines by invariance or co-translation):

  (I)   (A0+D0) u (A1+D1) = F2^k
  (II)  (A0+D1) u (A1+D0) = F2^k
  (III) (A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = F2^k
  (IV)  (A0+A1) u (D0+D1) = F2^k

census33_k3() is a COMPLETE normalized census over F2^3 halves (8-point
space) for every (u, u, x, x) class: covers, per-line failure tallies and
the kill shape ('pair' = no configuration even passes lines (I)-(III) with
(IV) slack... see the class rows).  Exact int arithmetic only.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build_tables(n):
    """Precomputed trans/sumset/selfsum for all subsets of an n-point group."""
    allm = (1 << n) - 1
    trans = [[0] * n for _ in range(1 << n)]
    for m in range(1 << n):
        for a in range(n):
            out = 0
            x = m
            while x:
                lsb = x & -x
                out |= 1 << ((lsb.bit_length() - 1) ^ a)
                x ^= lsb
            trans[m][a] = out
    summ = [[0] * (1 << n) for _ in range(1 << n)]
    for x in range(1 << n):
        row = summ[x]
        for y in range(1 << n):
            out = 0
            t = y
            while t:
                lsb = t & -t
                out |= trans[x][lsb.bit_length() - 1]
                t ^= lsb
            row[y] = out
    return allm, trans, summ


def census33_k3():
    """Complete normalized census of the (3,3) shape over F2^3 halves."""
    n = 8
    allm, trans, summ = build_tables(n)
    norm = [m for m in range(1 << n) if m & 1]
    subs = list(range(1 << n))
    classes = {}
    for u_size in range(1, n + 1):
        u_list = [m for m in norm if m.bit_count() == u_size]
        for x_size in range(1, n + 1):
            x_list = [m for m in subs if m.bit_count() == x_size]
            key = (u_size, x_size)
            r = classes.setdefault(
                key,
                dict(
                    configs=0,
                    covers=0,
                    fail_I=0,
                    fail_II=0,
                    fail_III=0,
                    fail_IV=0,
                    pass_I_II_III=0,
                    pass_all_but_IV=0,
                ),
            )
            for a0 in u_list:
                sa0 = summ[a0][a0]
                for a1 in u_list:
                    sa1 = summ[a1][a1]
                    iv_left = summ[a0][a1]
                    for d0 in x_list:
                        sd0 = summ[d0][d0]
                        i_left = summ[a0][d0]
                        iv_r = summ[d0]
                        for d1 in x_list:
                            r["configs"] += 1
                            sd1 = summ[d1][d1]
                            ok_i = (i_left | summ[a1][d1]) == allm
                            ok_ii = (summ[a0][d1] | summ[a1][d0]) == allm
                            ok_iii = (sa0 | sa1 | sd0 | sd1) == allm
                            ok_iv = (iv_left | summ[d0][d1]) == allm
                            if not ok_i:
                                r["fail_I"] += 1
                            if not ok_ii:
                                r["fail_II"] += 1
                            if not ok_iii:
                                r["fail_III"] += 1
                            if not ok_iv:
                                r["fail_IV"] += 1
                            if ok_i and ok_ii and ok_iii:
                                r["pass_I_II_III"] += 1
                                if not ok_iv:
                                    r["pass_all_but_IV"] += 1
                            if ok_i and ok_ii and ok_iii and ok_iv:
                                r["covers"] += 1
    out = {}
    for key, r in sorted(classes.items()):
        if r["covers"] > 0:
            r["kill_shape"] = "cover"
        elif r["pass_I_II_III"] == 0:
            r["kill_shape"] = "I/II/III"
        elif r["pass_all_but_IV"] == r["pass_I_II_III"]:
            r["kill_shape"] = "IV-only"
        else:
            r["kill_shape"] = "mixed"
        out[str(key)] = r
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res = census33_k3()
    (HERE / "CENSUS-33-K3.json").write_text(
        json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for key in sorted(res, key=lambda k: eval(k)):
        r = res[key]
        print(
            "%s configs=%d covers=%d pass3=%d shape=%s"
            % (key, r["configs"], r["covers"], r["pass_I_II_III"], r["kill_shape"]),
            flush=True,
        )
    print("PASS_CENSUS33_K3 classes=%d" % len(res), flush=True)


if __name__ == "__main__":
    main()
