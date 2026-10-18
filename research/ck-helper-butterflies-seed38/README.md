# Restored helper butterflies reduce the CK scalar panel from 8,434 to 8,430

**Finite complex-supplier circuit construction; no new kappa.** Two dyadic
sum/difference helper changes improve the fixed historical PR917 target-forest
compensation panel beyond its best known single-shear matching price. Under
the pinned PR696 lowering, the complete panel costs **8,430 component
primitives**, versus **8,434** for the reproduced single-shear comparison.
The complete local words save **8 real-component primitives per orientation**.

| Complete paid scalar quantity | Shear comparison | Butterfly candidate |
|---|---:|---:|
| Compensation component primitives | 8,434 | 8,430 |
| Forward real primitives | 104,934 | 104,926 |
| Inverse-transpose real primitives | 104,950 | 104,942 |
| Scalar macros, either orientation | 15,779 | 15,779 |
| Paid recursive children | 3,698 | 3,698 |
| Generic local primitive bound | 8,503,557,667,318 | 8,503,557,667,310 |

The helper count, frame events and recursive profile are unchanged. The new
word uses the same 492 helpers, eight private centers and one coefficient
work register. All 725 incoming coordinate columns, including arbitrary
target/helper dirt and private inputs, are checked in both complete scalar
orientations. The positive scalar envelopes need 41 and 65 bits, within the
inherited 192-bit local allowance. These are finite scalar and accounting
checks; native physical admission and a global invoice are not executed.

## The new operation

For a disjoint helper pair `(a,b)`, prepare

```text
a += b
b *= 2
b -= a
```

This maps `(a,b)` to `T(a,b)=(a+b,-a+b)`, with

```text
T = [[1,1],[-1,1]],       T^-1 = (1/2) [[1,-1],[1,1]].
```

Restore by the literal inverse word `b += a; b /= 2; a -= b`.
Every source read, doubling, halving and coefficient-work clear is paid.
Each unit ADD/SUBTRACT costs two PR696 primitives, including its clear;
each scale costs one. Preparation and restoration therefore cost **5+5**
component primitives. Work may be dirty on entry and is cleared as specified
by the existing lowerer; no clean-work cache or clear elision is assumed.

If the two original matrix columns are A and B, the new columns are
`(A+B)/2` and `(B-A)/2`. Let F be the pinned PR917 target transform and C the
original compensation matrix. Helpers are first changed by T, the middle
adds `F C T^-1` times the changed helpers, helpers are restored by T^-1, and
targets are restored by F^-1. The resulting target is exactly `y+C h`, with
every incoming helper restored. This holds for arbitrary target and helper
values, not just zero initial targets. Disjoint pair supports let all helper
changes commute. The inverse-transpose implementation swaps each ADD's
operands and negates its coefficient, and reciprocates every scale, in the
same event order; it is independently checked as `h <- h-C^T y` on the panel.

The two butterfly pairs are **(255,249)** and **(271,265)**. Their scalar
panel prices are respectively 54 and 62, including both boundaries, versus
56 and 64 for the cheapest same-pair single shears in the comparison alphabet.
The determinant-two transform changes both helper coordinates. It is outside
the single triangular-shear class and outside the prefix-monomial permutation
class in our PR1095.

## Complete bounded census and matching scope

Keep all 106 target-forest edges of the frozen PR917 recipe. For each of the
**32,131 unordered pairs** of its 254 active helper columns, compare:

- identity;
- either directed single shear with coefficient in `{-2,-1,-1/2,1/2,1,2}`;
- the displayed normalized butterfly, using the larger helper index as a.

This covers **385,572** directed coefficient/shear cases and 32,131 butterfly
cases. Residual coefficients are lowered independently, with both boundary
changes fully priced. Exactly the two displayed butterfly edges improve the
best same-pair identity/shear price, each by two component primitives. The
certificate retains the complete gap histogram and canonical census digest.
No state cap or timeout truncates this finite census. Rescaled butterflies,
other normalizations, overlapping pairs, other target forests, shared work,
frame changes and arbitrary arithmetic circuits are outside its scope.

An existing local NetworkX installation nominated two 117-pair disjoint
matchings. The standard-library verifier accepts neither a solver status nor
an objective alone: it checks every selected edge against the complete census,
rebuilds all residual columns, charges every boundary, and executes the
resulting programs. It reconstructs the comparison price 8,434 and the new
price 8,430. The matching program is optional discovery, not a proof dependency.

**PR1081, by steph4n-gh**, independently proves the old 8,434 floor for the
same frozen forest, six-coefficient alphabet and PR696 lowering. Its dual
certificates are not re-executed or imported here. Combining that credited
floor with this complete per-edge census would also bound this exact enlarged
disjoint-pair class at 8,430: at most the two two-unit gains can be added. The
self-contained claim of this package is the verified 8,430 construction and
the exact per-pair census; it does not claim an independently re-proved global
matching optimum or an unrestricted circuit minimum.

## Cost and invoice boundary

The new matching has 2,093 residual additions, eight fewer than the shear
comparison. Its butterfly boundaries require eight extra scalar macros, so
both panels have 2,547 macros and both complete programs have 15,779. The
unchanged event streams contain 3,690 climbs and eight centers. With the
pinned invoice formula,

```text
compiler = 64*(73+1)^3 = 25,934,336
adapters = 16*(15,779 + 3,698 + 716 + 8) + 64*73 = 327,888
local bound = adapters*compiler + max(forward real count, backward real count).
```

The reserve is identical for these two candidates, so the eight-primitive
saving survives this particular local comparison. **This is not overall
invoice optimality.** PR1081 also records a different historical-cost witness
with fewer macros and a better generic adapter invoice despite a worse scalar
price. This package does not beat that lower-macro invoice or silently add
savings from separate optimizations. No hosted provider bindings, ownership,
global invoice, recursive exponent or outer assembly is changed.

## Verification and reproduction

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -O -B research/ck-helper-butterflies-seed38/verify.py
```

Use `python` on Windows. Expected final line:

```text
PASS_CK_HELPER_BUTTERFLIES pairs=32131 panel=8434->8430 extra_real=8/8 columns=725 controls=10 no_new_kappa
```

Five mandatory source pins are checked before the sole predecessor code
import, PR696's lowerer. Every encountered coefficient price is checked
against the literal lowerer. A separate Fraction matrix interpreter checks
both complete panels on all 366 involved target/helper columns, with all
other columns untouched. A dense integer-grid interpreter executes the new
complete primitive streams on 725 independent columns. Each halving must be
exact on the chosen 2^-32 coefficient grid; the final matrix is checked
coefficient by coefficient, including restored logical helpers and cleared
private inputs. This is exact symbolic linear algebra, not sampled inputs.
Every unchanged non-scalar event is compared literally with the pinned source.

Ten controls reject omitted doubling/restoration, wrong normalization/sign,
reversed order, overlapping helpers, unpaid boundaries, work/source aliasing,
duplicate JSON and nonfinite JSON. The complete decoded certificate is compared
with type-sensitive canonical JSON; checks stay enabled under `-O`. The default
command writes nothing; `--write-certificate` deliberately regenerates it.

`python3 -I -O -B research/ck-helper-butterflies-seed38/test_package.py`
checks optimized minimal relocation and four actual corrupted packages. It
prints `PASS_CK_BUTTERFLY_PACKAGE relocation=1 corruptions=4`.

`discover.py` optionally nominates matchings using NetworkX. It writes only
when given `--write-witness`; default verification never needs NetworkX or a
solver. Discovery is deterministic for the recorded local version, but tied
solver witnesses need not be portable. The committed literal witness is the
reproduction input, and its mathematical validity is independently checked.
The local discovery version was NetworkX 3.6.1; no dependency was installed.

## Provenance and limits

Frozen base **abdc6a7002abdbcd9e21bfc5e1a795784deacfdf**; assigned seed **38**,
without reroll. Seed38 selects this round and the retained historical target
forest, not a random correctness assumption. At that base the accepted source
is PR942 with conditional kappa 0.001661960547713947. Main subsequently selected
PR1042; this experiment deliberately studies the historical PR626 CK word and
does not assert that its counts describe the current selected supplier.

Credit **Ross Richardson's PR917** for the two-sided CK recipe, **Hemant's
PR816** for the target forest, **David Awad's PR807** for helper-pair antecedents,
and **Sagar Thakrar's PR696** for the exact lowering. PR1081 supplies the
strongest relevant single-shear comparison and the scalar/invoice distinction.
Chafik Boukhalfa's PR626, Jeremy Kothe's PR622 and the retained icekylinx
compiler lineage supply the original programs and accounting. Their source
files and notices remain unchanged. Fresh PR1064 factory fusion, PR1088 signed
three-wire connector optima, PR1086 cleanup reordering and PR1080 U8 bi-forests
are different objects or rewrite classes; no independent savings are stacked.
PR931's bounded butterfly search concerns the PR681 factory, not this CK
compensation panel; its negative result is not reopened. No priority is claimed
for the classical sum/difference transform itself.

Only this package is added. Native phase/frame execution, physical common-label
realization, whole-call hosting, all-size compilation, precision/tape and
analytic transfer remain inherited obligations. A finite exact scalar replay
is not a formal proof of integer multiplication or a practical speed benchmark.
Prepared for **@woklerx**, with substantial **OpenAI Codex assistance**;
Apache-2.0. Algorithmic crosschecks and AI review are not independent human
peer review. See [NOTICE.md](NOTICE.md), [SOURCES.json](SOURCES.json) and
[VALIDATION.json](VALIDATION.json).
