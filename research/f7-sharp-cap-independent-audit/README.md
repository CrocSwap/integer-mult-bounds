# Independent audit of the sharp five-label cap

**Corroboration; no new bound or kappa.** This answers Ali Romman's explicit
[independent-review handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138920)
for [PR4992](https://github.com/CrocSwap/integer-mult-bounds/pull/4992).
The written-proof review below finds no blocking gap in its stated domain.
A separately implemented six-plus-six path join corroborates the cap **11**
and exclusion of every weight-four **(8,4)** split, without using either result
to discard a path. It imports no predecessor executable.

The audited theorem concerns simple restored universal singleton-prefix walks
of length twelve in F2^5, and functionals of weight four or five. For the two
functional classes A,B, the excess is

`choose(|A|,2) + choose(|B|,2) - |D(A)| - |D(B)|`,

where D(C) contains XORs of distinct pairs in C. Shared differences in the two
classes count twice. Universality means the twelve vertices have all 32 XOR
sums, including zero. The result and both equality witnesses belong to the
predecessors; this package adds independent implementation and proof coverage.
This is AI-assisted review, not independent human or proof-kernel acceptance.

## Written-proof audit

Reviewed source: PR4992 head `12a0105150f5f44a19a2199db8506d1aa44b009a`,
retained at main base `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`.
Its [proof](../f7-five-label-sharp-cap/README.md), verifier and receipt are
exactly bound in [SOURCES.json](SOURCES.json). They are authenticated, not
executed by the new verifier. The original registered verifier was also replayed
separately, in both normal and optimized Python.

1. **Class coverage and balance.** Universality implies
   `D(A) union D(B) = ker(f) minus {0}` because cross-class differences have
   functional value one. For weight four, the omitted-coordinate edges form
   a matching, including the closing edge. Counting degree two at every cycle
   vertex gives `s-t=a-b`, `2a<=s`, `2b<=t`. Hence the only unordered splits
   are (6,6), (7,5), (8,4). Weight five alternates and forces (6,6).
2. **Saturation in (8,4).** Equality forces four omitted-coordinate edges
   in the majority, none in the minority, and eight crossing edges. Every
   majority vertex belongs to exactly one matched pair. Contracting those
   pairs leaves four distinct block labels T in the even subspace E of F2^4.
   The four minority vertices alternate omitted-coordinate levels. No
   planarity assumption on the minority is used.
3. **The potentially delicate repeated projection.** A planar T supplies only
   seven lifted majority differences, insufficient even with six minority
   differences. Thus T has six differences. Its missing direction z satisfies
   `E = T disjoint-union (T+z)`. The minority must supply both missing lifts
   (z,0) and (z,1). A same-level pair u,w=u+z occupies both vertices of one
   level. A pair supplying (z,1) must use one of these vertices, so the other
   level repeats u or w. Relabel to repeat u. The cyclic minority order is,
   up to reversal and rotation, `u_0,u_1,w_0,y_1`; y=w is allowed. The four
   distinct contracted blocks require at least three neighbors of u in T
   and two of w. Translation by z exchanges T and its complement in E and
   sends N(u) to N(w), so those two neighbor counts sum to four. This is
   the claimed contradiction. Distinctness of the block labels, rather than
   distinctness of all four projected minority points, justifies the count.
4. **Small support lemma.** Five, six or seven points have affine dimension
   at least three. In dimension three their difference support is seven.
   In dimension four an affine basis gives ten differences; a sixth point
   of weight two or three gives twelve, and weight four gives fifteen.
   To make the weight-three case explicit, translate
   `{0,e1,e2,e3,e4,e1+e2+e3}` by e1 and use the basis
   `(e1,e1+e2,e1+e3,e1+e4)`. The extra point is the sum of the second and
   third basis vectors. Thus both twelve-support cases reduce to the source's
   `{0,1,2,3,4,8}`. Its four-row table covers every possible seventh point
   and contributes a new difference, giving at least thirteen.
5. **Final excess.** In (6,6), supports of size seven and seven cannot cover
   fifteen directions, so their sum is at least 7+12. In (7,5), a
   three-dimensional seven-point class would require the five-point class
   to cover eight directions outside that subspace. Its two cosets supply
   at most `k(5-k)<=6` such pairs. Hence the seven-point class has full
   affine dimension; the support sum is at least 13+7. Both excess bounds
   are eleven. The two cited words attain equality.

This review covers the claimed proof implications, including the nonplanar
minority. It does not establish any seven-label or partial-prefix assertion.

## Independent finite method and completeness

The new enumerator lists **every simple six-edge cube path starting at zero**,
grouped by its final vertex. It joins every unordered pair with that same
endpoint whose vertex-set intersection is exactly the two endpoints. Reversing
one path yields a simple twelve-edge cycle, with the closing edge included.

Conversely, split any simple twelve-edge cycle based at zero at its sixth
edge. Its two halves appear in these lists and have disjoint interiors.
The split is unique, and reversing the cycle only exchanges the halves.
Thus the join enumerates each cycle exactly once up to reversal. There is no
label-permutation reduction, universality prune, matching-balance prune,
quotient test, or excess prune in this generation step.

After generation, direct pair XORs decide universality and compute each of
the six high-weight functionals. Every generated cycle separately passes
vertex, simplicity, adjacency and closing-edge checks. Six smaller domains
compare the complete cycle sets against literal enumeration of every word;
they also check that the join emits no duplicate cycle.

| Quantity | Independently recomputed count |
|---|---:|
| All rooted cycles up to reversal in Q5, length 12 | 221,700 |
| Those using all five labels | 202,860 |
| Universal cycles | 49,680 |
| Universal cycle / high-weight functional checks | 298,080 |
| Universal weight-four (8,4) splits | 0 |
| Maximum excess for each of the six masks | 11 |
| Literal words in the six calibration domains | 77,019 |
| Distinct calibration cycles | 418 |

The complete excess histogram agrees with PR4907's earlier receipt after
multiplying by 60. This comparison happens after generation and evaluation.
That factor is exact: a simple twelve-cycle uses four or five labels, and
both label orbit sizes in Q5 are 120; this audit then identifies the two
orientations. Summing over every high-weight functional preserves the same
factor. The prior 828 universal normalized words and their maxima are not
new discoveries. [RESULT.json](RESULT.json) retains the full histogram and
a digest of the deterministic universal-cycle stream.

## Reproduction and controls

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/f7-sharp-cap-independent-audit
```

The registered commands run the independent audit normally and with `-O`,
then its mutation controls. Expect `PASS_F7_SHARP_CAP_INDEPENDENT_AUDIT`,
`PASS_F7_AUDIT_CONTROLS`, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
One full enumeration took about five seconds locally on Windows 11 with
CPython 3.12.0; this is a reproduction estimate, not a speedup claim.
Direct commands, also valid in an export containing the declared inputs:

```sh
python3.12 -I -B research/f7-sharp-cap-independent-audit/verify.py
python3.12 -I -O -W error -B research/f7-sharp-cap-independent-audit/verify.py
python3.12 -I -O -W error -B research/f7-sharp-cap-independent-audit/test_mutations.py
```

Eight semantic rejections cover the too-small cap, wrong functional domain,
length, repeated vertex, omitted closing edge, boolean vertex, nonuniversality
and a universal point set lacking the cycle contract. Both sharp witnesses
are positive controls. The set-only and low-weight counterexamples have
excess 18 and 21, respectively, and demonstrate why the hypotheses matter.

Six actual code mutations exercise the small literal-word calibrations and
semantic controls **without receipt comparison**: overlapping path interiors,
a missing coordinate, a missing closing edge, coordinate-bit grouping,
cross-class support, and cap ten. Two additional private-copy CLI controls
alter the reviewed proof and replace integer 1 by boolean true in the receipt.
The latter requires typed JSON comparison. Frozen inputs are never edited.

## Scope, coordination and credit

Task `census-pruning-audit`, changed scope under the explicit handoff; priority
revision 7. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4903#discussioncomment-19140301).
The entry overlap check covered 324 open PRs and 4,127 Discussion records
with complete remote pagination. After materializing relevant f7 packages,
103 local records were searched; 6,609 tracked notes remained omitted.
Arbitrary diffs and unpublished work are also outside that coverage.
PR5001 and JoyboyBrian's active prefix-engine integration are separate.

The source-binding orientation for selected #4470 passed. The selected kappa
remains `60403/20000000`. No selected cold replay, engine integration,
seven-label census, supplier admission, full multiplication theorem, Lean
or independent human review is claimed. Full-history ancestry preflight
is not claimed in this shallow checkout. The audit covers the exact pinned
proof and finite domain; later source changes require reassessment.

Credit **Ali Romman / PR4992** for the sharp theorem and neighbor-count proof;
**Mihir Srivastava / PR4907** for the earlier cap, quotient setup, finite
measurements and handoff; **Nick Petalas / PR4894** for matching balance.
Retain **unpaidmoon / PR4148**, **Nicholas Stone / PR2973**,
**James Reed / PR3096**, and **Ross Richardson / PR943** for the question,
corrected excess boundary, audit and singleton-prefix model. The new algorithm
is separately implemented; the reviewer read the predecessor sources and
does not claim a blinded review. Original sources and notices are unchanged.
Prepared by Mihir Srivastava with substantial OpenAI Codex assistance, solo.
New work is Apache-2.0.

## Open next questions

Independent human or proof-assistant review can strengthen confidence in the
four-block contradiction; begin with step 3 above, including y=w, and the
explicit affine-basis change in step 4. This requires new review, not a larger
finite census. PR5001's partial-prefix contract and its already claimed engine
integration remain the relevant downstream work. This audit does not reserve
them or infer a runtime benefit. No larger census is justified by this result.
