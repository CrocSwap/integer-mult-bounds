# Target feedback saves no XORs for three-helper / four-target dirty shears

**Finite exact result; no new supplier or kappa.** For all 4,096 binary
4-by-3 matrices K, allowing targets to feed helpers does not reduce the minimum
unit XOR cost of `(h,y) -> (h,y+Kh)`. There are three helpers and four targets;
every register starts with arbitrary independent data and there are no extra
registers. The maximum minimum is nine gates.

This answers the next finite case requested by @commdata2338 in
[PR1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306) and
[Discussion1290](https://github.com/CrocSwap/integer-mult-bounds/discussions/1290).
That predecessor established the equality for up to three helpers and three
targets and supplied the common-zero-frame substitution lemma. Its pinned head
is `0d4c0069f1f4592833304a9ea6e61e676c566113`; its theorem and lemma are credited,
not claimed here. This package adds the seven-register census, a simultaneous
shear-coset calculation, and a separate truth-table verification.

## Model and exact result

Registers are `h0,h1,h2,y0,y1,y2,y3`, numbered 0 through 6. A gate `[d,s]`
means `register[d] ^= register[s]`, with distinct indices. Each gate costs one,
including preparation and restoration. The restricted alphabet has 30 gates:
it excludes only helper destinations with target sources. Helper mixing and
target mixing remain allowed. The unrestricted alphabet has all 42 gates.

The complete required matrix is

```text
T_K = [ I_3   0   ]
      [  K   I_4 ].
```

The helpers and the initial target data must all be restored as shown. Testing
only zero workspace would be insufficient. The model has no allocation,
COPY/ERASE, frame changes, paid recursive calls, free basis changes or free
permutations. A length-L word costs L scalar ADDs and zero of these other events.
This is a local algebraic bill, not a hosted-supplier or precision certificate.

Both alphabets have this exact distribution:

| Minimum gates | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Labeled K | 1 | 12 | 66 | 220 | 495 | 810 | 1,017 | 922 | 529 | 24 |

The 24 nine-gate maps are precisely the permutations of these four rows:

```text
[1,1,1], [0,1,1], [1,0,1], [1,1,0].
```

No word of at most eight gates in either alphabet realizes one of them. The
nine direct helper-to-target XORs attain the bound. This includes unrestricted
words with temporary target feedback. The other 4,072 maps have explicit
restricted witnesses of length at most eight. [CERTIFICATE.json](CERTIFICATE.json)
stores 87 helper/target permutation representatives, their costs, orbit sizes
and restricted witnesses, as well as the complete search statistics.

## Why the finite calculation certifies global minima

Every XOR generator is its own inverse. Let B4 be the complete radius-four
ball in either alphabet, with breadth-first distances. Every word of length
at most eight splits into two words of length at most four. Its endpoint is
T_K exactly when there are A,B in B4 with `B = A T_K`; the corresponding word
runs B and then the reverse of A. Minimizing `distance(A)+distance(B)` over
these pairs therefore gives every minimum at most eight. An absent pair
proves a lower bound of nine. It becomes an exact minimum only when an explicit
nine-gate word is checked; the verifier refuses to fill a larger search gap.

The primary checker finds all pairs simultaneously. Write an invertible matrix
M by its three helper columns X and four target columns Y. Right multiplication
by T_K leaves Y unchanged and replaces X by `X+YK`. Reduce each column of X
modulo the span of Y, using a deterministic echelon basis derived only from Y.
Keep the reduction coefficients Q, so `M T_Q` is the canonical representative.
The four columns of Y are independent, making Q unique.

Two matrices have the same representative if and only if they differ by a
right shear. If their recorded coefficients are Q_A and Q_B, then
`A^-1 B = T_(Q_A+Q_B)`. Grouping B4 by these exact representatives and visiting
every distinct unordered pair thus loses no eligible pair. Pair reversal
preserves the shear because T_K is an involution; the identity is handled
separately. The primary computation prices all 4,096 labeled maps before
using any symmetry to shorten the certificate.

The radius-four sphere sizes are:

| Alphabet | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| Restricted | 1 | 30 | 534 | 7,113 | 75,645 |
| Unrestricted | 1 | 42 | 1,092 | 22,141 | 375,480 |

`independent.py` imports no primary or predecessor checker. It represents each
seven-register map by its literal outputs on all 128 bit inputs, builds the
unrestricted B4 by table composition, and directly tests `B=A T_K` for every
word shorter than each claimed minimum. It does not use the coset quotient.
For a claimed cost c <= 9, balanced splits require left distances only through
`floor((c-1)/2)` and right distances through four. Thus its shorter-word tests
are complete, including the eight-gate exclusion for the nine-gate class.

Separate helper and target permutations conjugate each alphabet into itself
and preserve cost. They transport endpoints and witnesses rather than execute
free gates. The second checker verifies that the 87 orbits partition all 4,096
matrices, and replays the transported restricted witnesses on all 128 inputs
for every labeled matrix. Restricted upper bounds and unrestricted lower bounds
agree. The shared mathematical principle is meet-in-the-middle; the code,
representation and pair enumeration differ. Both were written in one AI-assisted
session, not by independent human reviewers.

## Reproduce and failure controls

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/bit-zero-frame-feedback-3x4
```

This registered replay runs both checkers and the subprocess controls. The
checkers print `PASS_SHEAR_3X4_COSETS` and `PASS_SHEAR_3X4_TRUTH_TABLES`; the
runner ends with `PASS_REGISTERED_RESEARCH_PACKAGE` and `outcome=negative-result`.
To regenerate the certificate explicitly:

```sh
python3.12 -I -B research/bit-zero-frame-feedback-3x4/verify.py --write
```

Controls check a restored helper star and a complete feedback word, and reject
missing restoration, residual target dirt, wrong helper columns, forbidden
feedback, self-XOR, Boolean indices and an insufficient radius. The primary
checker validates all 672 shear products on the full 168-element GL(3,2).
The truth-table checker also traverses all 20,160 elements of GL(4,2), compares
all 16 two-by-two shear distances and rejects each overstated minimum.

The subprocess tests copy both checkers and the certificate to a fresh directory
and run under isolated, optimized Python. Both engines must reject four actual
certificate corruptions: a longer valid word falsely labeled optimal, a wrong
dirty-input column, a missing orbit and an understated sphere count. A further
test reproduces the predecessor's three-by-three distribution with the new
coset algorithm. No assertions are needed for the checkers' rejection paths.

The complete registered replay passed under CPython 3.12.13, including all
three test groups. The repository's 20 research-workflow tests also passed
under Python 3.12 with no skips. Source-pin and package
metadata checks passed; these checks are distinct from mathematical acceptance.

## Scope, sources and task selection

The base is main `55a02580ce1b283026e9d3b3510b218f8c93a4de`.
[TASK.json](TASK.json) records the selector nonce, changed scope, overlap checks
and stop rule. The original card was `bit-helper-contract`. PR1194 and PR1311
already address its H2/K question; this follows PR1306's adjacent D-local H1
cost question. It is a prerequisite/negative result, not an interface adoption.
[Discussion1544](https://github.com/CrocSwap/integer-mult-bounds/discussions/1544)
records the claim and result. No predecessor implementation or candidate is
imported. Catalogue/selected-record provenance and contextual source identities
are in [SOURCES.json](SOURCES.json).

The result is limited to these seven registers, F2, unit-cost single-source
XORs and the stated alphabets. It does not exclude feedback savings in larger
dimensions, with extra registers, weighted or multi-source gates, other fields,
or changed frame contracts. No R439 word, selected frontier or frozen input
is changed. Native replay, hosted emission, all-size/compiler and common-frame
realization, intermediate precision/tape bounds, outer analytic transfer and
proof-assistant formalization are not checked. No new multiplication exponent
follows, and the selected frontier's cold replay is not rerun for this package.

## Open next questions

Does feedback save gates with four helpers and four targets? A concrete strict
gain would make the D-local relaxation useful. First obtain a specific K and a
fully restored unrestricted witness beating a *certified* restricted lower
bound. Larger search balls and the absence of a candidate remain blockers;
this result alone does not justify an unbounded larger census. Any candidate
would still need actual frame, precision and hosting costs before supplier use.
The structured question is in [TASK.json](TASK.json). The three-by-four domain
itself needs no further search.

## Credit

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in mathematics,
implementation, verification and writing. Apache-2.0. No subagents or independent
human review. Emulate processing was unavailable; the prose was checked against
the sources and executed results under the donor's stated fallback.

Credit @commdata2338 / PR1306 for the prior census, model, substitution lemma,
meet-in-the-middle setup and explicit handoff; @woklerx / PR1194 and PR1105 for
the semantic-D and feedback-cleanup lineage; and Arham Tahir / PR1311 for the
independent semantic-D application. Retain Zhihao Chen / PR425, eumemic / PR555,
DreamingOfClouds / PR589, Gareth Davidson / PR926, @theon199 / PR967 and Sagar
Thakrar / PR1062, with Aaron Wang / PR1015 and Ross Richardson / PR923, as the
underlying bit-word/checker lineage. This result does not claim a new version
of their constructions or substitution arguments.
