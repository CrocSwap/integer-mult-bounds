# Precision-capped cuts and cancellable output returns

**Scoped recursive-interface construction and exact finite optimization; no new kappa.**
On Sagar Thakrar's fixed PR1537 example, intermediate cuts plus one
disjoint-register cancellation give **2,222 scalar instructions with exact
prefix row-L1 peak 3,958**, compared with the original **2,234 instructions and
peak 4,195**. The new word fits a magnitude allowance of 12 extra bits; the
original needs 13 under the same row-L1 criterion. These are operation and
coefficient bounds, not a measured runtime improvement or rounded admission.

The primary target was cap 256, one extra magnitude bit over the eager
reference. **That target fails in the declared class.** All permitted
partitions still cost at least the eager 2,494 operations below cap 788.
The certificate gives the entire 35-breakpoint frontier and separately retains
the 31-breakpoint control frontier without the cancellation.

## Fixed object and scope

Base: `64039f1bd3b6a523b96083fd858ad040a75e3030`. Assignment seed: **55**, drawn
with `secrets.randbelow(100)`. Predecessor: PR1537 at
`407f00df6ca0bf86b455b5640f18ec2f62ee77b9`. Its unchanged fixture uses seed 53,
53 children and five shear pairs; changing those would be another experiment.
The assignment seed selects cap 256 and the small cross-check fixtures,
not independent search coverage.

Work over exact rational components. Put

    J = [[0,1],[0,0]], Q=I+J, P=diag(Q,Q,Q,Q,Q), N=10, d=2.
    C_i(D,W) = (D+R_i W, P W), R_i P = Q R_i.

Each fixed child includes its trailing drift. D, preserved source X and dirty
workspace U are disjoint. All children and their literal inverses are paid.
ADD means `u += v` or `u -= v`; SCALE means exact doubling or halving. The
optimization prices both at one. It does not optimize arbitrary linear
circuits, change reader order or the power recipe, fuse inside children, or
permit an observer to inspect an unnormalized midpoint.

Schedules partition the ordered children into contiguous nonempty intervals.
Each interval uses PR1537's literal binary-power return. Interior interval
boundaries are canonical. The final interval may omit its output return and
matching inverse, as proved below. There are exactly `2^52` partitions. This
is a finite class, not an all-algorithm lower bound. The original pure
canonical class is also checked as a control.

## Deleting a return pair at the echo midpoint

Write a canonical group in chronological order as `H; C`, where C is its
terminal output-only return `Q^(-(ell-1))`. H has already restored W. If L is
the source unload `U -= X`, the full echo contains

    copy; earlier_groups; H; C; L; C^-1; H^-1; earlier_groups^-1.

C and L act on disjoint registers, so they commute: `C; L; C^-1` equals L.
Deleting the two return words preserves every final register for arbitrary
dirty inputs. The output at the midpoint can differ; a canonical observation
there prohibits this rewrite. A control also shows that an unload touching
D invalidates the argument.

Deletion cannot increase the maximum row-L1 norm. During the shortened
unload, D has the state already seen before C, while X,U have the states seen
during the original unload. Every row's norm therefore already occurred in
the original word. Retained prefixes outside the substring agree, and the
same argument applies to the literal inverse. Thus always deleting the final
return suffices for the optional-deletion optimum. This uses disjoint registers
and a rowwise bound, not a rounding theorem.

For the uncut word, deleting six ADDs and twenty SCALEs gives **2,208
operations**, with the same peak 4,195. This directly improves PR1537's invoice;
it does not refute that predecessor's restricted unit-power lower bound.

## Complete interval coverage

Let `S_t=sum_(i<t) R_i` and `S=S_53`. In the original D,X,U coordinates,
the four canonical states at a cut t are:

| Portion of the complete echo | Output | Workspace |
| --- | --- | --- |
| Forward word, forward groups | `D+S_t(X+U)` | `X+U` |
| Forward word, inverse groups | `D+S X+S_t U` | `U` |
| Inverse word, forward groups | `D+S_t U` | `U` |
| Inverse word, inverse groups | `D+(S_t-S)X+S_t U` | `X+U` |

These states depend on cut position, not earlier partition choices. For every
ordinary interval `[a,b)`, the checker propagates its literal ADD/SCALE word
from all four states, checks the endpoint and records every prefix row.
It obtains a path-independent maximum f(a,b).

An interval ending at 53 instead executes the entire fused middle
`H; unload; H^-1` from the forward-group state at a, and
`H; copy; H^-1` from the inverse-group state at a. Their endpoints must equal
the corresponding inverse-group states at a in the table. This checks the
unnormalized midpoint directly. All other intervals retain four-state checks.
The outer copies are covered at adjoining endpoints: each workspace row
changes between U and U+X and has norm at most two.

At cap B, keep precisely edges with `f(a,b)<=B`, assigning the one-sided
boundary ADD+SCALE cost after final-edge cancellation. Then

    dist[0]=0,
    dist[b]=min_(a<b, f(a,b)<=B) (dist[a]+cost(a,b)).

Every partition is a path from 0 to 53, and every such path gives one allowed
word. The child/copy bill is fixed. Induction on b proves optimality. Saved
distance vectors are lower-bound witnesses: the checker verifies every
applicable edge inequality and equality along an exhibited path.

Thus **1,431 interval evaluations cover all `2^52` partitions** through the
stated decomposition proof. They are not `2^52` separately replayed words,
a randomized search, or a proof-assistant formalization. The peak is integer;
the objective changes only at an edge peak, so sweeping every such value
gives the full cost-versus-cap frontier.

Fresh output dirt is not a valid interval shortcut. For `[20,36)`, it gives
peak 587 while the accumulated forward state gives 694. The verifier retains
this discrepancy as a rejection control.

## Complete scalar bill and results

Set `u(t)=popcount(t)` and `v(t)=2 floor(log2(t))`, both zero at t=0.
For interval length ell, the canonical boundary costs

    a(ell,m) = ell-1 + m*u(ell) + u(ell-1),
    s(ell,m) =         m*v(ell) + v(ell-1).

For the final interval, subtract `u(ell-1),v(ell-1)` for the deleted return.
Sum these one-sided interval bills to A_B,S_B. The 53 unchanged leaves cost
972 ADDs per direction, including drift. Both source transfers cost 20 ADDs.
The complete echo therefore has

    ADD = 1964 + 2 A_B,   SCALE = 2 S_B.

| Word / cap | ADD | SCALE | Total | Forward peak | Inverse peak |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eager reference | 2494 | 0 | 2494 | 87 | 65 |
| PR1537 uncut | 2114 | 120 | 2234 | 4195 | 2391 |
| Cancellation only, uncut | 2108 | 100 | 2208 | 4195 | 2391 |
| Optimal at cap 256 or 512 | 2494 | 0 | 2494 | 87 | 65 |
| Optimal at cap 1024 | 2182 | 248 | 2430 | 1013 | 1011 |
| Optimal at cap 2048 | 2108 | 200 | 2308 | 2018 | 1519 |
| Optimal at cap 4096 | 2122 | 100 | **2222** | **3958** | 2235 |
| Unconstrained optimum | 2106 | 100 | **2206** | 4116 | 2339 |

The cap-4096 cuts are `[1,2,3,53]`, lengths 1,1,1,50. The unconstrained
optimum is `[1,53]`. The first strict saving occurs at cap **788**; cap 787
still costs 2,494. In the pure canonical control, `[52,53]` keeps the original
2,234-operation total while reducing the peak to 3,932.

For all dirty inputs with coordinate magnitudes below `2^b`, multiply the
listed peak by `2^b`. Every prefix matrix in both directions is integral,
including each halving. This exact-grid calculation needs no new fractional
bits. Rounding, signed encoding and physical overflow remain separate.

The tariff matters. Relative to the original uncut word, the cap-4096 word
adds eight ADDs and removes twenty SCALEs. At common adequate width it is
cheaper exactly when `SCALE/ADD > 2/5`. Against eager execution it saves
`372*ADD-100*SCALE`. The certificate optimizes only equal prices; different
width-dependent bit costs are not identified with these scalar counts.

Every ADD reads two data coordinates and every SCALE one; each writes one.
Each instruction record, including its coefficient and addresses, is read
once. The cap-4096 word has **4,344 data reads, 2,222 data writes and 2,222
instruction reads**. No zero scratch or power oracle is hidden.

Preparation and planning are additional. The fixed instance has 1,060 leaf
coefficient slots, and its 53-child schedule is independent of input data.
For M supplied coefficients, emitted length L and height h, materializing the
word retains `O(M+(h+1)L)` preparation and `O(M+L+h)` compiler storage.
The cap planner additionally performs the explicitly recorded interval
replays and shortest-path sweeps; charge that work if recomputing per input.
No end-to-end speedup or amortization is asserted. Physical routing, descriptor
layout, bit arithmetic and hosting have not been implemented or priced here.

## Recursive composition

Appending P on the preserved source turns a completed echo back into the
original child type. The reader sum still intertwines P and Q. For specified
partitions at each node, including inverse descendants and all source copies,

    A_node = 2 sum_i A_i + 2N + 2 A_B + m,
    S_node = 2 sum_i S_i      + 2 S_B.

The root omits `+m`. For fixed arity k, equal child costs and fixed nonrecursive bill g,
`T_h=2k*T_(h-1)+g`, whose solution is
`(2k)^h*T_0 + g*((2k)^h-1)/(2k-1)`. Storage is `d+(h+1)N` coordinates.
A nested three-by-seventeen fixture costs **4,720 versus 4,960** operations.
Its complete endpoint and inverse are checked on all 32 dirty coordinates.

**Local caps do not automatically compose.** Nested peaks are recomputed as
1,267 forward and 1,103 inverse, versus eager 85 and 81. The 53-leaf cap is
not transferred to that caller. The recurrence has no proved relationship
to multiplication input size and is not a contracting supplier profile.
No actual indivisible selected child is identified. If these toy leaves can
be opened, their summed reader can be evaluated more cheaply; the fixed-child
restriction is essential. Common precision/tape admission and analytic
transfer remain open.

## Reproduction and evidence

From the repository root, Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/unipotent-precision-cuts-seed55
```

Expected: `PASS_PRECISION_CAPPED_UNIPOTENT_CUTS`, four passing package tests,
then `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
Standalone: `python3 -I -O -B research/unipotent-precision-cuts-seed55/verify.py`.
`--emit` prints a recomputed receipt; the default compares every field with
[RESULT.json](RESULT.json) and writes nothing.

Evidence includes the two complete fixed-instance frontiers; a separate
eager-map derivation of 216 canonical states; a Fraction column interpreter
on three full fused words and their inverses (132 basis columns); six attaining
sign inputs; exhaustive small partitions including a profitable planner
control; nested composition; and nine mathematical rejection controls.
Artifact tests cover source corruption, a false saved peak, dual tampering
and read-only relocation in a path with spaces. RESULT.json records the exact
completed domain and counts. Both implementations were written in the same
AI-assisted session, not by independent human reviewers.

No selected-supplier cold replay or full multiplication formalization is
claimed. The selected PR1094 record and upstream inputs are unchanged; the
cheap source-binding check is separate from mathematical replay. See
[VALIDATION.md](VALIDATION.md) for executed checks and omissions.

## Provenance and credit

The final refresh found Hanson's concurrent [PR1552](https://github.com/CrocSwap/integer-mult-bounds/pull/1552)
at `4db7213c90288b1eb83983e08c5ef401d19b7844`. It already reports the 52+1
reset, the complete 31-point canonical frontier and the cap-788 obstruction.
All 31 of its `(cap, boundary cost)` pairs agree with this package's control.
Those results are independently corroborated here, with no priority claim.
The distinct contribution is the **disjoint terminal-return cancellation and
its 35-point frontier**, including 2,222 operations at cap 4,096 and the
2,206-operation unrestricted minimum in the extended class. No PR1552 code
is imported. [OVERLAP.json](OVERLAP.json) records the exact comparison and
search coverage; code diffs and every historical closed PR were not searched.

[PREDECESSOR.json](PREDECESSOR.json) pins PR1537's original README, model and
receipt by SHA256 and Git blob at its exact head. Those bytes and attribution
are unchanged in `sources/`. The instruction emitter and fixture are reused
openly. New work comprises the contextual cap proof, commutation application,
cut planner, scalar-column oracle and certificates.

Credit **Sagar Thakrar / PR1537** for the infinite-order construction, paid
binary returns, original precision measurements and reset-cut follow-up;
**Ross Richardson / PR1287 and PR889** for output frames and dirty echoes;
and **Sagar Thakrar / PR1227** for sign frames. Selected context remains Rohan
Arun's PR1094 on Jeremy Kothe's packing, Hao Yan's T16 controller and the
retained PR589/555 bit lineage. No priority is claimed for output transport,
dirty cancellation, dynamic programming or disjoint-gate commutation as
techniques.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in derivation, implementation, verification and prose. Apache-2.0. Emulate
had 18 word credits, below the 40-word minimum, so its writing style pass
was unavailable. Prose was compared directly with sources and receipts.
No independent human review or proof-assistant verification is claimed.

## Open next questions

1. Does an actual indivisible supplier child expose this drift and admit the
   cancelled midpoint without an observer? Inspect one concrete call and price
   source access, precision and hosting. No such selected child is supplied.
2. Can this cut-state method optimize a nested caller at a global cap? Start
   with the supplied three-by-seventeen fixture and include caller output in
   the boundary states. Local caps are insufficient; global nested optimality
   is not established here.
