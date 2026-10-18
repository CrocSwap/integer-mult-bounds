# Six fixed-neighbour coalescences: exact two-choice classification

**Research audit / scoped negative result. No new kappa.**

For the six A-gate sites in Chafik Boukhalfa's (@chafreaky) [#583](https://github.com/CrocSwap/integer-mult-bounds/pull/583),
the only frame-chain-admissible replacements, with every other gate and frame
fixed, are the original line and the already selected plane. This class
therefore has exactly **64** assignments. An independent frame-set replay
checks every assignment and all **192** directed single-edit transitions.
Each selected plane replaces two rank-1 payments with one rank-2 payment,
regardless of the other five choices. All 504 helper widths are unchanged.

This corroborates #583's accounting, not a counterexample to it. The new
evidence is the complete fixed-neighbour classification, 1,530-plane census,
and code-disjoint subset replay. It does not repeat a closed optimization
search with a larger random budget.

## Reproduce

From the repository root, Python 3.11+ and standard library only:

```sh
python3 -B research/coalescing-subset-audit/verify.py
```

The command authenticates the supplier's 314-file manifest, rebuilds its raw
input word in a temporary directory, recomputes the audit, compares every
receipt field with `RESULT.json`, and removes temporary reconstruction files.
Expected final output:

```text
PASS_SIX_COALESCENCES_ALL_SUBSETS_AND_CONTAINING_PLANES
64 subsets; 192 marginals; 1530 containing planes; 18 negative controls
```

The reconstruction uses the credited predecessor builders unchanged; only
the frame accounting is independently implemented. The audit imports neither
`gk_word.profile` nor its binary Gaussian elimination. A frame is represented
by its complete set of at most 512 vectors; containment is literal set
inclusion, and dimension is the base-two logarithm of its cardinality.
Every A/B gate incidence, centre-scatter descent and terminal endpoint is
replayed. No floating-point arithmetic or numerical rank test is used.

For an already reconstructed input, `--word /path/to/FULL-WORD.json.gz` skips
only reconstruction and requires the same exact decoded-content digest.
`--write-result` regenerates only this package's receipt. Compression bytes
are not compared for regenerated words.

## Exact statement and proof

Let `L` be the original one-dimensional frame and `P` the nominated plane
at one of the six sites. The certificate reads the following neighbouring
frames directly from the unmodified word:

- target register: `0 -> L -> P`;
- source register: `L -> L -> P`.

Replacing the common middle frame by any subspace `F` is monotone on both
registers if and only if `L <= F <= P`. Since the quotient `P/L` has dimension
one, its only subspaces are zero and itself. Consequently **`F=L` or `F=P`**;
this excludes all other dimensions as well as all other planes. This is a
short written linear-algebra proof applied to exact finite premises, not a
proof-assistant formalization.

The finite census independently lists every plane containing `L`: adjoining
one of the 510 vectors outside `L`, with two representatives per plane, gives
255 distinct planes. Literal neighbour-containment checks admit exactly one
at each site. All six admitted planes are also checked by full-word replay.

| A index | Target | Source | Nonzero generator of L | Nonzero vectors of P |
|---|---:|---:|---:|---|
| 78 | 465 | 464 | 1 | 1, 126, 127 |
| 75 | 467 | 466 | 7 | 7, 121, 126 |
| 72 | 469 | 468 | 7 | 7, 120, 127 |
| 69 | 463 | 462 | 1 | 1, 120, 121 |
| 66 | 517 | 516 | 31 | 31, 103, 120 |
| 61 | 515 | 514 | 31 | 31, 102, 121 |

The twelve incident registers are distinct. Thus no edit changes a neighbour
on any other edited register: the six two-choice domains form a Cartesian
product. The complete audit separately replays that product rather than
assuming independence from the table alone.

For `F=L`, the target pays ranks 1 and 1 while the source pays rank 1. For
`F=P`, the target pays rank 2 while the source pays rank 1. Hence the net
change is exactly `Delta H_1=-2, Delta H_2=+1`. The rank mass is unchanged.
For a subset of size `k`, the only changed counts are therefore

```text
H_1 = 2420 - 2k
H_2 = 564 + k
```

The other counts are `{3:320, 4:192, 5:56, 6:56, 8:8}`. The complete original
and final profiles, all intermediate profiles, incident-frame witnesses and
individual control failures are in `RESULT.json`.

For any additive rank tariff `f` with `f(2) < 2 f(1)`, selecting all six planes
is the unique optimum **within this fixed-neighbour class**, with saving
`6 (2 f(1) - f(2))`. In particular this holds for `f(r)=r^(1-b)` and `b>0`.
This statement is about the local tariff, not a newly priced full supplier.
The historical 48-call dispatch gives `Delta H_1=-576, Delta H_2=+288`, exactly
as #583 reported; physical dispatch and phase admission are not rerun here.

## Negative controls and scope

Eighteen semantic controls are exercised:

- omit each edit: the profile differs from the full selection by
  `{1:+2, 2:-1}`;
- replace each frame by the full nine-dimensional space: the next incident
  gate rejects it as nonnested;
- use another plane of the **same dimension containing the old line**:
  the next incident gate still rejects it. Dimension and old-line containment
  alone are not an adequate legality check.

This is a classification under a fixed scalar word, gate order, register
incidence, entrance frames, centre frames and all unlisted operation frames.
Changing neighbours, adding helpers, reordering operations or changing the
scalar word is outside the class. It is not an impossibility theorem for
better suppliers. Native residual/Clifford feasibility is stronger than the
frame-chain conditions checked here. Scalar coefficients and incidences are
unchanged by construction; no new native, scalar-column, owner, assembly or
all-size replay is claimed.

The base-selected #1042 construction remains conditional on all-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer and bit H1-H5 assumptions. This audit neither
discharges nor weakens them and does not edit the selected certificate.

## Pins, domain and attribution

- Exact base: `ba82555c64e1879e4b7decce28186f208fcb8262`.
- Audited #583 source head recorded by the selected record:
  `89be768f0157f5a3d8e4db69cf1748768605eac9`.
- Vendored #579 dependency: `970d38a3862ee35064a827b671d196744ee2a928`.
- `SOURCES.json` pins the full supplier manifest (314 immutable files), which
  pins the recipes, constructors, frame algebra, proof and predecessor inputs.
- Decoded raw input SHA-256:
  `d339ebf52842f9ce01999106483eb59467b12ba6d13ce7757e7afdbaecbf98b7`.
- Domain: six fixed sites, all 64 subsets and all 255 containing planes per
  site. Stop after complete enumeration, not after finding an improvement.
- Assignment seed 67 (OS draw and selection rationale in `CLAIM.md`); it
  rotates the subset traversal by three. It does not change the exhaustive
  domain or establish novelty by itself.

The six chosen frames, historical gain and original admission belong to
**Chafik Boukhalfa** (#583), building on #579 and the PR535 coalescer. Retain
Jonathan Capalbo's #575 joint prefixes; Jeremy Kothe's #576/#568 kernels;
Dominik Scholz's #571/#569 construction; and DreamingOfClouds' exact word and
frame representation lineage. See the unchanged
[original notice](../kernel-frame-coalescing/NOTICE.md) and vendored notices
for complete ancestry and licenses. The maintainer's
[family588 review](../../docs/research/community-family588-review.md) already
accepted the historical finite construction; this work is additional scoped
evidence, not priority for those edits.

Before submission, open-PR metadata was refreshed through #1111. In
particular, Rohan Guliani's [#815](https://github.com/CrocSwap/integer-mult-bounds/pull/815)
at `d8c8b40ab0a95b6d77389e6726d86dddb60fb53c` studies a much broader
frame-assignment class on the different #626/#741 words using LP/CP-SAT.
Its stated lack of an exact rational dual certificate is not treated as a
counterexample or failed search. This contribution is narrower, uses no
solver, proves its finite-class exclusion directly, and audits #583's six
historical sites. It does not reestablish or supersede #815's claims.

Contribution by **Adam Gall (@adamgall)** with substantial **OpenAI Codex**
assistance for research, implementation, verification and writing.
New files are Apache-2.0. No upstream or predecessor source is modified.
