# R420 dirt correction through a restored target basis

**Finite bit-circuit construction; no new κ.** On eumemic's accepted PR543
R420 word, 57 disjoint target transvections reduce the frame-zero dirt
correction from **19,922 to 16,772 binary XORs**. Including preparation and
restoration, the complete native word falls from **26,916 to 23,766 ADDs**
(3,150 saved). No extra helper, copy, source access or frame movement is used.

| Quantity | Original | Target basis |
|---|---:|---:|
| D helper reads | 19,922 | 16,658 |
| D target preparation / restoration | 0 / 0 | 57 / 57 |
| Complete native ADDs | 26,916 | 23,766 |
| Exported records | 29,874 | 26,724 |
| Forward positive prefix | 144,651 | 144,651 |
| Reverse positive prefix | 2,270,064 | 3,703,810 |
| Local payload allowance, bits | 100 | 102 |
| Helpers / retained copies / rank mass | 420 / 9 / 5,112 | 420 / 9 / 5,112 |

The larger reverse prefix is charged, not inherited from the old circuit.
The new exact payload bound is
`64 * 144651^3 * 3703810^2 = 2657306775507971405724759110400 < 2^104`.
This is the local cohort allowance. A new hosted-parent finite invoice is
**not** supplied, and the old global precision charges are not asserted for
the changed word.

## Reproduce

From the repository root, with Python 3.9 or later and its standard library:

```sh
python3 -B research/r420-target-basis/verify.py
python3 -B -m unittest discover -s research/r420-target-basis -p 'test_*.py'
```

The verifier's final line is:

```text
PASS_R420_TARGET_BASIS D=19922->16772 native_ADDs=26916->23766 saved=3150 columns=660 rank_mass=5112 kappa=unchanged
```

It reproduces the matching, reconstructs the actual changed word, compares
every certificate field, runs the retained E8/frame checker, interprets all
660 symbolic inputs in both directions using a separate set representation,
and compares every record with the unmodified official exporter. Eight
negative controls and an F2-neutral but paid positive control are included.
Optimized Python is refused because the inherited exporter uses assertions.
No output files are overwritten; explicit certificate generation uses
`--write-certificate NEW_PATH` and exclusive file creation.

For the fresh C++17 legality and five-, nine- and eleven-stage replays:

```sh
python3 -B research/r420-target-basis/native.py
```

Install Boost headers or set `BOOST_INCLUDE` to their containing directory;
set `CXX` if the compiler is not `c++`. Expected final line:

```text
PASS_R420_TARGET_BASIS_NATIVE words=2 stages=5,9,11 columns=900,1380,1620 bridge_controls=96 missing_D_controls=6
```

Both original and changed words pass the unchanged C++ checkers. Each word
checks 900/1,380/1,620 physical formal columns and 6/18/24 omitted bridges.
A missing final D ADD is also rejected at every stage count; for the new
word that ADD is a mandatory target restoration. These are finite replays,
not a formal proof of the full multiplication theorem.

## Construction and sufficient interface

Work over F2. Let `K` be the original 120-by-420 helper-incidence matrix of
D, so D maps `(x,s,y)` to `(x,s,y+Ks)`. For distinct targets `a,b`, let
`P_ab` add coordinate `a` to coordinate `b`. It is an involution. For a
matching of disjoint ordered pairs, the transvections commute and their
product `P` is also an involution.

The new D performs three operations:

1. Add `y_a` into `y_b` once for each selected pair, producing `Py`.
2. Read the helper rows of `PK`. Row `a` stays `K_a`; row `b` becomes
   `K_a XOR K_b`; every other row stays unchanged.
3. Undo the target transvections in reverse order.

The result is `P(Py+PKs)=y+Ks`. This equality holds for **arbitrary target
inputs** as well as arbitrary helper dirt. Helpers and sources are never
written by D. Every touched register is a target or helper at frame zero,
so the extra ADDs are common-frame operations. Targets remain at frame zero
until the original scatter; all later instructions are unchanged.

The original literal H2 permits only helper-to-target reads in D. It rejects
this syntax, and its literal extraction of K also fails. We do not change
or disable either predicate. The sufficient replacement is:

> D is a legal frame-zero prefix whose complete operator is
> `(x,s,y) -> (x,s,y+Ks)`, with every helper unchanged before A.

The proof above establishes this replacement. The verifier separately checks
that operator on all 660 inputs, compares every field outside D with the
pinned source, and checks that the original H1/H3/H4/H5 and remaining
decomposed conclusions still hold. Substituting an equal prefix into the
unchanged `(A, scatter, B, C)` program preserves its F2 endpoint. The
original mutable-basis/common-label realization remains a conditional
interface requiring maintainer review for this changed D syntax.

This is an F2 endpoint statement. It does not assert equality of the two
forward integer matrices. Signed reverse execution uses inverse shears;
the cancellation-free integer bounds are recomputed in both directions.

The complete MOVE/COPY/ERASE subsequence is identical to the original, giving
the unchanged paid histogram `{1:1320, 2:1440, 4:60, 5:120, 8:9}`. All copies,
their closing operations and the original recursive children are retained.
The selected assembly is complex-limited, and a reduced scalar count alone
does not change a recursive exponent. No new bit exponent or κ is claimed.

## Search domain and controls

OS randomness assigned seed **5** and the bit-supplier track. We compared
three narrow candidates: phase-B block 5 (already PR674/688), phase-A quad 5
(close to PR691's quad-13 mechanism), and target-row conjugation (chosen).
No pinned sprint issue existed, so the scope is in `CLAIM.json`.

The search scores **all 14,280 ordered pairs** of 120 target rows. The exact
fully charged gain for `(a,b)` is
`weight(K_b) - weight(K_a XOR K_b) - 2`. A separate column-incidence census
checks every score. `random.Random(5)` supplies tie keys in lexicographic
pair order; decreasing `(gain,tie,a,b)` order and one greedy disjoint pass
select 57 positive pairs. Search stops after that pass. `RECIPE.json` records
every chosen pair and gain. No maximum-weight matching, optimal circuit,
or broader impossibility result is claimed.

Controls reject missing initial/final shears, a wrong helper row, nonzero
prefix frames, source access at frame zero, unrelated cleanup changes,
an omitted exported ERASE and an omitted exported target shear. In
particular, omitting the initial shear **passes every zero-target input**
but leaks arbitrary target dirt; an explicit test demonstrates why the
full input basis is needed. A cancelled target pair is accepted semantically
and charged two ADDs. Tests also reject overlapping pairs and a recipe
that omits restoration cost.

## Pins, related work and remaining obligations

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 source: `2065fe4f72a914d907f1046603f5a36f17018535`.
Selected PR626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`,
conditional κ `51110230636731/31250000000000000`.
`SOURCES.json` pins every consumed predecessor implementation, original
notice and selected-record input. The compressed word is pinned by its
decompressed bytes. `CERTIFICATE.json` pins the canonical new word and both
native instruction streams; `NATIVE-CERTIFICATE.json` records C++ coverage.

Concurrent [PR686](https://github.com/CrocSwap/integer-mult-bounds/pull/686)
by Mikhail R. Gadelha and
[PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694) by Greer
Guthrie factor **helper columns** and establish the semantic D-prefix
approach. They are credited predecessors to this investigation, not new
priority claims. PR694 head `9732ac127dd4bef98a846aaa904c20b5a84e72c1`
was inspected. This package factors **target rows**, restores arbitrary
target dirt, and imports neither their circuits nor their code. Its native
harness follows the validation pattern demonstrated in PR694. No composition
with those changes is certified here. PR670/674/688 concern phase-B blocks;
PR691 concerns a phase-A quad. Concurrent PR708 (Sagar Thakrar, head
`2ec522a466ec448f148d4355dc43b51c0ef1e0b5`) shares operands of the
separate FULL-frame decoder totals; it is not composed here. The final
overlap refresh covered open PRs through #709. PR661's fixed-order frame bound explicitly
excludes circuit changes, so this does not reopen its closed search.

Full hosted-parent reconstruction, whole-owner allocation, revised global
precision/finite invoices and a changed-word outer assembly remain separate
integration work. All-size compilation, common labels, mutable bases,
physical routing, residual hosting, precision/tape and analytic assumptions
remain. Neither `upstream/` nor the selected construction is changed.

Prepared by **Scott Woolsey Biggart (@swbiggart)** with substantial
**OpenAI Codex assistance** in the construction, proof, checking and
packaging. No independent human review is claimed. Apache-2.0. Credit remains
with eumemic (PR543/493 and xcheck), Dylan Crow (format/exporter/cohort
checkers), DaysSky (bridged stages and hosting), Zhihao Chen (scalar
interface), DreamingOfClouds (totals, pricing and engines), Chafik Boukhalfa,
icekylinx, Rohan Arun and the cumulative supplier/realization lineage. See
the unchanged [R420 notice](../e8-bit-r420/NOTICE.md) and
[carrier-skeleton notice](../e8-bit-carrier-skeleton/NOTICE.md) for the
complete inherited attribution and AI disclosures.
