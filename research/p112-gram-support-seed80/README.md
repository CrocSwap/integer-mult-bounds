# Label-free Gram certificate for the P112 support lemma

**Independent finite verification; no new kappa.** This corroborates the
finite geometry lemma in [PR845](https://github.com/CrocSwap/integer-mult-bounds/pull/845),
[PROOF.md, “Finite geometry lemma”](../p112-single-lift/PROOF.md#finite-geometry-lemma),
by a different representation and certificate. It additionally gives the sharp
uniform restricted-energy constant **4** on its 503 full-rank supports.
The rank census and its application to the single-lift obstruction belong to
Mihir Srivastava's PR845; no defect in that proof is alleged.

## Reproduce

From the repository root, Python 3.10+ and standard library only:

```sh
python3 -I -O -B research/p112-gram-support-seed80/verify.py
```

Expected:

```text
PASS_P112_GRAM_SUPPORT characters=511 full_rank=503 coordinate_kernels=8 spectra=10 sharp_energy=4 controls=7 no_new_kappa
```

Default execution is read-only: it checks source hashes and compares the entire
recomputed receipt with `RESULTS.json`. `--write /path/to/new.json` emits a new
receipt instead; an existing output is never overwritten. All checks remain
active under `-O`.

Base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
PR845 head: `125ce25bdae421627b56077adc14940c2d0aa52f`.
PR717 geometry head: `4150829a2cb66b823f4282da98985959ee448a90`.
`SOURCES.json` pins five immutable predecessor files in this checkout, including
the exact geometric snapshot and its notices. No network or predecessor code is
executed. The selected certificate at the base has conditional
`kappa = 1661960547713947/10^18`; neither that certificate nor `upstream/` changes.

## Exact object and new evidence

Let R contain one representative of each E8 root line, excluding the eight
orthogonal frame lines `e_(2j) +/- e_(2j+1)`. Normalize roots to norm squared two.
There are 112 remaining lines. Define `X_ij = <r_i,f_j>` and the binary pairing
matrix `B_it = 1 + <r_i,r_t> (mod 2)`. The implementation uses twice the roots,
so its integer dot products are divided by four. X has entries 0, +1, -1.

Enumerate each nonzero word w in the **row space of B**, and let
`I(w) = {i : w_i = 1}`. For `A_w = X[I(w),:]`, form the integer 8-by-8 matrix
`H_w = A_w^T A_w`. The complete spectrum census is:

| Eigenvalues, with multiplicities | Number of characters |
|---|---:|
| 0, 32 (seven times) | 8 |
| 4, 32 (four times), 36 (three times) | 112 |
| 20 (three times), 24 (four times), 52 | 112 |
| 24 (eight times) | 7 |
| 24 (seven times), 56 | 8 |
| 24 (four times), 28 (four times) | 112 |
| 28 (eight times) | 32 |
| 28 (four times), 32 (four times) | 112 |
| 32 (eight times) | 7 |
| 56 (eight times) | 1 |

Every singular H is **exactly** `32(I - e_j e_j^T)`, with each j appearing once.
Hence its real kernel is precisely the j-th coordinate axis. All other H are
positive definite, with minimum eigenvalue at least 4. Thus

- for all 503 nonsingular characters and every real a,
  `sum_(i in I(w)) (X_i a)^2 >= 4 sum_j a_j^2`;
- for each of the eight exceptional characters, the left side is exactly
  `32 sum_(k != j) a_k^2`.

`RESULTS.json` supplies a nonzero integer vector and literal 112-bit support mask
attaining the first inequality at equality; 4 cannot be raised uniformly.
Masks index the independently generated, lexicographically sorted twice-roots.
The receipt binds **every** mask, Gram entry and spectrum through a deterministic
SHA-256 transcript; it also lists all eight exceptional masks explicitly.
The hash is a reproducibility receipt, not a substitute for checking identities.

## Why this is an independent certificate

PR845's two existing implementations use stored nine-bit labels/duals and
nonzero minors (one uses Bareiss elimination). This implementation:

1. Generates the 120 root lines from their two elementary E8 coordinate families
   and deletes the frame, without importing a geometry module.
2. Reconstructs X and B directly from integer dot products. It binds roots/frame/X
   to the pinned predecessor snapshot up to root ordering, **never reading its
   labels, duals, reader bases, selected minors or RESULTS.json**.
3. Checks binary rank(B)=9 and enumerates its 512-element row space exactly,
   excluding only zero. This avoids choosing the predecessor's ambient labels.
4. Checks each Gram spectrum with integer matrix products and traces, not a
   determinant, floating eigensolver, tolerance, or rational elimination.

To relate the representation to the source lemma, in its notation
`B = L S L^T`, where L has column rank nine and S is nondegenerate. Thus the
row space of B equals the image of all nine-dimensional linear functionals on
the dual labels. Its 511 nonzero elements are exactly the source's 511 support
characters, regardless of the chosen label basis. The current check reconstructs
rank(B)=9 directly; the semantic interpretation of the source labels is the
stated predecessor convention, not a newly audited physical interface.

For a candidate list of eight eigenvalues, let D be its distinct values. The
checker verifies the exact matrix identity

`product_(d in D) (H - d I) = 0`

and the trace identities `tr(H^k) = sum_lambda lambda^k` for
`k=0,...,|D|-1`. Symmetry implies H is diagonalizable over the reals; the
annihilator confines its eigenvalues to D. These traces determine their
multiplicities uniquely because the Vandermonde matrix on distinct D is
invertible. This proves the claimed spectrum. No approximate spectral inference
is made. Four moments nominate a unique census row, but nomination alone is
never accepted: the matrix polynomial and multiplicity identities must pass.

The previous support conclusion follows: if the binary span of the dual labels
on `supp(Xa)` is proper, a nonzero character annihilates it, and `A_w a=0`.
The spectrum census forces a=0 or a onto one coordinate axis. Consequently
any a with at least two nonzero coordinates has full nine-dimensional support
span. This is a written consequence of finite exact certificates, **not a
proof-assistant formalization of PR845's full quantified theorem**.

## Controls and limits

Seven rejection controls exercise missing/duplicated/zero support characters,
omission of the affine 1 in B, alteration of a Gram entry, a false nullity with
the same annihilating polynomial, and a false rank-seven spectrum matching the
first two moments. The last is substantive: `diag(56,24,...,24)` and
`diag(0,32,...,32)` have equal traces 224 and equal traces of squares 7168,
but ranks eight and seven. Polynomial/multiplicity checks prevent that shortcut.
A scalar positive-spectrum case is accepted as a positive control.

Domain and stopping rule: exhaust all 511 nonzero words of this exact P112
pairing space, stop after complete coverage; all were completed. Assignment seed
80 selects this obligation, not a random sample or search restart. This does not
reopen the already proved single-lift negative result. It does not audit PR845's
3,272 sign systems or rank-63 conflict argument, nor cover other punctures,
changed readers, several extra totals, masked identities or a physical COPY
program. No supplier cost, recursive saving or kappa is inferred from the energy
bound. Inherited compiler, common-label/mutable-source, hosting, precision/tape
and analytic assumptions remain untouched. Full repository/native replay and
formal proof-assistant verification are outside this isolated check.

## Credit and disclosure

Prepared for **@adamgall**, with substantial **OpenAI Codex** assistance in task
selection, mathematics, implementation, verification and writing. Both this
checker and its predecessor have disclosed AI assistance; independent means
code/method independence, not independent human peer review.

- Mihir Srivastava (@mihir-s-05), PR845: support reduction, original rank census,
  real single-lift obstruction and existing independent minor checks.
- DreamingOfClouds, PR717: P112 model and geometry; PR446: inherited copy-tree
  interpretation. Their original Claude assistance disclosure is retained in
  the pinned [PR717 notice](../p112-single-lift/reference/PR717-NOTICE.md).
- Joel Pulikkan / GamingPuzzled, PR620: coordinate decoder copy cost 64.
- Jacob Sussman, Zhihao Chen, Dylan Crow, icekylinx, eumemic, Jeremy Kothe,
  Chafik Boukhalfa and the wider E8/compiler lineage retain the attribution in
  [PR845's notice](../p112-single-lift/NOTICE.md).

New work is Apache-2.0 under the repository license. No predecessor files are
modified. `CLAIM.md` records selection/overlap; `VALIDATION.json` records exercised
checks and their explicit scope.
