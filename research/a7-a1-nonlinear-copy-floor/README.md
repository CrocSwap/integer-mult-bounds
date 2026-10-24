# Nonlinear messages keep the A7+A1 nine-term COPY floor at 72

**Scoped negative result; no new κ.** The selected record and frontier are unchanged.

[a7-a1-decoder-floor](../a7-a1-decoder-floor/README.md) proves that the A7+A1 nine-normal decoder of
[PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224) has separate-term COPY cost at least 72
for every complex row shift. Its scope list says that arbitrary nonlinear decoder architectures are
outside that theorem. This package closes the nearest such case. It keeps the nine fixed term supports
and lets every term send an **arbitrary deterministic zero-error message**, for example one built with
AND gates. Each message is priced by its width in bits, the explicit pricing premise of
[gaussian-nonlinear-copy-floor](../gaussian-nonlinear-copy-floor/README.md) (#888) and #785/#814.

| Setting | Lower bound on the nine-term bill | Scope |
|---|---:|---|
| no reader side information | **72** (in general `sum rho_k`) | every complex shift (written lemma) |
| readers know all orthogonal inputs | **72** | both pinned sharp witnesses (finite certificates) |

Both bounds equal the linear invoice. So nonlinear coding cannot undercut it, and on the two sharp
witnesses free orthogonal side information cannot either. For d-bit blocks every bound scales to `72d`.

## Model

The model is inherited from a7-a1-decoder-floor without change. There are 120 E8 root lines with
`B_ij = 1` exactly when lines i and j are orthogonal or equal. The reader supports are
`Y_k = {j : T_jk != 0}` and the row supports are `X_k = {i : D_ik != 0}`. Term k is billed
`rho_k = rank_F2 B[X_k, Y_k]`. A nonlinear term k is a map `m_k = f_k(x restricted to X_k)` with finite
range. Every reader `j` in `Y_k` must recover its term value `sum_{i in X_k} B_ij x_i` from `m_k` and
from its own side information. The cost is `log2 |range f_k|`.

## Proofs

**Lemma 1 (no side information, every shift).** Choose `rho_k` rows S of X_k and `rho_k` readers R of Y_k
with `B[S,R]` invertible over F2. Set all inputs outside S to zero. The `2^rho_k` assignments on S then
give pairwise different value vectors on R. Each of these vectors is a function of `m_k`, so `m_k` takes
at least `2^rho_k` values. Summing over the terms gives `sum_k rho_k >= 72` for every shift, by the
predecessor's theorem. ∎

**Lemma 2 (orthogonal side information).** Suppose reader j knows `x_i` for every line i orthogonal to j.
Then a reader outside `X_k` already knows its term value. A reader j inside `X_k ∩ Y_k` needs exactly `x_j`.
Fix the inputs outside `X_k` to zero. Term k is then an index-coding instance on the induced orthogonality
graph `G[X_k ∩ Y_k]`. An induced subgraph only lowers the zero-error rate, and two lower bounds apply:

- *Petersen plus m isolated lines* gives `5d + md`. Petersen's broadcast rate is 5
  ([Blasiak, Kleinberg and Lubetzky, Fact 5.6(1)](https://www.cs.cornell.edu/~ablasiak/papers/bkl-beta.pdf);
  [p112-characteristic-two-minrank](../p112-characteristic-two-minrank/README.md) certifies the m=4 case,
  which gives 9d). Each isolated receiver v adds d: `H(M) = I(M; x_v) + H(M | x_v) >= d + H(M | x_v)`,
  and for each value of `x_v` the message is still a valid code for the rest. Induction on m finishes it.
- *A set of r pairwise non-orthogonal lines* gives `rd`: its receivers have no side information about
  one another.

The checker finds a certificate equal to `rho_k` in every term of both pinned witnesses:

| Witness (predecessor RESULT.json) | Invoice | Certificates |
|---|---|---|
| eight-active, `t_i = -x_i0` | `0,9,9,9,9,9,9,9,9` | 8 × (Petersen + 4) |
| nine-active (one row changed) | `1,8,9,9,9,9,9,9,9` | 1 non-orthogonal line, Petersen + 3, 7 × (Petersen + 4) |

The demand graphs have 50–57 lines. Both totals are 72. ∎

## What this does and does not cover

It covers nonlinear and AND-containing message codes on the predecessor's fixed nine-term supports,
for the separate-term bill and for the strongest natural side information at the two sharp witnesses.

It does **not** cover:

- other decoder architectures, changed normals, punctures, masked exactness or shared COPY billing;
- receivers that combine several terms nonlinearly instead of using separate-term values;
- the side-information bound for *every* complex shift (see the open question below).

With side information even a linear code can fall below `rho_k` on a small demand graph. A shift that
undercuts 72 under side information would therefore change the copy contract; it would not be a
nonlinear effect. No supplier, physical circuit or κ is claimed. The selected κ is unchanged.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -I -B research/a7-a1-nonlinear-copy-floor/verify.py
python3.12 -I -B research/a7-a1-nonlinear-copy-floor/test_verify.py
python3.12 -B scripts/research_package.py --package research/a7-a1-nonlinear-copy-floor
```

Expected markers:

```text
PASS_A7_A1_NONLINEAR_COPY_FLOOR roots=120 witnesses=2 no_side_info=72 orthogonal_side_info=72 petersen_terms=16 certificate=09a3e17032f727cb no_new_kappa
PASS_A7_A1_NONLINEAR_COPY_FLOOR_CONTROLS rejected=9
```

`verify.py` checks the SHA256 of the pinned predecessor `RESULT.json` before reading it. It rebuilds the
120-line model and both shift witnesses and checks the all-pairs identity and the invoices against the
predecessor. It then rebuilds every fooling block and side-information witness, compares the result with
the stored [RESULT.json](RESULT.json), and re-checks the stored certificate exactly as given.
`--write` regenerates the file explicitly. The default run is read-only. `test_verify.py` runs nine
rejecting controls: a singular or misplaced fooling block, a broken Petersen edge, a non-isolated or
duplicated witness line, a clique too small for its rank, a changed shift, a tampered certificate and a
drifted predecessor input.

## Open next questions

- Does the orthogonal-side-information floor stay at 72 for **every** complex row shift? A first step is
  to list each line's few support-reducing shifts (`t_i` in `{0, -x_ik}`) and find, per term, the largest
  demand graph that lacks a Petersen + (rank − 5) witness.
- The same two lemmas apply verbatim to the A8 simplex nine-term floor
  ([a8-simplex-decoder-floor](../a8-simplex-decoder-floor/README.md), #1248). Lemma 1 transfers at once;
  Lemma 2 needs its own witness search.

Prepared by Mark (Matarener) with substantial Claude Code (Claude) assistance.
