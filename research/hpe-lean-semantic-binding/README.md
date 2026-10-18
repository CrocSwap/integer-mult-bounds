# Independent semantic binding of the three Lean HPE pairs

**Independent finite audit; all comparisons pass. No new kappa or Lean theorem.**

The twelve frame and wrapper circuits in the retained
[`HyperplaneEnd/Exact.lean`](../hyperplane-end-lean/HyperplaneEnd/Exact.lean)
agree exactly with independent Gaussian-dyadic kernels and the retained Python
constructors. Both orientations pass on every one of the 512 basis inputs.
The three factorizations

\[
T_U T_E^{-1}=L(C_{[7]}\otimes I_4)R
\]

also pass, with global phase and both spectator coordinates retained.
These identities are already proved for the Lean definitions by Jeremy Kothe's
PR #593. This package adds a separately implemented, reproducible check of the
finite correspondence to the Python semantics; it does not claim priority for
the identities, or replace the existing formal proofs.

The claim is in [Discussion #1394](https://github.com/CrocSwap/integer-mult-bounds/discussions/1394).
The refined `formal-interface-lemma` card, exact heads, method and limitations
are in [TASK.json](TASK.json); input hashes and Git blobs are in
[SOURCES.json](SOURCES.json). Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

## Exact coverage

| Object | Domain | Checks |
|---|---|---|
| `fE1..3`, `fU1..3`, `wL1..3`, `wR1..3` | Twelve literal circuits | Exact circuit-list equality with the retained Python constructors |
| Same twelve operators and their inverses | 24 matrices, 512 columns each | Literal evaluator and source executor each equal an independent kernel |
| `lhsLit1..3`, `rhsLit1..3` | Six matrices, 512 columns each | Literal execution equals the composed independent kernels |
| Three residual factorizations | 512 columns each | Direct exact kernel equality, independent of the receipt hashes |
| Nine semantic faults per pair | 27 mutations | An explicit differing input/output coefficient for every fault |

The 24 primitive comparisons cover **12,288 columns and 6,291,456 matrix
entries**, including zeros. Each residual matrix has 65,536 nonzero entries
and a reduced common denominator of 16. Each terminal frame has 131,072
nonzero entries, also with denominator 16; each entrance frame has 1,024
nonzero entries and denominator 2. Each wrapper is a monomial matrix.

[RESULT.json](RESULT.json) records the complete coverage, matrix fingerprints,
literal fingerprints, source digests and counterexample coefficients. Hashes
compact the evidence; acceptance compares exact integer pairs and denominators.
Sparse representations include every nonzero entry, and equality therefore
checks the implicit zeros as well. Complex linearity extends basis equality to
every complex input vector.

## Independent kernel derivation

This is a derivation for the six fixed rank-one/rank-eight frames, using the
source's stated conventions. It does not assert an all-frame port theorem.

Let `U=(u_0,...,u_(r-1))` be one of these frame bases in `F2^9`. Extend it by
trying the coordinate unit vectors in ascending order, retaining a vector
exactly when it increases the span. Let `g` send coordinate bits to the XOR of
the retained columns, and `h=g^{-1}`. The independent implementation builds the
complete 512-element bijection by span enumeration; it does not call or port
the source's Gaussian-elimination inverse routine.

For the physical coordinate unit `e_i`, put `c_i=h(e_i)` and define

\[
Q_{ij}=\delta_{ij}+c_i\cdot c_j\pmod2,\qquad
\alpha_i=Q_{ii}\in\{0,1\},
\]
\[
q(x)=\sum_i\alpha_i x_i+2\sum_{i<j}Q_{ij}x_ix_j\pmod4.
\]

The source applies `K` as the permutation `g` followed by this diagonal phase:
`K e_z = i^{q(g(z))} e_{g(z)}`. Its frame circuit executes `K^{-1}`, then the
first `r` coordinate C gates, then `K`. Thus, for `delta < 2^r`, the only possible
output is `y=g(h(x) XOR delta)`, with coefficient

\[
(T_U)_{y,x}=2^{-r}i^{q(y)-q(x)}
  (1+i)^{r-|\delta|}(1-i)^{|\delta|}.
\]

All other coefficients are zero. The inverse conjugates the Fourier factors,
while retaining the displayed phase difference. This follows directly by
inverting `K F_r K^{-1}`. The kernel evaluates these powers in `Z[i]`.

For a serialized monomial `(Q,alpha,G,b,p)`, the separate formula is

\[
M e_x=i^{p+\sum_i\alpha_i x_i+2\sum_{i<j}Q_{ij}x_ix_j}
       e_{Gx\mathbin{\mathrm{XOR}}b}.
\]

Its inverse uses the enumerated inverse permutation and conjugate phase.
The independent kernel computes `Gx` by XORing columns and the phase by
explicit coordinate pairs. The literal evaluator instead uses row-mask
pullbacks and applies the parsed gates in order. The residual formula is
obtained by ordinary exact matrix composition. `C_[7]` only XORs bits 0..6;
the source's tensor map is `x -> (x mod 128, floor(x/128))`, so bits 7 and 8 are
the two spectators.

## Source and independence boundary

The audit uses three views:

1. **Closed-form kernels:** span enumeration and the formulas above. These
   import no producer, source state-vector executor, tableau or packed check.
2. **Literal execution:** a strict parser reads the twelve primitive and six
   composite gate lists from `Exact.lean`. A separate evaluator implements the
   `Clifford.lean` gate conventions, including pullback permutations. All
   permutation/inverse pairs are checked on the full 512-element domain.
3. **Source under test:** the byte-pinned `clifford_exact.py` constructs the
   frame circuits. Only the pure `monomial_op` function is extracted from the
   pinned HPE adapter module; its environment-dependent driver is not run.
   Constructor outputs must match the literal lists, and the source executor
   is compared against the kernel on all primitive columns, in both directions.

The source executor is an additional subject of comparison, not the oracle.
The kernels and literal evaluator share basic Gaussian-integer arithmetic and
exact comparison utilities. They are separate algorithms, not separate human
implementations or proof-assistant developments.

The existing [`verify_hpe_lean_binding.py`](../../scripts/verify_hpe_lean_binding.py)
compares emitted recipe records with `pair1..3`. Its historical
[`lean-bindings.json`](../community-hyperplane599-audit/lean-bindings.json)
receipt is pinned as context; this audit does **not** regenerate those emitted
38-helper words or revalidate that receipt's underlying runs. The new check
starts at the three fixed pair records and validates their operator semantics.

## Controls and interpretation

For each pair, the verifier rejects a global phase change, translation change,
reversed permutation direction, input character, C-sign change, replacement of
an active C axis by spectator bit 7, swapped wrappers, reversed circuit order,
and omission of the entrance inverse. Every rejection stores an exact witness.

The input-character control illustrates the need to retain all input columns:
adding 2 to the first right-wrapper linear phase preserves the zero-input
column and negates precisely the 256 odd-indexed columns. For pair 1,
input 1/output 4 changes from `(1-i)/16` to `(-1+i)/16`.
This is a boundary of a zero-column-only comparison, **not a reported defect**
in the source compiler, whose separate tableau check is outside this audit.
PR #702 and PR #712 already discuss analogous phase controls for different,
rank-four cold wrappers; their priority is retained.

The focused tests additionally check `C(q)^2=X(q)` and `C(q)^*C(q)=I` on five
specified masks and all 512 inputs; a corrupted frame literal; malformed or
duplicated declarations; an incorrect permutation inverse; changed source
bytes; receipt digest/type/duplicate-key corruption; output overwrite refusal;
and an isolated optimized replay from a copy whose input/package files are
read-only. Normal verification never rewrites the receipt.

## Reproduce

Standard-library Python 3.12; no Lean, GPU, network or third-party packages.
Run from the repository root:

```sh
python3 -I -B research/hpe-lean-semantic-binding/verify.py
python3 -I -B -m unittest discover -s research/hpe-lean-semantic-binding -p test_verify.py
python3 -B scripts/research_package.py --package research/hpe-lean-semantic-binding --check-only
python3 -B scripts/research_package.py --package research/hpe-lean-semantic-binding
```

The last command runs the verifier and the seven focused tests. Expected direct
output:

```text
PASS_HPE_LEAN_SEMANTIC_BINDING pairs=3 operators=24 operator_columns=12288 factorizations=3 controls=27 no_new_lean_build no_new_kappa
```

A direct replay takes about 30 seconds in the measured CPython 3.12.3
environment; timing is informational. The standalone audit also works in a
source export containing the declared inputs. The generic package metadata
check needs Git history to check provenance.

To create a separate receipt, use `--write-receipt NEW_FILE`; an existing file
is refused. Canonical receipt comparison preserves JSON types and rejects
duplicate keys. `--receipt FILE` checks a different expected receipt without
modifying it.

## Limitations

No Lean installation, kernel build or fresh axiom audit was performed. The
theorems and their proof-assistant trust base remain those of the retained
package. This finite result covers only the three fixed pair records and
their listed literals, not arbitrary frames, all selected helpers or future
source revisions. Hash pins deliberately reject source drift.

Scalar-word restoration, helper rows/columns, wrapper placement, tail
chronology, physical hosting/footprints, compiler uniformity, precision/tape,
complete recursive costs and analytic transfer are not checked here.
The selected construction, selected record and predecessor packages are
unchanged. No new physical supplier or improved exponent is claimed.

## Open next questions

- **Can the source-to-formal gate semantics be proved for a shared serialized
  circuit grammar?** This would reduce the manual semantic-translation trust
  boundary. A feasible first step is a small formal interpreter for the five
  gate tags and an explicit correspondence theorem for permutation and C
  gates. The blocker is a formally specified Python execution semantics or a
  separately verified shared compiler, not more finite examples.
- **Can one current emitted helper be bound end-to-end to this finite audit?**
  That would join the operator check to an actual invocation. Start with a
  pinned emitted word containing one of the three certified pairs, trace both
  wrapper records and their actual event positions, and verify the unit row
  and remaining label/hosting hypotheses. A raw pair match alone does not
  discharge those obligations. This package supplies no such new admission.

The same questions and blockers are structured in [TASK.json](TASK.json).

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Jeremy Kothe / `jeremykothe2` supplied PR #593's exact Clifford formalization,
the three pair records and their formal factorization proofs.
DreamingOfClouds supplied the Lemma A/G line, HPE wrapper definitions and
PR #599's multi-gate/cold extension. The Clifford engine is retained from
icekylinx's `split-centres-global` lineage. Chafik Boukhalfa / `chafreaky`,
Zhihao Chen / `jacklightChen`, and the realization/hosting contributors named
in the retained [NOTICE](../hyperplane-end-lean/NOTICE.md) retain their credit.

Nearby independent audits are BigCactusLabs' PR #702 (all fourteen historical
rank-four cold wrappers), Joshua Snider / `jsnider3`'s PR #712 (a symbolic
quadratic certificate for one such wrapper), and Gareth Davidson / `bitplane`'s
PR #1255 (selected physical chart phases). None is an implementation dependency.
The operator-domain and semantic-port focus here differ from those audits.

New code and prose are Apache-2.0 under the repository [LICENSE](../../LICENSE).
No source package is copied or modified. Substantial AI assistance covered
research, derivation, implementation, checking and writing; no independent
human review is claimed.
