# Four omitted ADDs cannot preserve the frozen PR967 helper-star boundary

**Finite certificate and scoped algebraic reduction; no new kappa.** None of
the **39,861,761,780,790** four-position subsets of PR967's frozen 5,563-ADD
`D` word can be deleted while preserving its full linear map on all 661
arbitrary dirty input columns. This resolves the explicit four-omission question
in [woklerx's PR1446](https://github.com/CrocSwap/integer-mult-bounds/pull/1446).
The one-, two- and three-omission results are PR1446's contribution; their
premises and zero counts are corroborated here. Any nonempty neutral omission
set, if one exists, therefore contains at least five positions.

This excludes one small, fixed simplification class. It does not prove that
the helper-star circuit is shortest, and it does not exclude inserted gates,
reordering, another helper basis, a changed interface, or a different word.
The selected supplier, paid recursive profile and exponent are unchanged.

## Object, provenance and new contribution

The input is
`research/r439-helper-stars-seed19/candidate.json.gz`, SHA256
`d8b08885e8ce9868200b2645189d15ed18a27fc2742e54990b3257a0ca4df6b8`.
Flatten each `D` record's source list in its stored order: one source is one
elementary XOR/ADD position, numbered from zero. All these gates are at frame
zero. No source, target or helper column is treated as clean or unobserved.

Exact base: `1ff9c501b624ec354e1330b1b9be571a6adba9cb`.
Exact retained predecessor heads:

| Predecessor | Head | Contribution used |
|---|---|---|
| PR1446, woklerx | `83bab0ac63d7297309e769641d176ca3f12b0124` | Transported-transvection reduction, one/two/three omission results and four-omission handoff |
| PR967, Sricharan Vagvala / theon199 | `c6caa79e6655d83780a3b70a1d658313126fb0b3` | Frozen helper-star construction |

All live input blobs and SHA256 values are in [SOURCES.json](SOURCES.json).
No pending implementation or unreviewed mathematical claim is a dependency.
The predecessor factor digest is used for corroboration; no predecessor Python
module is imported as an acceptance oracle.

The new work is the complete four-omission census and its exact image-plane
partition, which avoids retaining a table of all 15,470,703 pair products.
The largest image-plane bucket contains only 11,812 pairs. A second full
census partitions the same domain by covector planes; its largest bucket is
690 pairs. These are two uses of the same census implementation, not two
independently authored verifiers. Separately implemented dense matrix and
literal deletion checks provide the independent finite controls below.

The chooser selected `bit-helper-contract`, priority revision 3. The scope is
explicitly **changed** from proposing a replacement H2/K interface to PR1446's
named boundary audit, because PR1194/1311 already cover the immediate semantic-D
replacement. Its value is a precise stopping rule for this local simplification
class; it is a side result, not progress on the binding complex moment.
[TASK.json](TASK.json) records the complete scope and stop rule.
The claim is in [discussion #2004](https://github.com/CrocSwap/integer-mult-bounds/discussions/2004).

## Proof of the reduction and exhaustive coverage

Work over F2. Let the chronological elementary gates be
`L_i = I + e_dst e_src^T`, with distinct operands, and
`P = L_(n-1) ... L_0`. Each `L_i` is an involution. For its **original baseline
suffix** `B_i = L_(n-1) ... L_(i+1)`, define

```
T_i = B_i L_i B_i^-1 = I + u_i v_i^T,
u_i = B_i e_dst,          v_i^T = e_src^T B_i^-1.
```

Both factors are nonzero and `v_i^T u_i = 0`. As in PR1446, cancellation of
baseline suffixes gives, for omissions `a < b < c < d`,

```
P_deleted P^-1 = T_d T_c T_b T_a.
```

Thus the four omissions are neutral exactly when

```
T_b T_a = T_c T_d.                         (1)
```

The right side is the **inverse** of the late chronological pair product.
Using `T_d T_c` there would be wrong for noncommuting pairs. The checker keeps
both orientations and includes a positive example that detects this mistake.

All 5,563 transported factors are distinct. For two distinct factors,

```
T_b T_a - I
  = [u_a,u_b] [[1,0],[v_b^T u_a,1]] [v_a^T;v_b^T].             (2)
```

If `u_a = u_b`, the product minus identity is
`u_a (v_a+v_b)^T`; if `v_a = v_b`, it is
`(u_a+u_b) v_a^T`. Nilpotency removes the cross term in either case.
These are rank-one products and the factors commute. No pair belongs to both
cases, since the original factors are distinct. Rank-one equality is tested
with its unique nonzero binary outer-product factors.

Otherwise both two-column/two-row outer matrices in (2) have rank two and
the middle matrix is invertible. The product minus identity has rank two and
image exactly `span(u_a,u_b)`. Consequently two such products can be equal
only if their image planes are equal. A binary plane has exactly three nonzero
vectors. For each pair of distinct image vectors present in the source, the
checker includes their sum if it is also present; a three-member plane is
visited only at its two smallest vectors. A two-member plane is visited once.
This partitions every rank-two pair without any numerical hash approximation.

Fix a basis `(x,y)` of one such plane. Every product in that bucket has a
unique representation

```
T_b T_a - I = x r^T + y s^T.
```

The two exact 661-bit row masks `(r,s)` are its key. The implementation
computes these directly from (2) and separately computes the inverse product
key. Python dictionary collisions are resolved by exact tuple equality; a
digest is never used to decide product equality.

For each forward key, keep the earlier pair endings `b` in sorted order. For
each late inverse key `(c,d)`, count only endings **strictly less than c**.
This enforces `a<b<c<d`, excludes overlapping/interleaved pairs, and counts
each neutral four-subset exactly once, at its unique earliest-two/latest-two
split. The checked rank-one and rank-two pair totals sum to `choose(5563,2)`.
Equations (1) and (2) therefore reduce the entire four-subset domain to the
reported finite pair census. This is not brute-force enumeration of forty
trillion four-subsets.

For the dual check, transpose every factor, exchanging `u` and `v`.
The new chronological four-product is the inverse transpose of the original
four-product, so its identity condition is equivalent. The rank of each
pair-product minus identity is unchanged under inverse transpose. This gives
a different full partition with the same neutral counts.

## Exact result and controls

| Quantity | Image-plane run | Covector-plane run |
|---|---:|---:|
| Distinct partition vectors | 530 | 761 |
| Planes visited | 140,053 | 289,016 |
| Three-member planes | 66 | 82 |
| Rank-one pairs | 193,704 | 193,704 |
| Rank-two pairs | 15,276,999 | 15,276,999 |
| Largest rank-two bucket | 11,812 | 690 |
| Neutral four-subsets, rank-one / rank-two split | 0 / 0 | 0 / 0 |

The verifier reconstructs factors by a backward suffix sweep. A separate
forward-prefix calculation checks the transported covectors. Every one of
the 5,563 literal single omissions is then replayed on all 661 symbolic input
columns, checking its full outer-product difference against the baseline.
The resulting complete factor digest agrees with PR1446's frozen receipt.

The registered command also checks:

- All 5,985 four-subsets of all 21 nontrivial three-dimensional binary
  transvections in eight fixed orderings: **47,880 dense matrix checks**.
  Their neutral counts are `21,16,13,10,21,16,13,10`; both rank strata have
  positive fixtures.
- All 128 deletion subsets of a seven-gate noncommuting literal word, against
  independently replayed deleted circuits and the original baseline inverse.
- Rejection controls for wrong product orientation, a changed chronological
  order, interleaved pairs, repeated positions, duplicate/zero/non-nilpotent
  factors, and a clean-input-only check that misses dirty-helper leakage.
- Eight focused test groups, including all 1,728 deletion subsets of all 216
  three-gate three-wire words, plus factor and receipt corruptions.

All verifier predicates remain active under `-O`. Finite controls support the
implementation; the coverage argument above supplies the quantified reduction.
No Lean proof or independent human mathematical review is claimed.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 scripts/research_package.py --package research/r439-four-omission-boundary --check-only
python3 scripts/research_package.py --package research/r439-four-omission-boundary
# Direct, read-only mathematical replay:
python3 -I -O -B research/r439-four-omission-boundary/verify.py
```

Expected mathematical output:

```text
PASS_FOUR_OMISSION_CENSUS gates=5563 pairs=15470703 four_subsets=39861761780790 neutral=0 columns=661 dual_neutral=0 dense_controls=47880 no_new_kappa
```

One CPython 3.12 run of both complete partitions, single-omission replays and
controls took about 52 seconds and 137 MiB peak RSS. These are reproduction
measurements, not a multiplication-runtime claim. `--write` explicitly
regenerates [CERTIFICATE.json](CERTIFICATE.json); normal replay is read-only
and compares every receipt field.

## Limits and remaining obligations

The result is only about deleting four elementary gates from the **exact
frozen PR967 D word** while preserving its complete binary scalar endpoint.
It does not cover five or more omissions, whole-record deletion of other sizes,
inserted/reordered gates, target-only observation, changed helpers, the newer
PR1062 word, or alternate frame/operation contracts. No new scalar circuit is
constructed. PR1102's diagnostic input vectors are not asserted to detect
multiple faults; full endpoint inequality only guarantees that some input does.

Native multistage replay, physical hosting, precision/tape, H2/K admission,
all-size compilation, exact recovery, analytic transfer and the selected cold
replay were not run or proved. They are unnecessary for this finite unchanged-
source boundary statement and remain separate obligations for any new supplier.
No packing cap is claimed: there is no changed complex local profile or kappa.

## Open next questions

Can the star structure prove a larger deletion-distance bound without
enumerating all triple products? This would decide a broader local
simplification class. First classify products of three transported factors
using the helper/target block structure and test whether their image/row spaces
admit a compact exact partition. The blocker is that the present image-plane
argument does not cover rank-three products; a naive triple table already
has 28,677,526,461 entries. This question is recorded in [TASK.json](TASK.json)
and is not a recommendation to enlarge the search without a new reduction.

## Credit and license

Credit woklerx for PR1446's reduction, earlier omission exclusions and explicit
handoff, PR1017's single-omission atlas and PR1102's diagnostic probes;
Sricharan Vagvala / theon199 for PR967's helper stars; Gareth Davidson for
PR915/926's target basis and restored pairs; DreamingOfClouds for PR589 and
eumemic for PR555/543 and the retained checker lineage. The required orientation
example is Sagar Thakrar's PR1062 composition, using Aaron Wang's PR1015 and
Ross Richardson's PR923 block programs. Their sources remain unchanged.
No priority is claimed for transported transvections, rank-one factorization,
meet-in-the-middle search or the predecessor constructions.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. All predecessor licenses and notices remain in place.
