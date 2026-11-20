## What this PR supplies

This PR combines two directly dependent, individually reviewed results into a single interface contribution: **fixed Gaussian-rational scalars in recursive all-column C words**, followed by a **phase-preserving translation of the selected complex compiler** into that expanded grammar. This closes a concrete mismatch between #7828's odd rational scalars and #7834's dyadic-only receiver without increasing the paid C-call count. It is not a complete physical runtime or a new multiplication bound.

### Exact rational all-column grammar and common grid

Extend the C-word scalar alphabet by `SCALE(a,b,q): z -> ((a+i b)/q)z`, with fixed integers and positive q. The exact matrix-dictionary/Vandermonde test distinguishes scalar multiplication from columnwise phase `i^f`; it checks every productive output and requires all private outputs to be zero. For a word with base rank N and J instructions, let D be the LCM of the odd denominator parts, d=floor(log_N h). One root scale `D^(Jd)` pays all intermediate odd debt, since completed children return dyadic maps and only unfinished ancestor contexts accumulate division debt. A separate coefficient-dependent binary guard pays numerator staging, magnitude and exact final unscaling.

Under the source's named disjoint-XOR, placement, scalar-service and parking contracts, local scalar events cost O_word(V), root scaling costs O_word(V log(h+2)) and the working component width remains O_word(p) in the source geometry. The retained W^d genuine-row stock, <2 padding, zero-output checks, physical history and fallback are not hidden. The proof corrects the unary denominator budget to D≤3^(L/3), avoiding an earlier overstatement.

### Exact selected complex compiler admission

The translation preserves **N, W and the full paid count P** from the selected #7828 complex construction. It lowers each monomial to x/s/cz/cx/unit with signed phases and correct chronological order, retains both source L/R factors and all spectators, handles absolute phase by `i^(a*c*f)`, and applies exterior rational scalars once rather than tensoring them. The selected global LAMBDA is one complete two-term exterior scalar combination. Private SWAP/CLEAR operations are explicitly lowered and charged.

The selected conditional supplier funding check remains `P^500 < W^500 N^499`, with exact source saving `181502908503/50000000000000 > 1/500`. This *supplier price* is not a new complete multiplication κ. The compiled test fixture has 1,654 instructions, 18 paid calls and 28 private fields; it is deliberately unfunded.

### Reproduce

```sh
python3 -B scripts/research_package.py --package research/rational-all-column-c-word
python3 -B scripts/research_package.py --package research/complex-compiler-c-word-admission
```

Checks include exact Fraction-array/tensor oracles, deep odd divisions, multiple multiplicities and spectators; the compiler package checks 700 monomial packets, 712,754 exact address/phase comparisons, all 3,095 compact caller events, independent receiver replay and mutation controls for phases, aliases, dirty private exits and wrong exterior-scalar semantics. Both packages retain complete original proofs, source hashes, reviews and registered receipts.

### Boundaries and credit

No astronomical full word is materialized; source native operators, actual owner/grant, physical coded-field ABI, complete row routing, cost tariffs, supplier funding theorem and analytic recovery remain explicitly inherited. Neither all five selected assumptions nor κ is changed. Credit Ali Romman (#7828, #7834), selected #7000 numerical/compiler predecessors and their retained notices. Prepared for @CubeJerry with substantial OpenAI assistance and separate model-assisted checks; not human peer review or proof-kernel acceptance.