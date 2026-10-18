# Binary affine addresses: exact paid-call floor with arbitrary dirty registers

**Scoped no-gain theorem; no new kappa.** In the explicit nonabelian address
model below, any number of restored dirty registers and free scalar register
mixing leave the optimal paid-call bill equal to the direct bill:

\[
 \min\text{ paid calls}=\sum_{j=1}^{w}
 \operatorname{rank}_{\mathbb F_2}[A_j-I\mid b_j].
\]

The targets are affine maps `g_j(x)=A_j x+b_j`, with arbitrary invertible
binary `A_j`. The result holds for every address dimension, register count
and word length. [PROOF.md](PROOF.md) gives the full written proof and
constructive upper bound. The finite certificate independently corroborates
all **323,930 affine maps in dimensions 1–4**.

This deliberately replaces the abelian rational address group in the card's
starting model. It neither reduces rational frame entries modulo two nor
claims physical admission of a different supplier.

## Exact alphabet and boundary

Work over the formal group algebra `F2[AGL_d(F2)]`, not just one matrix or
finite-address representation. A unit paid call is
`I + ([g]-1)N`, where `N` is a binary rank-one idempotent and the homogeneous
displacement `rank([A-I|b])` of `g=(A,b)` is one. This includes nonzero
translations as **paid units**. Scalar `GL_r(F2)` basis changes are free in
this optimistic relaxation; address transformations are not free.

The complete endpoint is `diag([g_1],...,[g_w],1,...,1)` for arbitrary inputs.
Every extra register must be restored, including all dirty-state effects on
the target registers. No COPY, erasure or clean allocation is provided by the
alphabet. Every paid call, including restoration, is counted. The attaining
word uses no extra register or scalar basis change. Real implementations
would additionally need to price scalar work, storage and physical interfaces.

The lower bound normalizes scalar operations using augmentation, then applies
a homogeneous matrix representation and rank subadditivity. The upper bound
constructs exactly `rank([A-I|b])` allowed factors for each affine target and
proves their product in the formal group algebra. Noncommutativity is retained.

For a concrete three-target example, take the binary matrix with rows
`(4,5,2)` in bit encoding and translations `b=0,1,3`. These three affine
maps pairwise fail to commute and each has displacement rank three. They
require **nine paid calls even with arbitrarily many restored dirty registers**.
The checker builds a nine-call formal word with a fourth dirty register
returned identically, and rejects an omitted-call mutation. This is a theorem
about the declared binary-affine model, not the rational PR468 target family.

## Complete finite checks

| Address dimension | Affine maps | Paid address generators | Minimum-cost histogram, starting at zero |
| --- | ---: | ---: | --- |
| 1 | 2 | 1 | 1, 1 |
| 2 | 24 | 9 | 1, 9, 14 |
| 3 | 1,344 | 49 | 1, 49, 518, 776 |
| 4 | 322,560 | 225 | 1, 225, 11,830, 124,200, 186,304 |

The Python constructor supplies and replays an attaining factorization for
every map. Separate C++ code performs complete Cayley BFS without rank pruning
or the factorization algorithm: **72,642,074 directed transitions** in total.
Every distance and reachable state is compared, not just the histogram.
These are address-group censuses; they do not enumerate all multi-register
words. The unrestricted-register conclusion comes from the written proof.

Additional checks cover 44,020 elementary represented-call ranks; 96 exact
formal words and 576 chronological product prefixes; 56 formal identities,
including all `GL(2,2)` scalar basis conjugations and the attaining words;
small point-permutation BFS; and 32 factorization fixtures in dimensions
5, 8, 16 and 32. [EXPECTED.json](EXPECTED.json) records deterministic counts
and digests. Larger fixtures are tests, not an exhaustive census.

Seven boundary controls distinguish translations from their linear parts,
noncommuting order, clean-only target correctness from dirty correctness,
rank-two underpricing on either tensor factor, nonidentity free scalar
augmentation, and the kernel of the natural representation. In particular,
the nonzero sum of all 24 formal `AGL_2(F2)` elements maps to zero in the
homogeneous representation. Matrix-image equality alone is not used to accept
a universal formal identity.

## Reproduce

Full certificate, Python 3.12+ and a C++17 compiler (`g++` by default,
override with a single executable path in `CXX`):

```sh
python3 -I -B research/binary-affine-register-bound/verify.py --full --work /tmp/binary-affine-full
```

Use a new output directory; an existing one is refused. The command builds
the separate BFS, compares all four complete distance arrays and all attaining
factorizations, then retains the arrays and `RECEIPT.json`. Expected final lines:

```text
PASS_BINARY_AFFINE_FULL affine_maps=323930 exact_distances_and_attaining_words=true
receipt_sha256=e95e3af2f484cb03f600c8d669354465f4812a1316e842e248fc81a48d5a30d0
```

The full local check took about seven seconds on the recorded machine;
runtime is environment dependent. The dedicated
[workflow](../../.github/workflows/binary-affine-register-bound.yml) runs it.
The generic Python-only hook explicitly runs **quick coverage only**, omitting
the independent full dimension-four census:

```sh
python3 scripts/research_package.py --package research/binary-affine-register-bound --check-only
python3.12 scripts/research_package.py --package research/binary-affine-register-bound
python3 -I -O -B research/binary-affine-register-bound/verify.py --quick
python3 -I -B research/binary-affine-register-bound/test_package.py
```

Its five package tests cover typed certificate corruption, native distance
corruption, source/JSON corruption, read-only minimal export under isolated
optimized Python, and output preservation. See [VALIDATION.md](VALIDATION.md)
for observed commands and coverage limits. The proof is not Lean-checked.

## Task, sources and overlap

Submitted as [PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333).

Base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; OS nonce
`5d737eb3d3ab653b8a6a9411d0753d36`; bit-mechanisms card
`bit-new-register-model`, scope key `7084092dd726e7ba1f2f`, priority revision 2.
[TASK.json](TASK.json) records the precise refinement. Coordination:
[Discussion1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317).

[SOURCES.json](SOURCES.json) binds two unchanged context READMEs; neither
predecessor implementation is imported. Catalogue/selected-record provenance
is historical at the task base. [OVERLAP.json](OVERLAP.json) records the live
search, exact nearby heads and its limits. PR288's nonabelian solvable-quotient
model, PR468/720's rational abelian three-register theorems and PR836's complex
unitary-rank obstruction have different hypotheses. PR1194/1306 already
address the draw's other helper-contract suggestion; that work is not repeated.

## Open next questions

1. **Restrict the address alphabet to coordinate CNOTs and coordinate
   translations.** Direct single-role lengths may then exceed the rank floor.
   First choose a dimension-three target with that gap and seek a formal
   two-role word below twice its direct length. This requires a different
   complete operation bill and a full group-algebra endpoint certificate;
   natural matrix equality alone is insufficient.
2. **Identify a physically justified alphabet that escapes this rank budget.**
   First price one proposed primitive or free operation and compare its
   representation rank with its charge and target boundary. A claimed saving
   must change a material hypothesis. Physical/compiler/hosting admission is
   missing for this abstract model, and its binary argument does not transfer
   to rational frame data by modular reduction.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance in proof,
implementation, validation and writing; no subagents or independent human
review. New work is Apache-2.0; predecessor files and notices are unchanged.

Credit eumemic (PR288 and the bit-supplier lineage), Ali Romman (PR468), David
Govea (PR720), and the retained rank-method predecessors. The other card's
baseline is Sagar Thakrar's PR1062 composition of @theon199's PR967 stars,
Aaron Wang's PR1015 and Ross Richardson's PR923 blocks, with the retained
Gareth Davidson / DreamingOfClouds / eumemic lineage. The helper-contract
overlap was resolved by @woklerx's PR1194 and @commdata2338's PR1306.

Classical reflection-length and rank methods are credited in [PROOF.md](PROOF.md)
to Huang/Lewis/Reiner and delMas/Lewis, with primary references. No novel
reflection-length principle, literature priority, selected frontier change,
physical supplier, multiplication-runtime improvement or new kappa is claimed.
