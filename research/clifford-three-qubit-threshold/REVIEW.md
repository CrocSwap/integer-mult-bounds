# Independent agent review of the three-qubit threshold

**Disposition: no blocking mathematical defect found in the scoped theorem
`T(3)=10` or its stated sufficient spectral bounds.** This review was performed
by a separate OpenAI Codex agent after the derivation and primary checker had
been written. It is an independent derivation/checking pass within one AI-assisted
session, not independent human acceptance or proof-kernel verification.

The review treats the published character table of Lee, Yu, Peng and Lai,
[arXiv:2309.14850v2](https://arxiv.org/html/2309.14850v2), as a cited mathematical
input. It does not reconstruct that table from a presentation of the group.
Orthogonality and integrality checks alone could not establish the identity
of an arbitrary table with a named group.

## Exact reviewed state

The scientific worktree was based on canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. On 2026-11-04 the reviewed files
had these SHA256 hashes:

| File | SHA256 |
|---|---|
| `PROOF.md` | `d29091eb12b4ccd3f5acb389634a858af3beb0dc78865613bb7bd68c9440c6d0` |
| `table.json` | `388d617a76e345774a8768f32a6a9bc6e94b87f9c8a5cf6712a95a5a3a945fcd` |
| `EXTERNAL.json` | `eb64deffd68787fe12df7b745d98f3139f77c5ab7ecd41a86bd832db0c7ebe0a` |
| `verify.py` | `3e77a06c572d85fe4169eafc827752f41760b40953d4166073a5c6d5842e6e2d` |
| `extract_tex.py` | `1a0b50f638b470df06c3b1f83afddcd5d75f3116de084a2aaaf5263d1ec296ec` |

The table and external-manifest hashes above use the final LF publication
bytes. Normalizing their Windows CRLF line endings changed no data; the
exact checks were rerun on the normalized files.

Subsequent changes to these files require checking their mathematical relevance;
this receipt is not a blanket approval of later revisions.

## Mathematical checks

1. **Central extension and source identification.** The Gaussian-dyadic scalar
   kernel is exactly `mu_4`. Its projective quotient is the full usual Clifford
   quotient, since Gaussian-dyadic phase choices realize its generators. The
   primary paper explicitly identifies its second class, of size 63, with all
   nonidentity projective Paulis, and gives the conjugation character
   `M_8 = chi_1 + chi_10` in Section 5.2. These facts justify the normal-subgroup
   and adjoint inputs used by the extraction. Equality of a character value to
   its degree identifies trivial action on the Pauli subgroup, so the quotient
   character extraction is legitimate. Irreducible characters then separate
   quotient conjugacy classes.

2. **Odd-sector reduction.** Restriction to the Pauli group has a unique
   irreducible of central character `i`, and the actual natural representation
   extends it. Thus all irreducibles in this sector are `V tensor sigma`, with
   `sigma` an honest `Sp(6,2)` irreducible. No splitting of the group extension is
   required. The nonzero-trace lift argument gives the width-nine multiplicity
   character `2^(4d)` with the native phase retained.

3. **A different calculation of width nine.** I recomputed the multiplicities
   directly on the 67 projective classes, without using the primary checker's
   quotient construction or fixed-space dimensions. With `A=1+chi_10`, an
   inflated irreducible `sigma` has multiplicity

       (1/92897280) sum_K |K| A(K)^5 sigma(K).

   This follows from `chi_V^9 conjugate(chi_V) = |chi_V|^10 = A^5` for the
   Gaussian-dyadic trace alphabet. Every one of the thirty multiplicities agrees
   with the proof. The only zero has degree seven; the missing full-group
   irreducible has dimension 56. The rank is therefore 92,894,144. The same
   source row has value `-5` on the nonzero-trace transvection lift class.

4. **Even-sector trace bound.** For central character `-1`, the Pauli
   commutator acts trivially, so restriction decomposes into one-dimensional
   characters indexed by quadratic refinements. Clifford signs disappear
   because `lambda(-I)=1`; the action is the ordinary symplectic pullback on
   quadratic forms. I separately enumerated their complete truth tables and
   applied all 63 transvections to all 64 forms, evaluating all 64 vector labels.
   The 258,048 evaluations yield precisely two orbits of sizes 28 and 36, with
   sixteen fixed forms in each orbit for every transvection. This corroborates
   the written normal-form argument, rather than replacing it. Irreducibility
   forces a single orbit with common multiplicity, so the trace bound `16a`
   applies to every relevant irreducible and every lift.

5. **Width ten and quantitative conclusion.** Tensor reciprocity correctly
   uses `conjugate(V) tensor mu`. If a constituent were absent at ten, all of
   that representation would lie in the sole missing width-nine block.
   Dimensions and the transvection character would then require a trace of
   absolute value `5Na/7`, which exceeds `16a` for both `N=28,36`. The quantitative
   version correctly obtains remaining degree at least `dim(mu)/12`; the
   nonmissing width-nine multiplicity ratios lie in `[1/2,269]`. The regular
   convolution normalization gives exactly `945/262144` and `762615/32768`.
   There is no missing factor of four from scalar lifts.

6. **All widths and fixed residuals.** The unit-diagonal Schur-product step
   propagates the two spectral bounds to every larger width. It also excludes
   independence at any earlier width once width nine is singular. The central
   idempotent witness has a nonzero identity coefficient and the scalar phases
   cancel at width nine as stated. The four-width residual test and its norm
   bound follow from four-point Fourier inversion and Parseval with coefficients
   fixed across widths. The proof correctly distinguishes this condition from
   pointwise independence.

## Independent transcription check and executions

I checked all **4,489 numerical entries** against the original arXiv TeX source,
using a parser separate from the primary HTML parser. The TeX source SHA256 is
`caa1e0449ef7575fc4c516238e939effb309038c45ae6f3d41f64206b9619de3`.
The separate parser is retained as `extract_tex.py`; the article itself is not
redistributed by this package.

The following commands passed with CPython 3.12.2 on Windows, in normal and
optimized modes:

```text
python -I -B research/clifford-three-qubit-threshold/verify.py
python -I -O -B research/clifford-three-qubit-threshold/verify.py
python -I -B research/clifford-three-qubit-threshold/extract_tex.py /path/to/paper.tex
python -I -O -B research/clifford-three-qubit-threshold/extract_tex.py /path/to/paper.tex
```

The full-projective direct sum and literal quadratic-form checks above were
separate reviewer computations, importing no primary verifier functions.
All methods share the published character table. Their agreement is not an
independent reconstruction of that external input.

## Findings and limits

One minor source-reference issue was corrected before these hashes were
recorded: the normal-subgroup theorem is **Theorem 5.5**, not Theorem 5.2.
The relevant preceding prose is in Section 5.2. This did not affect the
mathematics or numerical data.

No full three-qubit Clifford group enumeration, tensor matrix construction,
proof-assistant run, physical caller audit, selected cold replay, new supplier,
or multiplication-exponent claim was checked. The sharp threshold is established
by the written representation-theoretic argument and the cited exact table;
the executable controls support the finite arithmetic. The nonoptimal spectral
constants and the earlier sufficient fixed-residual window are correctly
labelled. A global literature-priority claim is outside this review.
