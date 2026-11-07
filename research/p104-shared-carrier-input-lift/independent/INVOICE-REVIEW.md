> **Retained #6805 review.** This text and its numbers describe the #6805 word it was written for. The lifted word here has 66,888 paid requests and paid rank mass 178,044; see `RESULT.json` and `VALIDATION.md`.

# Independent complete caller and allocation review

**Qualified pass.** The new native word composes with the literal final #6726
caller after allocating and charging eighteen additional independent helper
fields. The complete price has 13,688 productive fields, 66,870 paid requests,
and rank-mass surplus 760. The corrected complete ordinary upper bound is
535,415,008, strictly below one billion.

**Ordinary-accounting correction:** the earlier version of this review
incorrectly described 252,223,008 as complete. That was a partial estimate:
it omitted explicit full-carrier canonical-job adapters for whole idles,
main targets and thin queries. Existing audit #6763 at commit
`c3e0500c7645b1bc228ebe5e5190e304a2da46ca` identified those charges. They
have now been independently reconstructed here from the literal caller.
This correction does not change the Gaussian histogram, root diagnostic,
field allocation or the retained one-billion ordinary cap.

`check_invoice.py` imports only the separately written `check_native.py`.
It imports no parent constructor, caller evaluator, pricing module or interval
engine. Normal Python and `python -O` produce identical results. This is a
separately written AI audit, not independent human acceptance or proof-kernel
certification. The candidate gzip SHA-256 remains
`2a9f93a82993b85625df20751cc8027d70a85e1fb4278187adbea520909a2e4e`.

## Literal identity and full caller map

The correct final literal is `retained/caller/CONTROLLER.json`: 34 roles,
18 stages, 606 events and ambient rank 153. `CALLER-ONE-RETIRED.json` has
33 roles and 592 events and is only an intermediate. Starting from
`CALLER-UNRETIRED.json`, this checker independently inverts the witness
bases, renames the suffix pivot, updates the declared targets, and reconstructs
both complete files exactly. It checks that each fresh caller field is
untouched before its handoff and the corresponding retired field is untouched
afterward.

A new reverse-adjoint evaluator then reconstructs all 34 by 34 coefficients
over `Q(i)[q,C1,...,C18]/(q^4-1)`. Every arbitrary-input column equals the
declared diagonal target, including both new caller inputs. This evaluator
does not share the retained caller evaluator's forward implementation.

The literal census is ADD 275, SCALE 86, SWAP 94, LAMBDA 100, LOCAL 18,
QUERY 15, IDLE 12 and IDLE_ONE 6. The eighteen LOCAL events use stages 1
through 18 exactly once, in order, with distinct source and destination
roles. Each charges one complete new native word. The fifteen thin queries
charge 104 rank-one requests each. Whole idle jobs charge ranks 8, 16, 32,
40 with multiplicities 208, 1664, 1040, 208, respectively.

All 3,536 main targets are counted directly from the 34 diagonal exponent
vectors and 104 ports. Their ranks are 1, 9, 17, 32, 33, 41, 73, 145 with
multiplicities 104, 208, 1664, 208, 832, 208, 208, 104. The old native word
with this same literal caller independently reproduces the retained #6726
invoice exactly.

## Complete new histogram

| Rank | Productive targets | Paid requests |
|---:|---:|---:|
| 1 | 356 | 41736 |
| 2 | 144 | 8172 |
| 3 | 72 | 8820 |
| 4 | 1962 | 1962 |
| 5 | 306 | 2754 |
| 6 | 54 | 126 |
| 7 | 162 | 162 |
| 8 | 720 | 226 |
| 9 | 6688 | 0 |
| 16 | 0 | 1664 |
| 17 | 1664 | 0 |
| 32 | 208 | 1040 |
| 33 | 832 | 0 |
| 40 | 0 | 208 |
| 41 | 208 | 0 |
| 73 | 208 | 0 |
| 145 | 104 | 0 |

Thus the literal complete differences are

\[
\Delta T=18(H_4+H_5-H_9),\qquad
\Delta P=18(H_1+H_5-H_6).
\]

The paid rank mass is 178,080 and the target rank mass is 178,840.
Every native call contributes the independently checked strict concavity
gain from `REVIEW.md`; no other caller mechanism changes.

## Constructive allocation and arbitrary-input compatibility

Number the caller's main fields by `104 * role + port_index`, giving IDs
0 through 3535. List the 564 native helper roles in increasing order. In
LOCAL stage `s`, assign helper ordinal `j` the global ID

\[
3536+(s-1)564+j.
\]

For the native main roles, map `live[port_index]` to the caller source and
`live[port_index]+112` to its destination. Each invocation's 772 public
roles map injectively; its helpers are disjoint from every main field and
from all other invocations' helper blocks. The checker explicitly builds
all eighteen maps. Together they use 10,152 independent helpers and 3,536
main inputs, totaling 13,688 public inputs. This is eighteen more helpers,
not eighteen more helpers per port: the native word already contains all
104 ports.

Reserve IDs 13688 through 13716 for the 29 owned labels and ID 13717 for
the separately uncredited thin-query scratch. Local invocations and thin
queries are sequential. All native owned lifetimes finish inside their
invocation, so these labels can be reused without aliasing any independent
input or retained output. There are 13,718 reserved field slots. All IDs
still fit in fourteen bits.

The independent local all-column audit establishes the key substitution
contract: in native charts, the 208 main roles have the original main map,
the 564 helper roles have the identity map, and all cross terms between
the two blocks vanish. Each helper output depends on its own arbitrary
input alone. The main input need not be pristine; it may be any linear
combination supplied by the caller, because the local identity and COPY-zero
guard were checked for arbitrary public inputs.

Consequently, after mapping a call to its disjoint global fields, its helper
block is independent of the caller's continuing main calculation. Although
the native implementation temporarily mixes roles, its returned main block
is exactly the one required by the existing LOCAL event. The complete caller
therefore extends by independent helper identities in normalized charts.
The new helper is supplied as an arbitrary input in initial chart 243 and
returns in chart 127. It is never initialized to zero, borrowed from a main
idle direction, or hidden in owned scratch. Native helper368 now returns at
chart243. The actual boundary operators for these charts still need the
native phase verifier; the normalized linear identity alone cannot replace
that check.

## Ordinary work and normalizers

Every invocation charges two boundary normalizers for each of its 564
helpers: 1,128 normalizers per call, 20,304 across the caller. This includes
the new helper's two normalizers and the changed helper368 endpoint. The
total increase is 36 helper normalizers, eighteen paid MOVE jobs and
18 times 384 scalar units.

The complete local count is

\[
138374+1000(3455+1128+208+416+4\cdot47)=5533374<10^7.
\]

The summands count native paid routes, helper normalizers, 208 main adapters,
four contacts for each of 104 ports, and four routes for each owned lifetime.
The 1000-unit route rate is an inherited physical/tape contract for each
native fixed whole-job map or elementary map on at most 17 specified axes.
It does not give a single 1000-unit charge for an arbitrary permutation of
the complete 153-axis carrier. The local count above must therefore be
supplemented by the explicit full-caller adapters below.

The complete caller's ordinary scalar calculation gives 3,526 real work
units and 2,280 coefficient-height units per port. Every actual gate fits
the 32-unit envelope; the maximum literal ADD/SCALE magnitude here is 6.
Scanning all 34 main roles at every one of 606 caller events costs at most
`32 * 34 * 104 * 606 = 68,570,112`. All fifteen thin queries charge another
24,960 units. The ordinary scalar part of all 3,536 main output normalizers
charges another `3536 * 26 = 91,936` units.

For a job on the coordinate set I of rank r, let C be the first r coordinates.
The sets `C minus I` and `I minus C` have the same size. Pairing their elements
gives disjoint two-axis swaps; the checker explicitly constructs the resulting
permutation, verifies that it sends C to I, and verifies its inverse. Every
job pays for both boundary permutations. Each selected fresh stage contributes
coordinates `9 + 8*(stage-1)` through `9 + 8*stage - 1`.

If the job also carries central q, a fixed map on the original nine axes sends
q to coordinate zero and its orthogonal complement to coordinates one through
eight. Its inverse is paid at the other boundary. The independent checker
checks the Gram matrix and reconstructs every one of the 512 addresses for
each of the 104 actual q bases. A negative q exponent additionally pays one
ordinary translation, since `Q^-1 = Q * Q^2` and `Q^2` is translation by q.
The same two basis maps and negative-exponent translation are charged for
each inverse thin query.

The complete inventory derived without importing the retained physical audit is:

| Canonical adapter | Elementary maps |
|---|---:|
| Main input/output two-axis swaps | 144,768 |
| Main input/output nine-axis q-basis maps | 6,656 |
| Main endpoint phase translations | 3,328 |
| Whole-idle input/output two-axis swaps | 127,296 |
| Thin-query input/output q-basis maps | 3,120 |
| Thin-query phase translations | 1,560 |
| **Total** | **286,728** |

The maps have support at most nine axes each, even though their composition
can act on the full carrier. Charging the retained 1000-unit rate separately
for each map gives 286,728,000 units. This replaces the former flat
`3536 * 1000 = 3,536,000` main-output route term; it is not added on top of
that obsolete term. The net correction to the partial estimate is therefore
283,192,000. It already applies to the predecessor's same caller, rather
than arising from the new helper split.

The conservative complete bound is therefore

\[
18\cdot10^7+68570112+24960+91936+286728000=535415008<10^9.
\]

Substituting the counted local work gives 455,015,740. The native change adds
60,912 relative to the old native word under the same fully charged caller
adapter inventory. The 1,128 helper normalizers per invocation remain in the
local count and are not replaced by these main/idle/query conversions.
The Gaussian ranks and the one-billion cap are unchanged, so the earlier
exact moment and final-parameter conclusions survive the corrected invoice.

## Independent numerical diagnostic and scope

A separate 110-digit Decimal evaluator, with no retained interval code,
finds the raw crossing

\[
\kappa_{\mathrm{raw}}
\approx0.00330814518914275077684453840250387824668768225786645.
\]

The old raw crossing is approximately
`0.00330724468485362459737980198976843209518931940083131`.
Their difference is approximately `0.0000009005042891261794647364`.
The final proposed eight-decimal claim is **0.00330814**, with tested price
**0.003308145**. The diagnostic signed margins are respectively
0.0011842144282776484 and 0.000043164272593392920. These remain diagnostics,
not exact rational interval certificates or completed compiler/outer
admission.

The primary package's already certified raw lower endpoint is
`0.0033081451891`; the inspected receipt has positive lower-endpoint
margin `0.000000009756156009235365099032` in each exact interval engine.
Independently checked rational arithmetic gives

\[
0.00330814 < 0.003308145 < 0.0033081451891,
\]

\[
0.0033081451891-0.003308145=1891/10^{13}>0,
\qquad
\frac{0.003308145-0.00330814}{7}=1/1400000000.
\]

Thus the tighter claim preserves the exact compiler grid gap. With the
same power 1920 and reserve `1e-27`, the finite strictification inequality
`1 / (1 + 1920 * reserve) + 4 * (31/32)^1920 < 1` and the rank-rounding
inequality `11^64 < 12^63` still hold by exact rational/integer arithmetic.

At the tighter tested price, the separate Decimal diagnostics give
`1-alpha = 2.4374197157291656e-10`, over `2.4e17` times the reserve;
`gamma = 0.9193522426688072` and `delta = 0.9201996372770363`, both below
`31/32 = 0.96875`. The compiler complement diagnostic is
`eta = 1.8635150721153376e-14`, above
`(63/64)^2100 = 4.3371903853167193e-15`. The narrower distance to the raw
crossing therefore causes no meaningful reserve or completion concern.
There is no independent arithmetic objection to using the tighter claim,
provided the primary package reruns both exact interval engines and the
complete compiler/outer chain at these final parameters. None of the
native/caller words, histograms, allocation or ordinary invoices changes.

Five negative controls reject the intermediate one-retirement caller,
an omitted LOCAL call, one reversed thin-query orientation, aliased native
main roles, and the obsolete 563-helper allocation. Normal and optimized
execution agree byte for byte. Native absolute phase/all-column admission,
both exact interval engines, completion tails, the compiler, BIT compatibility
and the complete outer ledger remain the primary package's responsibilities.
The inherited owned-erasure and other framework assumptions are unchanged;
this review does not establish scientific admission or change the selected
frontier.

Reviewed for @CubeJerry with substantial OpenAI assistance. Credit Ali
Romman for the helper-basis mechanism, DreamingOfClouds for #6702, zxv for
#6726, and the retained native, caller, compiler, BIT and analytic authors.
Apache-2.0.
