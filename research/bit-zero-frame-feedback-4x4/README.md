# Zero-frame target feedback: exact four-helper/four-target census

**Finite exact negative result; no new supplier or kappa.** For every binary
4-by-4 K, allowing targets to feed helpers does **not** shorten the minimum
fully restored circuit

    (h, y) -> (h, y + K h)

on eight arbitrary dirty registers with unit-cost single-source XORs and no
extra registers. This answers the next question of
[PR1557](https://github.com/CrocSwap/integer-mult-bounds/pull/1557) (3-by-4),
which extended the merged 3-by-3 census of
[bit-zero-frame-feedback](../bit-zero-frame-feedback/README.md) (PR1306). The
model, the two alphabets and the prefix-substitution lemma are PR1306's,
unchanged. The scope is recorded as a refinement of `bit-helper-contract` in
[TASK.json](TASK.json).

## Result

All 65,536 labeled K, in 317 orbits under target and helper permutations, have
the same minimum in both alphabets:

| Minimum XORs | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Number of K | 1 | 16 | 120 | 560 | 1,820 | 4,416 | 8,452 | 13,040 | 16,002 | 14,372 | 6,329 | 384 | 24 |

* The maximum, 12, is attained exactly by the 24 matrices `J - P` (all ones minus
  a permutation matrix): every row has weight three and the rows are distinct.
  Twelve direct helper reads are optimal there. No restricted or unrestricted
  word of at most 11 gates exists.
* The 408 K needing more than ten gates form three orbits. Two of them (288 K of
  weight 11, 96 K of weight 13) cost exactly 11 in both alphabets. The weight-13
  orbit is two gates below its direct count, and that saving already exists
  without feedback. The remaining 24 K form the J − P orbit, which costs 12.

[CERTIFICATE.json](CERTIFICATE.json) has the histogram, the cost of every K
(`costs_hex`, indexed by `K[i][j]` = bit `4i + j`, target `i`, helper `j`) with
its SHA256, sphere sizes, the hard-case receipts, and for each orbit
representative an attaining restricted word.

## Method and lower-bound argument

A gate `[d, s]` is left multiplication by `E = I + e_d e_s^T` over F2. The required
map is `T_K = [[I, 0], [K, I]]`. The shears `N = {T_K}` form an elementary abelian
group, with `T_K T_K' = T_{K+K'}` and `T_K^2 = I`.

**Coset keys.** `T_K U` changes only the target rows of `U`, adding combinations
of its helper rows. Two invertible matrices therefore lie in one coset `N U`
exactly when their helper rows agree and their target rows agree modulo the span
of those helper rows. `verify.py` keys each matrix by its helper rows and its
target rows reduced against a row-echelon basis of that span (zero at the pivot
columns). This is a canonical form of the coset. Within a coset, every element
is `T_label * anchor`, and two elements with labels `a`, `b` give `T_{a xor b}`.

**Exactness to ten gates.** For each alphabet, `verify.py` builds the exact
radius-5 BFS ball and records every same-coset pair `(U, V)` whose depths differ
by at most one. Each pair is an upper bound: `T_K = V U^-1` costs at most
`d(U) + d(V)`, since gates are involutions. Conversely, let `w` be a minimal word
of length `L <= 10` for `T_K`. Its first `floor(L/2)` gates `P` and last
`ceil(L/2)` gates `S` are themselves geodesic, because they are subwords of a
geodesic. So `U = P^-1` and `V = S` lie in the ball, at depths differing by at
most one, with `V = T_K U`. The census minimum therefore equals the true minimum
whenever it is at most ten. If no pair gives at most ten, the minimum exceeds ten.

**Beyond ten gates.**

* *Weight-11 and weight-13 orbits:* the census shows both alphabets exceed ten
  gates. An 11-gate restricted witness is replayed, so both costs are exactly 11.
* *J − P orbit, restricted:* a word of exactly 11 gates splits into a geodesic
  first part of six gates and a last part of five. No `X` in the exact restricted
  sphere 6 has `T_K X` in the restricted radius-5 ball. 12-gate words exist.
* *J − P orbit, unrestricted:* `J - I` is fixed by permuting helpers and targets
  by the same `sigma` in S4. Relabeling a word by `sigma` gives another word for
  the same `T_K` and length, so the first gate can be assumed to be one of six
  orbit representatives. These are `hh`, `yy`, `y_a<-h_a`, `y_a<-h_b`, `h_a<-y_a`
  and `h_a<-y_b`, with orbit sizes 12, 12, 4, 12, 4 and 12. With
  `X = E_g Y` for `Y` in the radius-5 ball, no `T_K X` lies in that ball, so no
  unrestricted word of 11 gates exists. Every other K in this orbit follows by
  permutation invariance.

Permutation invariance holds because conjugating by a helper permutation and a
target permutation maps each alphabet to itself and maps `T_K` to a permuted K.
The primary check also confirms it numerically on the computed costs.

## Independent evidence

[independent.py](independent.py) imports no primary or predecessor code. It
differs from `verify.py` in four ways:

* matrices are column-packed rather than row-packed;
* lower bounds come from a per-orbit direct lookup of `T_K X` in the
  unrestricted ball, with no coset grouping;
* the J − P exclusion normalizes the last gate rather than the first;
* every one of the 65,536 labeled K gets its orbit's witness transported by
  register renaming, replayed on all 256 dirty inputs and checked against
  `costs_hex`.

An unrestricted lower bound also bounds the restricted alphabet. Both checkers
rest on the meet-in-the-middle principle, so this is independent code and
decomposition, not an independent mathematical method.

A third, unregistered cross-check takes about 8 minutes. It scans all 56 first
gates for J − I with no symmetry reduction, and also found no word of at most
11 unrestricted gates.

Both checkers reproduce published data:

* `verify.py` reproduces the PR1306 3-by-3 histogram (read from its pinned
  certificate) and the PR1557 3-by-4 histogram
  `[1,12,66,220,495,810,1017,922,529,24]`, in both alphabets.
* The sphere sizes match the PR1306 table for 3-by-3.

The 4-by-4 sphere sizes at radii 0 to 5 are:

| Alphabet | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Restricted (40 gates) | 1 | 40 | 936 | 16,428 | 234,224 | 2,808,680 |
| Unrestricted (56 gates) | 1 | 56 | 1,904 | 50,316 | 1,121,820 | 21,927,640 |

Controls:

* **Positive:** both predecessor reproductions; a cost-11 K found by the same
  normalized search machinery used for J − P; attained-word lookups for 40
  orbits in the independent check.
* **Negative:**
  * a radius-4 census must leave K unresolved;
  * a cancelling feedback pair is accepted only in the unrestricted alphabet;
  * a truncated witness, a wrong target map, a self-XOR and a Boolean register
    index are each rejected;
  * a valid but longer word labeled optimal is rejected;
  * a tampered minimum is rejected.

Both scripts refuse to run under `-O`.

## Reproduce

Python 3.12 with `numpy==2.4.0`, from the repository root:

```sh
python3 scripts/research_package.py --package research/bit-zero-frame-feedback-4x4 --check-only
python3.12 scripts/research_package.py --package research/bit-zero-frame-feedback-4x4 --install-deps
```

The registered replay runs three commands:

```sh
python3 -I -B research/bit-zero-frame-feedback-4x4/verify.py --stage census
python3 -I -B research/bit-zero-frame-feedback-4x4/verify.py --stage hard
python3 -I -B research/bit-zero-frame-feedback-4x4/independent.py
```

Expected lines:

```text
PASS_ZERO_FRAME_FEEDBACK_4X4 maps=65536 orbits=317 max_minimum=12 feedback_gains=0 controls=11 no_new_kappa
PASS_ZERO_FRAME_FEEDBACK_4X4_HARD jmi_minimum=12 jmi_words_le11=0 both_alphabets no_new_kappa
PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK_4X4 labeled_maps=65536 orbits=317 dirty_inputs_per_map=256 max_minimum=12 feedback_gains=0
```

`verify.py --write` regenerates the certificate deterministically.

Each stage took about 2.5 minutes (census and hard, run concurrently) and the
independent check about 1.5 minutes, on the donation host: Windows 11, CPython
3.14, numpy 2.4.0, 64 GB RAM. The largest arrays are the 23.1M-element
unrestricted ball and its level-5 expansion (about 63M candidates); peak memory
was not measured. CPython 3.12 was unavailable on the host. The registered 3.12
replay was therefore **not** run locally; `--check-only` was. Local runs omitted
`-I` because numpy is installed in the host's user site directory.

## Limits and unchecked obligations

The equality is proved only for:

* H = T = 4, over F2;
* PR1306's two single-source unit-cost alphabets;
* no extra registers, with all inputs arbitrary.

It is not a theorem for larger dimensions, other gate costs, multi-source
gates, nonzero frames or other fields.

**Exploratory, not certified:** every other shape with at most eight registers
that PR1306 and PR1557 left open was also checked with the same census code.
These are 1x4, 1x5, 2x4, 1x6, 2x5, 1x7, 2x6 and 3x5; transposes are equivalent
by the `M -> M^-T` duality. All give elementwise-equal costs in both alphabets,
with every K resolved within the exact ten-gate horizon. The maxima are 4, 5, 6,
6, 7, 7, 8 and 10. Reproduce one shape with:

```sh
python3 -B research/bit-zero-frame-feedback-4x4/verify.py --shape H T
```

These shapes have no witnesses, independent check or registered replay here.
Together with PR1306 and PR1557, they suggest no feedback gain for any shape with
at most eight registers. Only 4-by-4 is certified.

No fixed R439/R420 word was edited, and no physical supplier, precision/tape
bound, hosting, all-size compiler, native replay or recursive moment was built
or checked. The selected frontier's cold replay was not rerun for this isolated
finite result.

## Open next questions

1. **Is there a general no-feedback theorem, or a counterexample beyond eight
   registers?**
   * *Why it matters:* a proof, equivalent to geodesic convexity of the
     block-lower-triangular parabolic subgroup of GL(H+T, 2) under unit
     transvections, would close this D-local relaxation for every prefix size.
     A counterexample would be the first legal cheaper prefix to price
     physically.
   * *First step:* certify the exploratory shapes above (witnesses and an
     independent check, as here). A K on H helpers and T targets costs the same
     as its transpose on T helpers and H targets, by the duality `M -> M^-T`,
     which reverses every gate. Then look for a structural reason in the
     incompressible extremal `J - P` family.
   * *Blocked by:* there is no proof idea yet. Nine registers (4-by-5, 3-by-6)
     need radius-6 unrestricted balls (hundreds of millions of matrices) or a
     new reduction.

The structured version is in [TASK.json](TASK.json). The 4-by-4 domain itself
needs no further search.

## Credit

Prepared for rtyu193-rgb with Claude Code (Anthropic Claude Opus 5.5), which
designed the coset method, wrote both checkers and drafted this README. This
was one session with no subagents and no independent human review. New work is
Apache-2.0.

This package claims the finite 4-by-4 census and its certificate. It does not
claim novelty for elementary matrix substitution, CNOT synthesis or
meet-in-the-middle search.

**Predecessors:**

* @commdata2338's PR1306 (`bit-zero-frame-feedback`): the model, the
  substitution lemma, the meet-in-the-middle setup and the original handoff.
* @bbMisk (Hanson Sun)'s
  [PR1557](https://github.com/CrocSwap/integer-mult-bounds/pull/1557)
  (`15e0987e5fa88d1c15699215ac0cd70b47a535a6`): the 3-by-4 census and this
  next question.
* @woklerx's PR1194 and PR1105, and Arham Tahir's PR1311: the semantic-D and
  feedback-cleanup lineage.

**Underlying bit-word and checker lineage:**

* Zhihao Chen (PR425), eumemic (PR555), DreamingOfClouds (PR589), Gareth
  Davidson (PR926), @theon199 (PR967);
* Sagar Thakrar (PR1062), with Aaron Wang (PR1015) and Ross Richardson (PR923).

No predecessor code is imported. The PR1306 certificate is read as a pinned
input for the reproduction control.
