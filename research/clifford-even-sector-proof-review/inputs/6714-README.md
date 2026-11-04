# The sharp three-qubit Clifford tensor threshold is 10

The **full three-qubit Gaussian-dyadic Clifford alphabet** has 92,897,280
projective classes. Their tensor powers are linearly independent exactly at
widths **f >= 10**. At width nine the exact nullity is **3,136**. Thus

    T(3) = 10,

not the extrapolated value `4n+1=13` suggested by the sharp one- and two-qubit
cases. This resolves the three-qubit question in
[PR5675](https://github.com/CrocSwap/integer-mult-bounds/pull/5675) and
[PR5967](https://github.com/CrocSwap/integer-mult-bounds/pull/5967), whose
general bounds left `7 <= T(3) <= 16`.

This is a mathematical native-interface result. It changes no paid supplier
profile or multiplication exponent. Selected PR6030 remains at
**kappa=0.003125804**, with all five inherited framework assumptions.

## The new argument

[PROOF.md](PROOF.md) reduces the odd central sector to representations of
`Sp(6,2)`. At width nine the multiplicity-space character is the permutation
character on ordered four-tuples of binary six-vectors. Its exact decomposition
has one missing irreducible, of dimension seven. The corresponding Clifford
block has dimension 56 and accounts for the nullity `56^2`.

The width-ten step needs **no even-sector character table**. A missing
irreducible would force its tensor product with the conjugate natural
representation to contain only that missing block. Its transvection trace
would then exceed what its Pauli character spaces permit: each quadratic-form
orbit has only sixteen fixed spaces. This contradiction proves completeness.
Schur products propagate it to all larger widths and exclude independence
at every smaller width.

The same argument gives explicit, nonoptimal bounds for the normalized Gram:

    (945/262144) I <= H_f <= (762615/32768) I,  f >= 10.

The resulting condition-number bound is 6,456. Four tests at widths
**10,11,12,13** decide a fixed complete Clifford residual at all positive
widths, retaining exact scalar phases. One test has normalized squared
residual at least `945/262144` times the combined coefficient squared norm.
The constants and test window are sufficient; neither is claimed optimal.

## Evidence and external input

[table.json](table.json) contains the numerical 67-by-67 table published by
Chin-Yen Lee, Wei-Hsuan Yu, Yung-Ning Peng and Ching-Jui Lai in
[On character table of Clifford groups, arXiv:2309.14850v2](https://arxiv.org/html/2309.14850v2#S6.SS3),
Section 6.3. Section 5.2 identifies the Pauli class and adjoint character.
This table is for the **projective** group; the proof handles the required
scalar-fourth-root extension explicitly.

Its identification with the named group is a cited mathematical input,
not independently reconstructed here. Orthogonality and integrality check
the transcription and calculation; they do not prove that an arbitrary
orthogonal array is a group character table. All 4,489 entries independently
extracted from HTML and original TeX agree. [EXTERNAL.json](EXTERNAL.json)
records URLs and hashes. No article prose is redistributed. Optional
[extract_table.py](extract_table.py) and [extract_tex.py](extract_tex.py)
repeat the separate extractions from local HTML and TeX.

The primary verifier authenticates source pins and table bytes, checks the
complete quotient and width-nine decomposition, all 63 transvection fixed-form
counts, stability constants, and eight rejecting controls. Odd widths
1,3,5,7,11,13 provide additional phase and rank controls.
[independent_check.py](independent_check.py) supplies separate calculations;
[REVIEW.md](REVIEW.md) records adversarial mathematical review. These checks
share the cited published table. No floating-point acceptance, dense tensor
matrix, numerical eigensolver, proof-assistant result or human review is claimed.

## Reproduce

Standard-library Python 3.12; no network is needed:

```sh
python -B scripts/research_package.py --package research/clifford-three-qubit-threshold
```

The registered replay runs both checkers normally and with `-O`. Direct
scientific commands, also suitable for a Git-free source export, are:

```sh
python -I -B research/clifford-three-qubit-threshold/verify.py
python -I -B research/clifford-three-qubit-threshold/independent_check.py
```

[VALIDATION.md](VALIDATION.md) records actual execution and limits. Written
arguments supply the universal statements; fixtures do not prove them by
extrapolation.

## Scope and provenance

Scientific base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The fork was current before the isolated branch was created. The selected
certificate, construction review and binding baseline were followed;
historical PR5599 priority prose was not treated as the accepted frontier.
[TASK.json](TASK.json) records the formal-interface card's explicit change
to this written algebraic side result. [SOURCES.json](SOURCES.json) pins
predecessors, which remain unchanged.

Pointwise independence permits arbitrary complex coefficients at a fixed
width. The four-test implication requires the same exterior coefficients
and program at every width. Non-Clifford operators, nonunitary maps,
cross-column operators, rounded execution, physical delivery, precision,
stock, tapes and complete supplier/outer costs remain outside this theorem.
No selected cold replay or discharge of a framework assumption is claimed.

## Open next questions

1. **Determine T(4).** The three-qubit answer prevents extrapolation from
   n=1,2. First decompose the relevant odd-sector character for `Sp(8,2)`
   and test a quadratic-orbit bound on the missing blocks. An authenticated
   character table and tractable missing-block structure are needed.
2. **Find the sharp width-ten spectral endpoints.** First decompose the
   even-sector multiplicity spaces using the two quadratic-form stabilizers.
   Additional representation data is needed; a dense Gram is unnecessary.
3. **Bind a concrete native caller to the earlier window.** First check
   its entire alphabet, phases and dirty returns. This algebraic result
   supplies no paid saving without that caller and its complete invoice.

## Credit

Prepared for **alephnan** with substantial OpenAI Codex assistance in
derivation, implementation, independent calculation and adversarial review.
The separate reviews are AI reviews.

Credit Ali Romman (PR5376/PR5526: trace, phase and pointwise frameworks),
MatShep (PR5549/PR5594/PR5675: sharp small-qubit cases), Nick Petalas
(PR5967: general lower bound and open question), and the retained native
lineage. Lee, Yu, Peng and Lai supplied the published table and adjoint
identification. Pauli representation theory, character orthogonality,
tensor reciprocity, quadratic forms and Schur products are classical.

The new contribution is the sharp three-qubit threshold, the transvection
completion argument and its quantitative consequences. No general
representation-theory invention or global literature priority is claimed.
New work is Apache-2.0; retained sources keep their attribution and licenses.
