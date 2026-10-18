# P111 Parseval blocks: a scalar-copy interface audit

**Exact fixed-class obstruction, not a new supplier or kappa claim.**

PR [1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900), pinned at
`9a891c9cb25b15f5a189bcad1d022198adeaf885`, gives a valid F2 Parseval
factorization of the selected P111 bit decoder. This audit **confirms** that
identity on all 111 targets and all 661 formal dirty input columns. It does
not repeat the complex-field obstruction in PR1889: F2 is the correct payload
field here.

The new result concerns the next implication: can the five coefficient blocks
be implemented as ordinary scalar copied totals at the sum of their five
union-support pairing ranks, `40`? **No.** In the explicitly bounded inherited
scalar model below, their exact minimum is **73**, versus the original decoder's
**63**. The literal ten Parseval scalar channels cost **74**. A hypothetical new
physical block-valued primitive is outside this lower bound; its cost is **not**
proved to be twice a union-support rank.

## Exact object and result

Reconstruct the selected PR589 word after its `D` and `A` sections. Its nine
retained channels and scatter supports give factors `P,Q`, with the entire
dirty update `P Q^T`. PR1900 uses the following columns of a 9-by-10 matrix `A`:

```text
3, 5, 6, 7, 8, 16, 32, 64, 128, 256   (little-endian binary vectors)
```

They satisfy `A A^T = I9` over F2. Group columns into `(0,1)`, `(2,3)`, `(4,5)`,
`(6,7)`, `(8,9)`. For each block, let `L` be its two transformed target columns
and `R` its two transformed source columns, including every dirty input. Its
map is `L R^T`, of rank two even after restricting to the 111 source ports.

A **scalar copied total** with support vectors `l,r` implements the rank-one
update `l r^T`. Its priced objective is the inherited rational pairing rank

```text
beta(l,r) = rank_Q( G[target_support(l), source_port_support(r)] ),
G = root_lines * root_lines^T / 2.
```

This is the per-total objective of PR446 Theorem C, retained in
[the P111 certificate](../p111-copy-rank-certificate/PROOF.md) and
[the bit label-decoder model](../bit-orthogonal-pair-decoders/PROOF.md).
It is not an assertion that every abstract term has a simultaneously legal
physical realization at exactly that price. Those additional costs remain
nonnegative obligations.

**The audited class:** in each fixed block, every scalar term has factors
`l=Lx`, `r=Ry` for nonzero `x,y in F2^2`. Arbitrarily many terms, asymmetric
factors, all basis changes, and repeated terms are allowed. Different blocks
are not rebased or canceled together. There is no new block-valued copy,
operator-valued encoding, or changed port geometry in this class.
Each total reads the fixed retained-channel values at this boundary and
preserves them; complete scalar calls restore private scratch. Source-mutating
or operator-valued encodings are outside the class, not assumed impossible.

| Block | Rank of the union-support pairing | Literal two scalar terms | Exact minimum, any number of within-block scalar terms |
|---|---:|---:|---:|
| 0 | 8 | 16 | 16 |
| 1 | 8 | 16 | 15 |
| 2 | 8 | 14 | 14 |
| 3 | 8 | 14 | 14 |
| 4 | 8 | 14 | 14 |
| **Total** | **40 (not a scalar invoice)** | **74** | **73** |

The optimum has seven rank-7 and three rank-8 scalar copies. For block 1 an
attaining factorization, in its local two-column coordinates, is

```text
(x,y,cost) = (2,3,7), (3,1,8).
```

The other blocks attain their minima with `(1,1)` and `(2,2)`. This improves
the literal Parseval scalar expansion by one, but still loses ten copy-rank
units to the original nine-channel decoder. The existing global optimum 63
for the broader scalar label-decoder model is predecessor work, not a new
claim here. Cross-block cancellation can recover the original nine-channel
factorization; that is why the fixed-block restriction is explicit.

## Proof of completeness and the interface counterexample

Both `L` and the source-port restriction of `R` have full column rank two.
They therefore have left inverses over F2. Consequently

```text
sum (L x_i)(R y_i)^T = L R^T  iff  sum x_i y_i^T = I2.
```

There are exactly nine nonzero pairs `(x,y)`. Two identical pairs cancel over
F2 and have strictly positive cost, so deleting both never increases cost.
Every finite factorization has a no-more-expensive representative among the
`2^9=512` subsets. The verifier exhausts all 512 for each block: 32 subsets per
block give `I2`, for 160 exact factorizations overall. All six ordered GL2(F2)
bases per block occur, but the census also covers every longer decomposition.
Each accepted subset is replayed against the full dirty block, not merely its
2-by-2 coefficient identity.

Every rank is exact. Rational reduction computes the support subspaces and
pairing rank; separate modular elimination on the original, uncompressed
Gram submatrix supplies the same rank lower bound. A field-control fixture
has rational rank three but F2 rank two, so these two rank notions are not
silently interchanged. The finite source checks support the written
all-length reduction; no proof-assistant verification is claimed.

A single scalar copied total has rank at most one, so it cannot implement
any rank-two block, regardless of how its rank-one supports are chosen.
In particular, actually using the two support unions as one scalar term per
block gives **5,838 wrong source-target entries** and **17,146 wrong entries**
on the full dirty input matrix. A smallest explicit source input is port 0
set to one, all other input registers zero: target 0 should receive one but
receives zero. The verifier also supplies 45 explicit two-bit witnesses
against the nine within-span single-total choices for each block.

This does **not** say a primitive with two independent operator-valued
channels must be two separately charged scalar copies. It says the inherited
scalar primitive does not perform the asserted block update. A physical
block-copy lemma must supply its own complete operator and invoice.

## Coverage law and favorable paid screen

The coefficient planes are planes in a **binary factor space**, not supplied
rational port planes on each of the 111 physical data families. Keeping the
selected line-port geometry keeps the one-unpaid-coordinate contract. Merely
regrouping decoder coefficients does not establish the source `E -> FULL`,
target `0 -> E^perp` endpoint for two-dimensional physical `E`. This is the
separate plane-port obligation posed by ctoth in
[Discussion1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510).

For a deliberately favorable screen of the fixed scalar interpretation, keep
all incumbent non-copy children, use its minimum copies, and set *all extra*
basis, storage, cleanup, routing, hosting and precision costs to zero. No such
cost is declared free in a completed construction. With `m=64`, `W=888/9=296/3`,
`R=42`, and unpaid=1:

| Quantity, per call | Original | Best fixed-block scalar screen |
|---|---:|---:|
| Centre copy charge | 63 | 73 |
| Total paid mass, `63 W + C` | 6279 | 6289 |
| Local paid mass | 5129 | 5139 |
| Idle mass | 1150 | 1150 |
| Deficit, `W-C` | 107/3 | 77/3 |
| Certified upper bound on `a` | 0.001947467559 | 0.001401325233 |

The complete profiles and certified adjacent-grid brackets are in
[RESULT.json](RESULT.json). They use the unchanged pinned `ceiling.py` with
`unpaid=1`, **not** the unproved `unpaid=2` physical interface. The changed
profile replaces two rank-7 children by three rank-8 children. Its moment is
larger throughout `0 <= a < 1`, since
`3(8/64)^(1-a) - 2(7/64)^(1-a) > 0`, with unchanged idle mass. Adding the omitted
implementation costs cannot rescue this fixed-profile route. Deleting or
redesigning other side work would change the screened hypothesis.

This is not a recalculation of the price of a genuinely new plane supplier.
No physical word, hosted template, precision invoice, assembly, selected-bound
change, or new kappa follows from this audit.

## Reproduction and evidence

From the repository root, with standard-library CPython 3.12:

```sh
python3.12 -I -O -B research/p111-parseval-copy-interface/verify.py
python3.12 scripts/research_package.py --package research/p111-parseval-copy-interface
```

`verify.py --write` regenerates the deterministic receipt. Normal replay
compares all proof-relevant fields with it. Explicit `require` checks remain
active under `-O`. The replay includes baseline and Parseval positive
controls, all subset/GL2 cases, 45 one-channel failures, ten optimal-term
omissions, a broken frame, an omitted block, switched channels, and the
rank-field control. Source bytes are hash-bound before use. The wrapper
checks package metadata and historical provenance too.

Locally exercised on **CPython 3.12.12, Darwin arm64** via
`uv run --python 3.12 --no-project python`: the optimized isolated generator
smoke and the registered replay both passed. The exact replay output was:

```text
PASS_P111_PARSEVAL_COPY_INTERFACE blocks=5 subsets=2560 factorizations=160 dirty_columns=661 copy_min=73 baseline=63 union_failure_entries=17146
PASS_REGISTERED_RESEARCH_PACKAGE research/p111-parseval-copy-interface outcome=negative-result
```

The first wrapper attempt rejected an invalid TASK outcome enum; it was
corrected to `negative-result` before the successful registered replay.
No mathematical verifier failure was suppressed.

The catalogue's complex-ceiling working example and lever script were run
as orientation controls; they do not verify a new bit construction. No full
repository suite, selected cold replay, native proof build, or human proof
review is claimed.

## Provenance and credit

- Independent OS-random seed `3cc9f4c8f3719f13f4ae6bf28c9ba982`, recursive-interfaces,
  coverage-law-change; all emitted cards are retained in [SELECTION.json](SELECTION.json).
- Exact baseline `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record hash
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Cinna Davis / 1337isnot1337's PR1900 supplies the valid Parseval construction
  and the audited copy claim. Exact head, Git blobs, constants and scope are
  in [SOURCE-CLAIM.json](SOURCE-CLAIM.json). No predecessor executable is imported.
- The selected PR589/PR555 word, DreamingOfClouds' PR446 pricing premise,
  and bit orthogonal-pair decoder proof retain their attribution. The
  P111 scalar-copy certificate was prepared with Codex at Russell Seligmann's
  request; Joel Pulikkan / GamingPuzzled's PR620 supplied the earlier cost-63
  experiments and cost classification. Their global scalar optimum is not
  claimed as new here; see the predecessor's [NOTICE](../p111-copy-rank-certificate/NOTICE.md).
  ctoth's Discussion1587 establishes the plane-port endpoint question.
  Douglas Colkitt's ceiling engine, prepared with Claude assistance, is reused
  unchanged. PR1889's complex scalar-lift audit is distinct and not reused.
- [Claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925833).
  The shared 2026-10-14 overlap snapshot covered 579 open PRs and 547 discussion
  records with complete pagination; targeted queries found PR1900 and its
  handoff, not a prior audit of this scalar-copy implication. Immediately before
  publication, live `Parseval` title/body search returned only PR1900, a
  `blockwise`/`copy` search returned no open PR, and the PR1900 head remained
  `9a891c9cb25b15f5a189bcad1d022198adeaf885`. Search coverage is not a novelty proof.
- Prepared by Adam Gall with substantial OpenAI Codex assistance in research,
  exact calculations, verification and writing. No independent human review.
  New work is Apache-2.0; existing source notices are unchanged.

## Open next questions

1. **Can a new physical block-valued copy implement these blocks at one
   union-support charge?** This is the mechanism that could bypass this
   scalar obstruction. First write its full operator on independent dirty
   source/target streams, including restored scratch and legal frames. The
   blocker is that no such typed primitive is supplied by coefficient grouping.
2. **Can a completed physical two-dimensional port contract share boundary
   work that the scalar interpretation cannot?** This is what could justify
   unpaid=2. First specify each data family's rational plane and a small dirty
   endpoint with all copies, frame changes and restoration charged. The
   coefficient-space factorization does not supply those physical planes.
