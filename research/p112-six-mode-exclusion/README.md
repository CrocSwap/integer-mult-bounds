# P112: a cost-297 floor for one aligned six-mode factor family

For the explicit P112 cover and aligned six-mode spaces below, every finite
rational rank-one decomposition of the fixed endpoint `K = R R^T` has whole-group
cost **at least 297**. Thus this family cannot reach the necessary integer
decoder target `C <= 296`. The bound is not claimed sharp: the known complete
construction still costs 334. This is a scoped obstruction, not a cheaper
decoder, a bound for all P112 decoders, a native supplier or an improved kappa.

## Exact scope and contribution

The physical labels are authenticated from the selected replay archive.
[CANDIDATE.json](CANDIDATE.json) is the unchanged cover from
[PR2757](https://github.com/CrocSwap/integer-mult-bounds/pull/2757), pinned at
`18da668a4f248f5c0cf3fc94355068ead4db3476`: 37 orthonormal triads and one residual
line, with 18 matched pairs. The endpoint has rank 57. Both factor sides lie in
the same 63-dimensional space formed by its 57 canonical columns and six
disjoint exterior modes. The mode assignment on the 18 pairs is

```text
1,2,0,2,3,0,0,4,5,5,4,2,4,3,1,5,3,1
```

The distinguished exterior coordinate is the first payload coordinate; the
residual uses the second. These axes, the mode partition and the endpoint are
fixed. Coefficients may be arbitrary rationals and the number of terms may be
any finite number. Each term is charged the binary pairing rank of its entire
source and reader group spans, not its scalar coefficient rank.

The new step is a complete finite reduction of a hypothetical cost-at-most-296
factorization. After proportional coalescence, a quotient deficit inequality
leaves coordinate subspaces plus at most one rational line. A dual diagonal
change of coordinates removes that line's amplitudes without changing any
physical group support. This yields **4,928 families and 5,440 term-count cases**.
Exact subspace-cover certificates close every case. Coalescence may lower the
opposite factor rank; all rank counts refer to the resulting representation.

See [PROOF.md](PROOF.md) for the universal algebraic argument and its finite
premises. [CERTIFICATE.json](CERTIFICATE.json) records actual cover witnesses,
not a collection of solver timeout or infeasibility claims. Both replays rebuild
the support geometry, validate all covered edges and recompute the bounds.
No discovery search is needed to check the result.

## Reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -O -B research/p112-six-mode-exclusion/verify.py
python3 -I -O -B research/p112-six-mode-exclusion/independent.py
python3 scripts/research_package.py --package research/p112-six-mode-exclusion --check-only
python3 scripts/research_package.py --package research/p112-six-mode-exclusion
```

The package registers both read-only checks in [VERIFY.json](VERIFY.json).
[SOURCES.json](SOURCES.json) binds the candidate, certificate, exact physical
archive/member and base provenance. The two mathematical replays also work in
a Git-free source export containing this directory and the declared archive.
They do not import each other or any scratch research code.

The finite checks support the written scoped proof; they are independent AI
implementation checks, not human peer review or a proof-assistant verification
of the complete multiplication theorem. Selected-supplier cold replay and Lean
suites are outside this isolated package.

## Why 296, and limitations

Under the proposed 37-triad/one-line coverage accounting, positive saving first
requires `C < 2672/9`, hence integer `C <= 296`. This is only a necessary,
optimistic gate. Beating the selected exponent requires a stronger full cost
calculation. Preparation, chart conversion, routing, hosting, storage,
restoration, precision, recursive composition and a compatible bit supplier
remain outside this theorem. Unknown costs are not zero.

This result does not cover changed fitting matrices, other mode partitions,
other relative source/reader orientations, different residual coupling, or
factor directions outside the specified spaces. It does not establish that
cost 297 is attainable. The predecessor cost-334 construction is a positive
control, not a new result.

## Sources, overlap and credit

The package starts from canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6. The selected record
is unchanged. [TASK.json](TASK.json) records the user-directed scope and latest
submission overlap check, including its incomplete Discussion coverage.

This extends flyingviper's whole-group rational-decoder investigation in PR2757.
The source geometry and pricing retain the contributions of Cinna Davis
(PR2041), Adam Gall (PR1889), Sagar Thakrar (PR2532), Jeremy Diviney (PR2203),
ctoth and collaborators, Philippe Van Velzen, and the selected PR1094 lineage
including Rohan Arun and Jeremy Kothe. Exact predecessor heads and input hashes
are retained in SOURCES.json and the unchanged candidate.

PR3026 concerns a different five-triad, per-term-tariff-at-most-3 theorem and is
not used here. PR2985 and PR3029 concern root-line residue/deficiency budgets;
PR2832 concerns different singleton-decoder contracts. Their claims are not
imported as premises of this proof. No worldwide novelty claim is made.

Prepared by flyingviper with substantial OpenAI Codex assistance in the original
proof, certificate work, packaging, and separate-agent checks. New material is
Apache-2.0; inherited source attribution and licenses are retained.

## Open next questions

- Can a changed fitting matrix or different relative source/reader geometry
  permit a complete invoice below 297? First state the changed endpoint/spaces
  and screen their physical support costs. The present theorem provides no
  construction or obstruction outside its stated family.
- What is the sharp minimum inside this family? The established interval is
  297 through 334; first supply a cheaper exact decomposition or a stronger
  lower-bound witness. Attainment at 297 is unknown and is not needed for this
  exclusion.

These are handoff questions, not active searches. Further research is paused.
