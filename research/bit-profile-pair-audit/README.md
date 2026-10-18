# The bit paid profile is the whole bit supplier, and the reframing class is exhausted at #589

This note prices a bit word from its **paid profile alone**, and then uses that to run an exhaustive
audit of the merged bit supplier. It adds no κ: at the current frontier the bit side does not bind.
It is a scoped exact result about one move class on one word, plus a reusable exact pricer.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`, rebased onto `29218749`; every pinned input
is byte-identical on both.
Objects: PR #555's punctured R439 word (`research/e8-bit-p111/`) and PR #589's tuned word
(`research/e8-bit-p111-tuned/tune/`), both unchanged on main.

## 1. What is new

### 1.1 The paid-profile duality

Let the nine-stage bit pipeline's paid profile be `n = (n_r)`: for each elementary paid climb of
dimension jump `r`, one unit. Let `m` be the pipeline modulus, `W` the live port-register count, and

    M := sum_r r * n_r          (rank mass)
    D := m*W - M                (deficit)

**Fact.** The certified saving `c` of the word is the unique `a > 0` with

    Psi(a) := sum_r n_r * r * ((m/r)^a - 1)  =  D.

*Proof.* The pipeline's `moment`/`certify` pair (`.../engines/moment.py`) finds the root of
`S(a) = sum_r (r n_r)/(m W) * (m/r)^a = 1`. Multiplying by `mW` and subtracting `M` gives `Psi(a) = D`;
`Psi` is strictly increasing on `a > 0` because `(m/r)^a` is, and `r <= m` for every paid rank.
∎

Since `Psi(a) = m^a G(a) - M` with `G(a) = sum_r n_r r^(1-a)`, and both `m^a` and `G` are increasing
in `a`, the following is immediate and is what makes search tractable:

**Corollary.** For **any** fixed `a0 > 0`, the certified saving is a strictly decreasing function of
the single weighted count `G(a0) = sum_r n_r r^(1-a0)`. Rank-profile search is therefore a
one-dimensional linear-objective problem, and a candidate word can be priced in `O(#gates)` with
integer arithmetic only — no root finding and no floating point.

**Verified exactly.** `code/bitprof.py` re-derives `c` from the profile with its own rational
`ln`/`exp` interval bounds (no repository engine, no floating point). For both words the lower
endpoint of the resulting `10^-24` bracket is *exactly* the shipped 24-digit value:

| word | shipped `c` | bracket from the profile equation |
|---|---|---|
| #555 base, R439 | `1733052823330162099157/10^24` | lower endpoint equal |
| #589 tuned, R439 | `1733427039589844234749/10^24` | lower endpoint equal |

Only the **nine-stage** price is used here. The eleven-stage pipeline runs the same pricer on its own
profile (`research/e8-bit-p111-tuned/tune/EXPECTED.json` records both); nothing in this note depends on
the eleven-stage numbers.

The shipped values include the pipeline's inherited bad-envelope surcharge (32·m² rank-one fallback
calls per paid child at `10^-16`), which is `Psi(a) + 32 m^2 (sum_r n_r) m^a / 10^16 = D` here. The
unsurcharged root is strictly larger by `2.01e-12`, i.e. the surcharge is *not* negligible at 24
digits; the verifier checks both roots. Reporting the surcharge explicitly is the only correction to
a naive reading of "the certified saving is the root of the moment equation".

### 1.2 The objective decomposes over registers

`G` is a sum of per-register contributions: a register's cost depends only on the operations that
touch it. Hence

* the objective delta of one transported operation is the sum of the deltas of the two registers it
  touches, and
* **a `k`-operation improvement requires the `k` operations to share registers.**

The second point is what makes a *complete* two-move search affordable: at the fixed point the 9,347
nominated moves reduce to 6.5·10^5 register-adjacent pairs instead of ~4.4·10^7.

### 1.3 The audit

Move class (the merged tuner's, `research/e8-bit-p111-tuned/tune/tune.py`): single-operation transport
with reframing under exact commutation and frame nesting, plus Steinberg 3→2. All prices below are on
the **exact** objective `G(a0)`, `a0 = 0.001733`.

| check | result |
|---|---|
| nominated single moves, #589 tuned word | 9,347 |
| strictly improving single moves | **0** |
| exactly cost-neutral single moves (a flat plateau) | 9,263 |
| improving Steinberg 3→2 moves (671 triples) | **0** |
| legal `(slot, frame)` pairs examined (3,064 operations) | 9,933 |
| operations where the nominated frame is *not* exact-objective optimal | **0** |
| complete register-adjacent two-move neighbourhood (`--full`) | 645,900 pairs |
| best two-move delta | **0**, exactly |

So the merged word is a fixed point of the *complete* nominated one-move neighbourhood, and the
nomination itself loses nothing at the frame level: the tuner's per-slot frame choice (made with its
own proxy cost) coincides with the exact-objective argmin frame for every operation. Two moves do not
escape the plateau either.

**Positive control.** Steepest descent on the exact objective, with a full re-nomination at every
step, started from #555's base word, applies **exactly two** moves — `A[2034] -> slot 2028, frame 79`
(PR #589's hoist) and `A[2041] -> slot 2076, frame 517` (PR #589's sink) — and lands on the tuned
word's profile and objective (`5122.831869920` from `5122.839536792`). The machinery rederives #589
independently rather than being told about it.

**What this is worth.** It closes the reframing avenue for the merged bit supplier at one and two
moves. Any further bit saving from this word must come from a mechanism outside the class — geometry,
decoder constant, helper count, or hosting — not from moving gates. It also gives the exact marginal
exchange rate for any future move: `dc/c = -(dG/G) / (a (ln m - E[ln r]))`, so a candidate can be
priced before it is built.

## 2. What this does not claim

* Not an optimality theorem over bit words. It says nothing about words outside the R439/punctured
  family, nor about three-or-more-move escapes of this plateau.
* The two-move search is complete **for the nominated move set**; the verifier separately certifies
  that the nominated set already contains the exact-objective best frame for every operation, which is
  the only place the nomination could have lost a candidate.
* No κ change. The bit side is not binding: at the merged #589 word `c = 0.0017334`, above the complex
  caps cited by the current frontier. This is headroom bookkeeping only.
* The tuner's own proxy objective is *not* identical to the exact objective (largest absolute
  discrepancy `1.645e-5` on this word, at `A[2076]`); only its argmin agrees here. The audit prices
  everything on the exact objective for that reason.
* Every interface that #543, #555 and #589 retain remains assumed: all-size compilation,
  mutable-basis and common-label realization, pooled-cell hosting, the compact/residual,
  precision/tape/exact-recovery and analytic contracts. This is a finite exact computation, not a
  formal proof of integer multiplication.

## 2b. Concurrent work, and what it says about this result

The repository moved while this audit was prepared. Its pinned inputs are unchanged on the current
`main` (`29218749`), and these concurrent contributions are consistent with — and sharpen — the
conclusion above:

* **PR #1043** improves the *same* #589 word by a mechanism outside the reframing class: it deletes
  `helper470` by reading `source77` at a caller boundary, giving R438 and
  `c = 0.001734176288479865766692` (from `0.001733427039589844234749`). That is a register/helper
  rewrite, not a gate transport, which is exactly where §1.3 says the remaining headroom has to come
  from.
* **PR #1040, #1047** reduce complete ADD counts on a different R439 lineage (post-PR915/PR967), and
  **#1045** crosses PR941's disjoint-pair floor with a four-helper fusion. Their words, their
  accounting (complete ADDs) and their move classes differ from the #589 word and the transport class
  audited here, so none of them is a counterexample to the fixed point above; the helper-shear and
  fusion mechanisms are further examples of the "outside the class" route.
* These results are cited from their own packages and were not re-run here.

## 3. Reproduce

```sh
make bit-profile-pair-audit-verify        # ~6 min: every check except the pair search
make bit-profile-pair-audit-full-verify   # ~35 min: adds the complete two-move neighbourhood
```

Python 3.11+ with `numpy` (used by the pinned tuner). No C++ toolchain, Boost, Lean or network access
is needed: every input is a pinned file on main and every check is exact integer or rational
arithmetic.

## 4. Files

* `code/bitprof.py` — the profile→saving equation, with own rigorous rational `ln`/`exp` bounds.
* `code/replay.py` — independent word replay and paid profile (rank over the rationals, not modulo a
  prime), sharing no code with `wlib.py`.
* `code/stateprof.py` — the exact objective on the flat elementary-op state and the register
  decomposition.
* `code/search.py` — the one-move scan, the exact steepest descent, and the complete register-adjacent
  two-move search.
* `verify.py`, `EXPECTED.json` — the checks and every number.

## 5. Credit and disclosure

The base word, its generator, its checkers, its pricing pipelines and the tuner are PR #555 (eumemic),
building on PR #543 (eumemic; R420 L3 skeleton), PR #545 (DreamingOfClouds; punctured star unit) and
PR #510. The two transports audited here are PR #589 (DreamingOfClouds). The deficit identity
`m W - rank_mass = T(2Kv - L cst)` is PR #545's. GamingPuzzled's #620 and vectorsss's #631 bound the
decoder side (`63/111`), which is orthogonal to the reframing class audited here.

Prepared with substantial AI assistance (DeepSeek Harness / deepseek-flash). All checks in `verify.py`
are deterministic and were run against the pinned files on main.
