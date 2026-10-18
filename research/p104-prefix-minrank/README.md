# Exact early-prefix dimensions for the P104 pooled correction

The rational shared correction dimension for the unchanged P104 trace is:

| Completed original events `c` | Exact minimum `h(c)` |
|---|---:|
| 0–2525 | 104 |
| 2526–2555 | 103 |
| 2556–2571 | 102 |
| 2572–2617 | 101 |
| 2618–2645 | 100 |
| 2646–2717 | 99 |

This answers an early-prefix part of the open question in
[the prefix-boundary handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18940216).
It also gives an exact eight-dimensional minimum-rank formulation for any
prefix satisfying the checked lifting hypotheses. The earlier
[PR #2251](https://github.com/CrocSwap/integer-mult-bounds/pull/2251) establishes
the full-pool minimum 96; the handoff reports 97 on 2824–2911 and 96 from 2912.
Those late-prefix results are credited, not independently recertified here.

**No chronological correction circuit or paid transport saving follows.**
The model pools snapshots from different times and permits arbitrary new
rational shared directions for free. It does not construct, transport, host
or restore those directions. No new supplier, exponent or selected result is
proposed. Cuts 2718–2823 are deliberately left unresolved in this package.

## Model and immutable inputs

Use Rohan Arun's 4,058-event PR #1972 channel, as frozen by Chafik Boukhalfa's
native PR #1991. A cut counts completed events, so cut zero is the initial
state. There are 104 source inputs `X`, 104 target inputs `Y` and 72 arbitrary
dirty helper inputs. For each target `t`, set

```
S_t(c) = span_Q { v_r(d) : 0 <= d <= c, r != Y_t,
                 frame(r,d) = frame(Y_t,d) as binary subspaces }.
```

Here `v_r(d)` is the logical row in the **unchanged original trace**. No added
row is fed back into that trace. Basis changes inside a binary frame are free
in this pooled model. Let `R` be the 8-by-104 doubled root-coordinate matrix,
`C = I_104 - R^T R/8`, and define `h(c)` as the least dimension of a rational
space `H` in all 280 boundary coordinates with `C_t in S_t(c)+H` for every `t`.
All coefficient fields in the result are **Q**. We make no assertion equating
constrained rational minimum rank with real or complex minimum rank.

[SOURCES.json](SOURCES.json) pins the two actual JSON inputs by Git blob and
SHA-256 at main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The input witness
hash is `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
No pending predecessor program is imported; frozen packages are unchanged.

## Exact reduction, including arbitrary dirty components

The checker reconstructs the roots and verifies `R R^T = 104 I_8`. Hence
`C` is invertible, with inverse `I_104-R^T R/96`, and `R C = -12 R`.
It checks the following facts against **every** original cut:

1. Every eligible snapshot's source projection lies in `row(R)`.
2. At cut zero all 175 non-source coordinate units other than `Y_t` are
   available to target `t` in the zero frame.
3. No eligible snapshot contains its own target input `Y_t`.

Write `pi_X` for projection to the source coordinates. Facts 2–3 let us subtract
the entire nuisance part of any eligible row using available initial units.
Therefore `pi_X(S_t(c)) = S_t(c) intersect X`. This lifting equality is needed:
projection containment alone does not justify replacing a shared space with
dirty components by a source-only space. The control suite gives two small
counterexamples when either lifting premise is dropped.

Define `L_t(c) = { a in Q^8 : a R in S_t(c) intersect X }`. Any serving `H`
gives rows `C_t-s_t in H`; projecting them yields a serving source-only space
of dimension at most `dim H`. Conversely a source-only space is an allowed
full-space choice. Thus the two minima agree, and choosing one local row per
target gives exactly

```
h(c) = min_{B_t in L_t(c)} rank(C - B R).
```

The residual row span attains each candidate rank. A minimum exists because
the possible ranks form a nonempty finite set of integers. Since each `L_t`
is a linear space, substitute `B=-12 A`. With `D=R^T/8-12 A`, the residual
is `I_104-D R`. The maps `R` and `D` restrict to mutually inverse maps between
`ker(I_104-D R)` and `ker(I_8-R D)`: if `x=D R x`, then `R x=R D R x`, and
conversely `z=R D z` gives `D z=D R D z`. These are kernel isomorphisms, not
claims that either rectangular map is globally injective. Since
`R D=13 I_8-12 R A`, rank-nullity gives

```
h(c) = 96 + min_{A_t in L_t(c)} rank(I_8 - R A).                 (1)
```

Let `E(c)=span_Q { r_t a : a in L_t(c) }` be the space of 8-by-8 matrices,
where `r_t` is column `t` of `R` and `a` is a row. The matrices `R A` are
exactly `E(c)`; row choices for distinct targets are independent.

## A linear test that certifies the early staircase

Let `U(c)` be the union span of all coefficient rows in all `L_t(c)`, of
dimension `r`, and also use `U` for any full-row-rank basis matrix. Every
`M in E(c)` has row space contained in `U`. Therefore `M z=0` on `ker U`,
so `I-M` fixes that `(8-r)`-dimensional space pointwise:

```
rank(I-M) >= 8-r.
```

Equality holds **if and only if** `U M=U`. For necessity, equality forces
`image(I-M)=ker U`, so `U(I-M)=0`. For sufficiency, this identity puts the
image inside `ker U`, while the fixed-point property supplies the reverse
inclusion. Thus feasibility of `U M=U`, `M in E(c)`, is an ordinary rational
linear-system question. Infeasibility strengthens `h(c)>=104-r` by one.

The verifier reconstructs every distinct eligible source projection through
cut 2717, forms `U` and `E`, and checks exact coefficient/augmented ranks at
the following right endpoints:

| Cut | `rank U` | `dim E` | `U M=U` feasible | Certified lower `h` |
|---:|---:|---:|:---:|---:|
| 2525 | 0 | 0 | yes | 104 |
| 2555 | 2 | 8 | no | 103 |
| 2571 | 2 | 13 | yes | 102 |
| 2617 | 4 | 27 | no | 101 |
| 2645 | 5 | 33 | no | 100 |
| 2717 | 6 | 45 | no | 99 |

[WITNESS.json](WITNESS.json) supplies respectively 1, 4, 6, 14 and 18 weighted
contacts at the five nontrivial **left** endpoints. A contact
`[target, cut, register, weight]` contributes its source coefficient
`weight * pi_X(v_register(cut)) R^T/104` to the corresponding row of `A`.
Each contact's availability and every dirty-input lifting premise are replayed.
The checker computes the exact rank both of `I_8-R A` and of the actual
104-by-104 matrix `K=C+12 A R`. Their ranks agree with (1); `row(K)` is a
serving space because `K_t-C_t` lies in `S_t(c)`.

The source-only 104-dimensional space is the trivial first upper witness.
Pools grow with the prefix, so `h(c)` is nonincreasing. Matching a left-end
upper bound to a right-end lower bound certifies every cut in each interval.
This is not a floating-point or finite-field search inference.

## Reproduce and inspect

Standard-library Python, read-only by default; the registered runner uses 3.12:

```sh
python3.12 -I -O -B research/p104-prefix-minrank/verify.py
python3.12 -I -O -B research/p104-prefix-minrank/test_verify.py
python3.12 scripts/research_package.py --package research/p104-prefix-minrank
```

Expected primary output: `PASS_P104_EARLY_PREFIX_MINRANK intervals=6 cuts=4059 columns=280`.
[RESULT.json](RESULT.json) is compared in full, including the six bounds,
110,814 distinct target/snapshot pairs and unchanged local profile. The dense
replay checks 280 independent columns on a checked denominator-eight integer
lattice, all frame transitions, owned private lifetimes, source/dirty helper
restoration and the original `G/2` endpoint. This is an algebraic trace replay;
it does not rerun the predecessor's native Clifford recipes.

`build.py --out NEW.json` optionally regenerates the contact certificate using
an independently written eight-coordinate rational projection search. It
imports no mathematical routines from the acceptance verifier. Its output must
equal `WITNESS.json`; it alone is not a check of arbitrary dirty inputs.
All output options refuse to replace an existing file.

Controls cover incorrect contact coefficients, unavailable/self or future
contacts, wrong paid rank, missing initial compensation and final cleanup,
the rectangular rank identity, and failures of both lifting hypotheses.
Checks use explicit exceptions/unittest assertions and run with `-O`.

## Open next questions

- **Resolve cuts 2718–2823.** Apply (1) to the exact small operator spaces.
  The one-step projector obstruction may leave a gap; seek rank-one/two
  residual certificates or stronger dual obstructions. This would complete
  the interval before the predecessor's `h=97` result at 2824. The blocker
  is constrained rational minimum rank, not another root/Gram calculation.
- **Realize an affordable chronological correction.** Choose a serving space
  and provide actual creation, frame paths, source reads, dirty restoration,
  owner scheduling and a complete recursive invoice. A dimension such as 99
  or 96 cannot be substituted for a paid transport count. Fixed-path
  obstructions and precision/all-size obligations remain applicable.

## Credit and scope

Gonzalo Mier / #2173 supplied the pooled-snapshot model and lower96/upper97
question. Gareth Davidson (@bitplane) / #2251 supplied the rational complement
construction and full-pool minimum96. The prefix-boundary handoff by @josecarlosgonzalezroque-design at
Discussion #2245 comment 18940216 supplied the prefix formulation, earliest96
cut and 97 interval, and explicitly left earlier prefixes open. This package
extends that algebraic problem; it does not claim their model, 96 lower bound,
or late-prefix result as new.

Rohan Arun / #1972 supplied the scalar/frame channel; Chafik Boukhalfa / #1991
its native realization; Adam Gall / #1940 the schedule; Josie Elliston / #1071
the fixture, with Ali Romman / #1125 and their retained geometry/decoder
lineage. Their original files and notices are unchanged.

AAAmirinu with substantial OpenAI Codex assistance in mathematics, code,
checking and writing, including separate AI-assisted exploration and proof
review. Evidence is author-checked, not independent human review or formal
proof-assistant verification. Apache-2.0. No native regeneration, global
hosting/moment, precision/all-size proof or selected cold replay is claimed.
