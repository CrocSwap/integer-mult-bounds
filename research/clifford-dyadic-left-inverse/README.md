# Exact Gaussian-dyadic Clifford recovery at sufficient tensor width

**Algebraic construction; no new κ.** For the full four-qubit projective
Clifford alphabet, every integer tensor width `f >= 256` admits a left inverse
whose coefficients all lie in `R = Z[i,1/2]`. This answers the noncanonical
left-inverse question in [PR #7792](https://github.com/CrocSwap/integer-mult-bounds/pull/7792)
at an explicit sufficient width. It does not determine the least width or
supply an affordable physical decoder.

The [proof](PROOF.md) establishes the stronger raw-tensor statement for every
`n >= 1`: width `f >= 4n2^n` suffices. For four qubits, the source map is

```text
A_f[:,a] = vec(U_a^(tensor f)) / 2^(2f),
B_f A_f = I,       B_f has entries in Z[i,1/2].
```

There is one column for each scalar coset modulo `<iI>`, with arbitrary fixed
representatives. The columns generate a direct summand, hence a saturated
module, over R. At `f=257`, the canonical least-squares map requires odd
division by #7792, while this different exact left inverse does not. The
canonical result and this construction are compatible.

## Construction

Let `d=2^n`, let `P_j` run through the `2n` Hermitian generators `X_j,Z_j`,
and put `Q_(a,j)=U_a P_j U_a*`. For a variable matrix X define

```text
Delta(X) = det X,
t_(a,j)(X) = Tr(Q_(a,j) X P_j adj(X)) / d,
h_(a,j)(X) = (t_(a,j)(X)^2 + t_(a,j)(X) Delta(X)) / 2,
F_a(X) = product_(j=1)^(2n) h_(a,j)(X).
```

Each factor evaluates to `Delta(U_b)^2` times the indicator that the two
signed Pauli images agree. The determinant lies in `{1,i,-1,-i}`, so the
phase cancels across `2n` factors. Agreement on all generators identifies a
scalar coset. Thus `F_a(U_b)=delta_ab`, with homogeneous degree `4nd` and
only dyadic denominators. Multiplying by
`(Tr(U_a*X)/d)^(f-4nd)` pads to every larger width.

A coefficient of each commutative monomial is assigned to one ordered tensor
word. This makes the polynomial a linear tensor functional without dividing
by factorials or multinomial coefficients. The full matrix is specified
algebraically, not materialized.

## Verification

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-dyadic-left-inverse
```

`VERIFY.json` registers normal and optimized runs of both implementations.
All four runs pass on CPython 3.12.14 (macOS arm64).
They use exact rational Gaussian arithmetic and explicit checks that remain
active under `-O`. The written proof supplies the infinite quantifiers.

- `verify.py` expands commutative one-qubit polynomials, chooses sorted tensor
  words, and checks the normalized left-inverse identity. It also checks
  literal four-qubit matrix examples and authenticates the retained sources.
  Coverage: 1,392 commutative polynomial coefficients, all 576 one-qubit
  left-inverse entries, 256 literal tensor coordinates, 16 four-qubit matrices,
  128 generator images, 2,048 pairings and 256 interpolation entries. Six
  faulty variants and three mutated source files are rejected.
- `independent_check.py` imports no primary or predecessor implementation.
  It enumerates operators by their entries and expands noncommutative ordered
  coordinate words. Its complete one-qubit calibration has 96 matrices, 24
  projective cosets, 2,304 interpolation pairs, 6,912 phase-padding cases,
  576 normalized left-inverse entries, 12,288 row terms and 1,536 tensor
  coordinates. Five faulty variants are rejected.
- Phase controls include 48 matched lifts for which both individual detector
  factors are minus one. Omitting the determinant or the signed term changes
  the map. The non-Clifford CCZ example gives `27/512`, showing why unitarity
  and dyadic entries alone are insufficient.

These are finite implementation checks, not a full four-qubit enumeration or
formal-kernel proof. No character table, predecessor executable, Lean, Docker,
selected scientific cold replay or complete multiplication program is run.
The selected source-binding orientation passed separately.

## Sources, overlap and attribution

Canonical main was pulled on 2026-11-19 at
`e54523517d0f03e58352e647c403a5af3e525a57`. Priority revision 8 is older than
the selected #7000 record; the task is explicitly a changed-scope algebraic
side result of `uniform-transfer-audit`, not discharge of a selected caller
assumption. [TASK.json](TASK.json) retains the original card and the bounded
family decision.

[SOURCE-PINS.json](SOURCE-PINS.json) records exact commits, original Git blob
IDs, SHA-256 hashes, URLs and byte lengths for three unmodified proof files:

- Ali Romman's #7792 canonical obstruction at
  `9321c67e29c3c41a188154bc5c2add7d7802b694` supplies the open question and
  the canonical comparison.
- Ali Romman's #7788 at `9a8ce06644700ffa576d99316450bcb52835d6dc`
  supplies the four-qubit tensor normalization and alphabet size.
- alephnan's #6714 at `f7f32a18dde54e67624a9ed9cc7e1b266d9585c0`
  supplies the Gaussian-dyadic scalar and Pauli framework.

Their proof bytes are retained inside this package so an exported replay
needs neither network access nor unmerged Git objects. `SOURCES.json` binds
the base catalogue and selected record as historical provenance; the
separate source manifest binds these package-local retained proofs. The new
interpolation proof is elementary and independent of the character-table
computations; only its comparison with the canonical inverse uses their
reported spectral theorem.

Fresh all-state PR searches and the newest direct PR-body corpus found no
matching positive construction. The repository overlap helper could not
fetch remote corpora because `gh` was unavailable. Discussion snapshots and
sparse local notes are incomplete; this is not a global novelty guarantee.
Newer cubic work #7506/#7543 was checked before choosing a different family.
The scoped [claim](https://github.com/CrocSwap/integer-mult-bounds/pull/7792#issuecomment-7012504080)
records this investigation on its source question. No predecessor package or
shared implementation is changed.

Prepared by **apoursh**, with substantial **OpenAI Codex and separate agent
assistance** in proof, implementation and review. Credit Ali Romman,
Nick Petalas, alephnan and their retained predecessor lineage. Classical
adjugate, Pauli orthogonality, interpolation, tensor lifting and module
arguments are not claimed as new. Source notices remain intact. Apache-2.0.
No independent human acceptance or proof-kernel verification is claimed.

## Limits

A left inverse is exact on the image: `B_f(A_f c)=c` for every coefficient
vector. On arbitrary noisy observations its error is `B_f e`; no useful
norm or stability bound is supplied. Precision, movement, storage, native
preparation, owned-state restoration and the complete caller bill remain
unknown. No new supplier, physical speedup or κ follows.

## Open next questions

1. Determine the smallest width that admits an R-left inverse. Start with
   the actual module or modular ranks at widths near the complex independence
   threshold 13. The canonical Gram denominators alone cannot decide this;
   widths 13 through 255 remain unresolved by this contribution.
2. For a specified caller, bound and price a chosen noncanonical decoder.
   First derive its recovery norm and a complete evaluation/restoration bill.
   Algebraic existence is insufficient justification for a large implementation.

The structured questions and blockers are also in `TASK.json`.
