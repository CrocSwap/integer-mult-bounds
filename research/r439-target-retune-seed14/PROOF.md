# One target insertion on the fixed PR967 mixed matrix

## Exact class and identity

Let K be the original 111-by-439 Boolean compensation matrix of the
selected PR589 word. Let E be the fixed product of the 306 PR915 target
transvections, and H the fixed product of PR967's 221 helper-star
transvections. In PR967 the middle matrix is `M = E K H^-1`; its helper
and target preparations and literal inverse restorations are all paid.

For distinct target indices a,b, define the transvection Q by
`(Q y)[a] = y[a] + y[b]`, with all other coordinates unchanged. Over F2,
`Q^-1=Q`. The new chronological circuit is

```text
H on helpers;
E on targets;
Q on targets;
inject Q M from helpers into targets;
Q on targets;
E^-1 on targets;
H^-1 on helpers.
```

Starting from arbitrary targets y and arbitrary helper dirt s, the state
immediately after injection is

```text
targets = Q E y + Q E K H^-1 H s = Q E (y + K s).
```

The remaining target steps restore `y + K s`, and helper restoration
returns s. Source registers are untouched throughout D. Thus the complete
D map is exactly `(x,y,s) -> (x,y+Ks,s)` without any clean-target or
clean-helper assumption. The unchanged suffix consequently retains the
full source-to-target endpoint. This proof requires the donor row after
helper mixing; using a donor from E K omits a mixed contribution and is
explicitly rejected by a negative control.

The searched class consists of zero or one such target transvection
inserted at this precise boundary, with fixed H and E, canonical direct
middle injections and a literal paid inverse. It does not include helper
omission, different helpers, more target insertions, a changed insertion
point, arbitrary middle circuits or a different target basis from scratch.

## Complete count and finite minimum

Only row a of M changes, to `M[a] xor M[b]`. Therefore the complete ADD
saving is exactly

```text
gain(a,b) = weight(M[a]) - weight(M[a] xor M[b]) - 2.
```

The final two counts pay preparation and restoration. All other D
operations, A/B/C, scatter, source access, helpers and frame paths are
retained. The class contains 12,210 directed pairs; both implementations
enumerate every one. The builder uses packed rows; the verifier rederives
M from source instructions and uses set symmetric differences. A SHA256
tie key of the UTF-8 string `14:a:b` fixes the ordering, including every
non-improving pair. The certificate binds the complete score/tie census.

There are twelve positive-gain pairs: one gains three, five gain two and
six gain one. Every other choice has gain at most zero and cannot improve
on the baseline, so full precision pricing is only needed for the twelve
positive nominees to determine the optimum. The complete literal word is
priced for every one of them. Ten pass both prefix bounds; two gain-one
choices fail the nine-stage bound, although each passes the local bound.

The unique gain-three pair is `(a,b)=(24,35)` and it passes. Thus 11,780
is the exact minimum in this stated class, both before and after imposing
the inherited local/nine-stage guards. The baseline without an insertion
costs 11,783. No random search, timeout or incomplete branch is used.

The chosen row decreases from 112 to 107 middle entries. Its whole D
invoice is

```text
221 + 307 + 4504 + 307 + 221 = 5560.
```

The unchanged remainder costs 6,220 ADDs, for 11,780 in total. Before
helper mixing, applying the same row operation to E K has gain -18;
the coupled choice is not a remaining profitable step on the original
PR915 target problem. This is the concrete change of mechanism.

## Precision and exact resource preservation

Both implementations replay the entire positive word in forward and
inverse directions. The independent verifier lowers all multi-source
gates to elementary ADDs and makes COPY/ERASE explicit. For both parent
and candidate the resulting maxima are

```text
F = 72847, B = 10394084,
64 F^3 B^2 = 2672929057893220568931365420032 < 2^104,
2^18 F^5 B^4 =
6276870480677531528435239117197771736166837152483102425088 < 2^192.
```

The staged formula and 18-bridge specialization for K=4, as well as the
192-bit charge, are checked against the pinned supplier sources. These
are exact integer inequalities, not rounded bit-length admission. The
existing very small margin is unchanged. The rejected pairs `(105,98)`
and `(52,59)` have B values 10,602,110 and 10,566,138 respectively and
fail the same exact staged inequality.

The unchanged source exporter emits 14,709 records instead of 14,712.
After removing ADDs, the entire record sequences are identical, including
all 2,911 MOVEs, nine COPYs and nine ERASEs. The charged rank mass remains
5,129. Every non-D word field is identical to PR589 and PR967, and all
new operations are at frame zero on already available target registers.
There is no new helper, source-access operation, copied total, recursive
child or restoration expense to omit. The recursive profile is unchanged.

## Independent checks and limitations

The main verifier imports no builder or predecessor compensation code.
It reconstructs the recipe from pinned data, checks every changed middle
entry, and uses set-valued formal inputs to replay the D map and complete
word for all 661 independent columns in both directions. It separately
runs the unchanged PR589 geometry/interface checker on parent and
candidate, and the unchanged Python record exporter. The checker reports
exactly the inherited syntactic H2 and literal K-extraction failures;
H1/H3/H4/H5 and the other decomposed conclusions pass. These failures are
not converted into a claim of the original interface lemma.

The supplied evidence admits a local finite semantic-D substitution and
its two stated prefix inequalities. It does not include native 5/9/11
stage compilation/replay, a changed whole-hosted supplier, full invoice
or outer assembly. Those, along with inherited all-size/compiler,
realization, precision/tape and analytic obligations, remain open for
adoption. There is no new kappa or runtime claim.

PR915/926's target and two-sided compensation and PR967's restored helper
stars are essential predecessors. Their circuits and source files remain
unchanged; see NOTICE.md for attribution and SOURCES.json for exact pins.
