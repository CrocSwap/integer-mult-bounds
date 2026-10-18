# Independent arithmetic audit of the selected T21 recurrence

**Status: independent finite verification; no new kappa.**

This confirms both the native and conservative complex moment brackets used
by the PR890 construction selected at the pinned base. Each lower endpoint is strictly below
the recurrence threshold, and its adjacent `10^-24` successor is strictly
above it. The implementation uses only positive generalized-binomial terms,
integer outward rounding and a geometric tail. It imports no production
logarithm, exponential, supplier or owner implementation.

The exact contribution base is `007664306fff84fbb1c9a1b4053b69f439764034`. The selected
conditional kappa remains `1661957774647029/10^18`. This is an arithmetic
audit of its paid profile, not a fresh physical replay or a proof of the
complete multiplication theorem. The preliminary package used
`47481c89fd30a43f8f882eb4b391e89c29273fd0`; its assembly and selected-record
inputs are byte-identical at the contribution base.

## Reproduce

Python 3.11+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/t21-binomial-audit/verify.py
python3 -I -O -B research/t21-binomial-audit/test_package.py
```

Expected first marker:

```text
PASS_T21_BINOMIAL_MOMENT four strict endpoint decisions; 450 algebraic comparisons; 5 mathematical controls; 11 rejected inputs.
```

The second command prints `PASS_T21_BINOMIAL_PACKAGE controls=10`, followed
by successful relocation, regeneration and failed-run output-preservation markers.
`--write-certificate` regenerates the exact certificate; the default recomputes
it and requires an identical result. No network or third-party library is used.
The package also runs from an unrelated current directory after relocation.

In the pinned repository, add `--repository .` to the first command to compare
all eight source files with the checkout. This checks source bytes without
importing or executing the production arithmetic. It does not require the
current Git head to equal the base if those source bytes are unchanged.
An explicit check against a later, changed selection is expected to fail;
the default command continues to audit the frozen inputs.

## Exact arithmetic argument

For a child rank r, ambient arity m, and rational saving a in `[0,1]`, put
`x = 1-r/m`. The positive binomial expansion is

`(m/r)^a = sum_(k>=0) t_k`, with
`t_0=1` and `t_(k+1)=t_k*(a+k)*x/(k+1)`.

For `0 <= a <= 1`, `(a+k)/(k+1) <= 1`, so every ratio is at most x.
Consequently the tail after term k is bounded
above by `t_(k+1)/(1-x)`. The checker stores lower and upper term values as
integers over `2^240`, rounding every recurrence product outward. Positivity
allows summing those bounds directly; the rounded-up geometric tail is added
only to the upper sum. The stopping rule bounds that tail by `2^-170` per
power factor. Each returned interval is rational and explicitly encloses
the infinite series. Zero saving and a full-rank power factor are exact
special cases.

Dividing the inherited recurrence sum `sum_r c_r*r^(1-a)` by
`18816*73^(1-a)` gives the native normalized moment

`M(a) = sum_r c_r * r/(73*18816) * (73/r)^a`.

The conservative variant charges `32*73^2/10^16` additional rank-one
calls per paid child. Applying the same normalization gives the fallback

`32*73*sum_r(c_r)/(10^16*18816) * 73^a`.

The factor `73/r` is greater than one for every paid rank, and every weight
is positive. The moment is therefore continuous and strictly increasing in a,
so the two strict endpoint decisions bracket its unique root on the relevant
grid. This numerical statement takes the recurrence/fallback contract as an
input; it does not justify its construction-level realization.

## Profile and checked obligations

The proof's single-call profile `{1:2548,2:338,3:446,4:162,5:72,8:8}` is
multiplied by 189. Adding idle children `{48:6292,3:1,1:3}` reconstructs the
committed assembly profile exactly. There are 681782 children. The 21 replicas
use `9*21=189` local calls, live stock `8*112*21=18816`, and physical stock
`18816+504+8+2=19330`. These values are checked against the pinned construction
claim. Its rank mass is 1366848 and its deficit
is `73*18816-1366848=6720=21*320`.

| Price | Accepted lower endpoint |
| --- | --- |
| Native | `1664724476433282815289/10^24` |
| Conservative | `1664724473541313810689/10^24` |

Both successors at `+10^-24` are rejected. `CERTIFICATE.json` supplies the
exact residual intervals and term counts. `SOURCES.json` pins the assembly,
selected record, construction claim and proof. The assembly and proof hashes
are also checked against the selected record. Four additional source references
identify the pricing entrypoint and formula; both arithmetic-engine hashes
must match the assembly's recorded inputs. These source files are not imported.

The 450 algebraic checks use exact integer-power inequalities to verify the
enclosures at rational exponents with denominators at most three. They cover
every rank through arities 2, 3, 5, 7 and the actual arity 73, including the
slowest-decaying series at rank one. The five
model controls cover the zero-saving mass identity, an omitted rank-48
child, a dropped conservative surcharge, physical versus live-stock
normalization, and a redistribution preserving both call count and rank
mass. In the last case two rank-48 children become rank-47 and rank-49
children. The moment strictly decreases, as expected from concavity, despite
the unchanged totals. These are deliberately altered models; no defect in
the selected production checker is alleged.

Package controls use actual disposable copies. Corrupting any of the four
pinned inputs or the recorded certificate rejects. Deleting the geometric
tail or upper rounding fails the exact algebraic comparisons; undercharging
the fallback fails the strict endpoint test. These three implementation
mutations run with `--write-certificate`, so they cannot pass merely by
rejecting an old receipt. Every rejection is checked for its specific error,
and failed runs must preserve the existing certificate. Two synthetic
repository-fixture controls reject changed and missing reference files.
All ten controls run under `-O`; a relocated positive and exact certificate
regeneration also pass.

## Provenance, overlap and limits

OS-random assignment seed **69** selects the mathematical-audit track.
Candidate tasks considered: the complex moment accounting, the partial-bank
complement, and the outer assembly arithmetic. The first was selected for a
small, independent calculation with exact source binding. The scope and result
were recorded locally; no sprint coordination issue was identified.

[#678](https://github.com/CrocSwap/integer-mult-bounds/pull/678) by **0x-chad**
previously introduced binomial enclosures for the historical PR543 bit moment.
[#706](https://github.com/CrocSwap/integer-mult-bounds/pull/706) by **arkfx**
checks historical PR626 complex moments using integer roots, and
[#813](https://github.com/CrocSwap/integer-mult-bounds/pull/813) by
**Gareth Davidson / bitplane** independently checks the outer inequalities.
This contribution does not claim a new enclosure technique. It supplies a
separate implementation and exact native/conservative evidence for the
PR890 complex profile. The October 13, 2026 submission refresh identified
**navinor**'s concurrent
[#957](https://github.com/CrocSwap/integer-mult-bounds/pull/957), pinned at
`65c931415587c444a7a1f48939842c4cf0aa0411`. It transcribes the two retained
logarithm/exponential engines, adds a direct Decimal evaluation, and audits
endpoint-to-kappa reduction and surcharge attribution. This package corroborates
its complex endpoint conclusions using a different exact enclosure method;
it does not claim priority for the T21 endpoint audit. The focused search found
no other T21 binomial audit. PR942's pending T37 extension and PR947's
constant-row center-shear bound are distinct. PR813 has been incorporated for
its historical checkpoint. Search results are an overlap check, not an
exhaustive certification of all open work.

Construction credit belongs to **Chafik Boukhalfa** (PR890), **Jeremy Kothe**
(PR869/870), **Hao Yan** (PR858), **DreamingOfClouds**, **eumemic**,
**Rohan Arun**, **icekylinx**, and the repository's cumulative lineage.
Prepared for **David Breslauer** with substantial **OpenAI Codex** assistance,
under Apache-2.0. There is no independent human-review claim.

The preliminary subset was checked against a complete source checkout with
shallow Git history. `make selected-record-check` passes; this binds the
selection, its original source inventory and proof supplements. The separate
arithmetic audit and its controls also pass. See `VALIDATION.json` for the
recorded environment, commands and scope. No full `make verify`, supplier cold replay,
physical tape/owner audit, bit-supplier replay, 47-inequality outer replay,
Lean run or hosted CI success is claimed. All-size compilation, common-label
and mutable-source realization, whole-call hosting, precision/tape and
analytic-transfer obligations remain inherited.
