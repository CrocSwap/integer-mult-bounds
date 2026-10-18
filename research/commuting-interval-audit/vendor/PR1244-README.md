# Ordered-subset bounds do not give linear interval amplification

**Adversarial mathematical audit / scoped negative result; no new kappa.**
For the unchanged PR628 balanced dirty dispatcher, invertible factors can have
every ordered subset product bounded by `G`, yet an interval between two leaf
boundaries amplifies a perturbation by at least `1+G^2`. Seven factors suffice
even when the perturbation is restricted to the immediately preceding leaf's
destination. The complete ideal word has norm two and restores its dirty arrays.

This makes the quadratic dependence on `G` unavoidable for a **generic
noncommuting interval bound based only on ordered subsets**. It supports the
retained conservative step in [PR905's proof](../dirty-cubic-precision/PROOF.md),
which uses two prefix bounds. It does not find a bug in that proof or establish
a failure of its actual cyclic leaves. Those leaves have the additional common
operator/commutation hypothesis, which this witness deliberately fails.

## Exact statement and proof

Use the maximum norm on each two-dimensional real array and on their joint
state; the induced matrix norm is the maximum absolute row sum. An ordered
subset product is `A_jk ... A_j1` with `j1 < ... < jk`, including the empty
product. Factors act on column vectors. For every real `M >= 1`, set

```text
J = [[0, M], [-1/M, 0]],    D = [[1/M, 0], [0, M]].

||J|| = ||D|| = M,
D J = [[0, 1], [-1, 0]],   ||D J|| = 1,
J D = [[0, M^2], [-1/M^2, 0]],
||I - J D|| = 1 + M^2.
```

Both `J` and `D` have determinant one. In the seven-factor word choose `A_1=J`,
`A_4=D` and every other factor equal to the identity. Every ordered subset
product is one of `I,J,D,DJ`, so its norm is at most `G=M`. The complete factor
product is `DJ`, with norm one. The ideal full word is the source-to-target
shear with that product and identity on all dirty scratch; its norm is two.

The pinned dispatcher splits a factor interval at its floor midpoint, uses
one distinct dirty connector per depth, and expands a positive node as
`U,V,U^-1,V^-1`. Negative nodes reverse and negate that literal word. In the
seven-factor positive word there are 52 leaves. Number ports as `0=x`, `1=y`,
`2=z0`, `3=z1`, `4=z2`; number leaves from zero. A cut `t` is after the first
`t` leaves, so interval `[s,t)` executes leaves `s,...,t-1`.

Consider `[13,27)`. Leaf 12 is `z2 -= A_3 z0`, so `z2` is an allowed local
error destination at cut 13. Start the *difference* between two executions
with `z2=v` and all other ports zero. The fourteen leaves are:

```text
13  z1 -= D z2       20  z1 -= D z2
14  z2 += z1         21  z2 -= z0
15  y  += z2         22  y  += z2
16  z2 -= z1         23  z2 += z1
17  y  -= z2         24  y  -= z2
18  z1 += D z2       25  z2 -= z1
19  z2 += z0         26  z2 += J z1
```

Throughout, `x=z0=0`. Direct substitution gives the following difference
states; this is a symbolic computation valid for every vector `v` and every
`M>=1`, not an extrapolation from a finite parameter search.

| Cut | z1 | z2 | y |
|---|---|---|---|
| 13 | 0 | v | 0 |
| 14 | -Dv | v | 0 |
| 18 | -Dv | v | -Dv |
| 22 | -Dv | v | -Dv |
| 26 | -Dv | v | 0 |
| 27 | -Dv | (I-JD)v | 0 |

For `v=(1,-1)`, the entry norm is one and the final `z2` norm is `1+M^2`.
Consequently, even on this actual leaf-destination input subspace, no bound
`C(7) G^q` with a finite constant independent of `G` and exponent `q<2` can
hold for all these factors. PR905's valid generic bound is `C_n^2 G^2`, where
`C_n=2*3^ceil(log2 n)`; only the power of `G`, not that coefficient, is sharp
here. The example's problematic monomial is squarefree but in the wrong order.

There is also a four-factor witness: take `A_1=J`, `A_2=D`, others identity.
In its 16-leaf word, `[5,9)` has diagonal block `I-JD` on `z0`. However, leaf
4 writes `z1`, not `z0`. This smaller example concerns arbitrary state
perturbations and must not be presented as a leaf-destination example.

## Reproduce and inspect

From the repository root, with Python 3.12 and no third-party packages:

```sh
python3.12 scripts/research_package.py --package research/dirty-interval-propagator-audit
```

The hook checks source provenance, runs the verifier under isolated optimized
Python, and runs seven package tests. Expected final status:
`PASS_REGISTERED_RESEARCH_PACKAGE research/dirty-interval-propagator-audit outcome=negative-result`.
The standalone mathematical check is
`python3 -I -O -B research/dirty-interval-propagator-audit/verify.py`.
It must print `PASS_DIRTY_INTERVAL_PROPAGATOR_AUDIT intervals=9772 leaf_supported=9342`
and compare its complete deterministic output with [CERTIFICATE.json](CERTIFICATE.json).
It normally writes nothing; `--write NEW_PATH` creates a new receipt exclusively.

Evidence and limits:

- All **9,772 nonempty intervals** for `n=1..8`, both signed words, are expanded
  in the free noncommutative algebra with exact integer coefficients. Of these,
  **9,342** start after a leaf and admit a preceding-leaf destination column.
  An unordered monomial first occurs at `n=4` for unrestricted columns, and
  at `n=7` for those destination columns. This is exact finite minimality of
  the *order-property failure* in this dispatcher, not a theorem about other
  circuits. The enumeration records no repeated factor within a monomial in
  this finite domain; no all-size multiaffinity claim follows.
- The separately expanded word is compared with the actual pinned `compose`
  function for 26 signed cases at counts `1..9,12,16,31,64`. Only that function's
  AST is executed, with leaves instrumented as a recorder and all its admission
  checks active. Predecessor numerical modules are not imported. This checks
  the dispatch schedule, not the numerical implementation of a leaf.
- Sixteen exact dense cases cover both witness sizes and
  `M in {1,2,3,4,7,16,64,257}`. They check all 16 or 128 ordered subsets,
  determinant one, the complete dirty-state map, and interval matrices three
  ways: free-algebra evaluation, full dense shear multiplication, and
  `P_t P_s^-1` with independent Gauss-Jordan inversion. A separate vector
  interpreter compares two nonzero dirty trajectories.
- A positive control checks the ordered-monomial prefix and inverse-prefix
  contract at all 446 boundaries for `n=1..8`, both signs. Inverse prefixes
  are built by right column updates rather than forward row updates.
- Six mathematical controls distinguish order, commutation, the stronger
  all-permutations premise, the false four-factor injection interpretation,
  a truncated interval and a sign fault. Package tests reject source drift,
  a changed certificate and an occupied output path, and reproduce the exact
  receipt in a read-only minimal copy at a path containing spaces.

The exact base is `49b3157d1d89adcef16df8be98445451672be5ba`.
[SOURCES.json](SOURCES.json) pins consumed source bytes with Git blobs and
SHA256; the hook additionally resolves them in the base Git history. The
selected certificate at that base has conditional
`kappa=836330098538459/500000000000000000` and remains unchanged. This package
does not run the selected supplier's cold replay.

## Scope and interpretation

The failed implication is "ordered subset norm at most G implies a generic
interval norm at most C(n)G." It is not a failed search and not a counterexample
to the retained `B^2` argument. Source and target are distinct, all scratch
ports are distinct by depth, factors are fixed invertible linear maps, and
every inverse/restoration leaf remains in the word.

An injected disturbance supported on a leaf destination is an admissible
input to a local-error transport lemma. We do **not** claim that the single
impulse pattern is generated by the particular deterministic rounded cyclic
leaves, whose forward/inverse errors can be correlated. This package does
not establish a minimum working precision for those leaves. For `M>1`,
`JD!=DJ`, so the family cannot consist of rational functions of one common
operator. It therefore does not challenge PR905's common-isometry hypothesis,
PR1054's all-length cyclic precision result, or the common conjugation in
PR1038. Physical/compiler, hosting, source-access, precision/tape, preparation,
analytic-transfer and selected bit H1-H5 obligations are not discharged.
No supplier, recurrence invoice or multiplication exponent is changed.

## Open next questions

Does the common-operator case admit an interval bound linear in its subset
budget? The finite census has only squarefree monomials through eight factors;
commutation then removes their order issue. A useful first step is an induction
over the two endpoint subcalls that proves or refutes squarefreeness at every
size, retaining the reuse of deeper scratch between siblings. A finite replay
does not supply that induction. This would be relevant to tightening the
existing cyclic precision estimate; the present noncommuting obstruction
does not close that route. The structured question and stopping rule are in
[TASK.json](TASK.json).

## Credit and overlap

Credit Chafik Boukhalfa (@chafreaky) for PR628's dispatcher and PR905's free
prefix/common-operator argument; Gareth Davidson (@bitplane) for PR877's
inverse-prefix and nonlinear perturbation analysis; and the retained source
lineage. PR628 is pinned at `0768f97d06c623b8211e651543c66135796b62bf`, PR905 at
`aab6c0b8f4574cb36285ab5dab3fcfad0cd2b69e`, and PR877 at
`80a60c0da2b916798167deb0ce3a5ef22fda147a`. Their original files remain unchanged.

Hanson Sun's PR1085 (`82b99c7d12dac009d35636562df4c6c91e885409`) sharpens the
prefix coefficient count; it does not supply this two-cut obstruction.
PR1054, PR1093 and PR1211 address all-length cyclic accuracy, a different fixed
word's error budget and factor-tape travel respectively. This package adds a
parametric noncommuting obstruction with a genuine leaf-destination cut and
finite minimality evidence. The entry and final overlap checks are recorded in
TASK.json; absent matches do not establish literature priority.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in research, proof, code, checking and writing. Independent implementations
are used inside the audit; no independent human or proof-assistant review is
claimed. New work is Apache-2.0. Predecessor licenses and attribution remain
intact. Assignment seed **64** was drawn once from OS randomness; it selects
the audit track, displayed scale and extra dispatcher count, not novelty.
