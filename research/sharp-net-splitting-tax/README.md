# Sharp net splitting tax: at most two quotient candidates

For `0<t<1`, the least coefficient in

```
q J^t + r^t - R^t <= N(t,sigma) R^sigma J^(t-sigma),
R=qJ+r>J,  0<=r<J,
```

is finite exactly for `sigma>=1`. At sigma=1 it is 1, approached but never
attained. For sigma>1, a strictly unimodal optimized quotient envelope reduces
all integer q>=1 to at most two adjacent candidates. Each candidate has one
maximizing remainder, characterized by a strictly decreasing scalar equation.
[PROOF.md](PROOF.md) gives the exact formula, attainment characterization,
and integer sharpness. This answers Open next question 2 of
[#6390](https://github.com/CrocSwap/integer-mult-bounds/pull/6390).

The q=1 reduction for the full split charge does **not** apply to the net tax.
For example,

```
N(1/2,3/2)=8/27,
q=2, s=r/J=1/4,
J=4d, R=9d  (every positive integer d).
```

The predecessor net coefficient in
[#4480](https://github.com/CrocSwap/integer-mult-bounds/pull/4480) is 1/2
at these parameters. More generally, `sigma=1+1/(2n)` has the unique best
quotient `q=n(n+1)` and remainder 1/4, proving that optimal quotients are
unbounded as sigma decreases to 1. A separate completing-square proof
confirms this family independently of the general envelope calculation.

The claim is a scoped written theorem with exact finite corroboration.
There is no new kappa, supplier inventory, selected-frontier update,
least tensor power, or claim of a globally optimal compiler.

## Exact characterization

Set `a=t^(1/(1-t))`. The unique positive root z of

```
(sigma-t)[(z+a)^t-a^t]=(sigma-1)z
```

determines the candidate quotients
`{max(1,floor(z)),max(1,ceil(z))}`, with duplicates removed. For each such q,
the unique maximizing remainder s in (0,1) satisfies

```
t q s^(t-1)+(t-sigma)s^t-sigma q+(sigma-t)(q+s)^t=0.
```

N is the maximum of `(q+s^t-(q+s)^t)/(q+s)^sigma` at those candidates.
Both equations admit rigorous monotone root bracketing. The theorem permits
a tie between adjacent candidates and does not assume nearest-integer rounding.

## Complete retained strictification

With the notation and native premises of #4433 and #4480, put `C=1-t`,
`u>=C`, `sigma=t+u`, `J=c^v`, `L=b^v`, and `h=C t^(t/C)`. The complete
sufficient test becomes

```
alpha^v + N(t,t+u) gamma^v + delta^v
                  + 2h epsilon^v - delta0^v < 1,
alpha=P_t/T_t,             gamma=P_(t+u)/(c^u T_t),
delta=B b/(c^C T_t),       epsilon=B c^t/T_t,
delta0=B b^t/T_t.
```

Only the original-paid net splitting coefficient changes. The full
nonnegative completion bound and the productive increment that justifies its
negative term remain. For sigma>1 the new coefficient is strictly smaller
than #4480's `Q=min(A,K)`, where `A=max(C/u,h)`; the simplification A=C/u
is not valid for every u. At sigma=1 both coefficients equal 1.

The verifier's small histogram example has raw target/paid moments 49 and 9,
original split tax 4, completion tax 2, and final gap 34. The retained complete
sufficient bound is exactly 75/98. This checks the accounting identity and
both charges; this toy histogram is not a native supplier admission.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
python3 -I -W error -B research/sharp-net-splitting-tax/verify.py
python3 -I -O -W error -B research/sharp-net-splitting-tax/verify.py
python3 -I -W error -B research/sharp-net-splitting-tax/independent_family.py
python3 -I -O -W error -B research/sharp-net-splitting-tax/independent_family.py
python3 -B scripts/research_package.py --package research/sharp-net-splitting-tax
python3 -B scripts/check_research_commit.py --package research/sharp-net-splitting-tax
```

Expected markers are `PASS_SHARP_NET_SPLITTING_TAX`,
`PASS_INDEPENDENT_NET_SPLIT_FAMILY`, `PASS_REGISTERED_RESEARCH_PACKAGE`, and
`PASS_RESEARCH_COMMIT_BYTES`. The primary verifier prints a fresh JSON receipt
bound to the package bytes and five frozen predecessor documents. It does not
write output files or treat a saved receipt as an oracle. The final command
requires committed publication bytes.

The primary exact checks cover 16 rational parameter pairs, 4,608 literal
integer splits, 109 optimized noncandidate quotients, 16 near-maximizing
integer witnesses, 16 exact families with 64 integer attainers, 35 rational
power enclosures, the complete-gap fixture, and 13 rejection controls.
The separate lead-authored checker covers 4,844 rational-radical fixtures
including 50 exact attainers and an omitted-raw-charge control. Neither imports
the other's implementation or any predecessor executable.

Every scientific comparison uses integers and rational intervals. The primary
checker uses 112-bit outward dyadic power enclosures and 44 stationary-root
steps. Its census covers t in {1/3,1/2,2/3,3/4}, sigma in {5/4,3/2,2,3},
1<=J<=8, 1<=q<=8, and every remainder. It checks rather than silently accepts
an inconclusive sign or exhausted finite bracket. The proof, not this finite
domain, supplies the all-real theorem. The exact family check extends through
n=16; the parameter-finding API intentionally has smaller denominator limits.

## Sources, scope and overlap

[SOURCES.json](SOURCES.json) pins canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, and frozen
source exports from #4433, #4480, #4832, and pending #6390. The latter is pinned
to `f9e68f40b0da7236a7fad415f7172218c0666d27`. Exports are byte-equal to their
source Git blobs and carry SHA256 hashes. The direct verifier needs only this
package; no pending commit, Git installation, network, or predecessor executable
is needed. Source export origin is documented, not an assertion that a foreign
pending commit is an ancestor of this package.

The assignment selected recursive interfaces using seed 53 and an explicit
portfolio override. [TASK.json](TASK.json) records changed scope from
`uniform-transfer-audit` to this compiler coefficient question. It discharges
none of the five selected-framework assumptions. The selected conditional
kappa remains .003125804 from #6030; the admitted ordinary BIT saving remains
.0034. Source-bound native, ownership/erasure, compiler closure, precision/tape,
analytic recovery, stock, and exact physical accounting remain inherited.

The session lead performed broader live overlap/orientation checks. This worker
also searched all-state PRs for `"net splitting" "sharp"` (only #6390) and
`"net tax" "coefficient"` (#6390, #5351, #4480, #5070). The latter two adjacent
compiler papers concern exit-law/logarithmic certificates, not this sharp
quotient/remainder objective. Narrow searches do not prove novelty over arbitrary
historical code, unpublished work, or the literature.

No selected cold replay, supplier native suite, actual physical caller, Lean,
Docker, or independent human review was run. [VALIDATION.md](VALIDATION.md)
records actual command outcomes and remaining limits; [REVIEW.md](REVIEW.md)
binds the separate agent reviews to exact proof and code hashes. Managed Python integers,
Fractions, and JSON allocate dynamically; fixed scientific loops and parameter
bounds constrain the replay, not hostile-filesystem behavior or all memory use.

## Open next questions

The [selected #6030 joint application](https://github.com/CubeJerry/integer-mult-bounds/blob/223ea940b604c1f8a2bd28093618628ba4a113a4/research/selected6030-smaller-compiler/JOINT-PROOF.md)
now supplies one source-bound numerical application with the complete splitting,
completion, compiler and outer accounting retained. It pins this theorem at
`a0ef8b7ae2592202247b15da453ce42598863a26`. That application is a follow-up,
not a proof or replay dependency of this theorem package; its inherited native,
physical and compiler obligations remain explicit.

- Apply N to further source-bound fully charged inventories that still use
  strictification. Reuse their exact moment enclosures and retain completion
  and the complete outer consumer. Identify the actual native, physical and
  compiler obligations that remain at each caller; a smaller sufficient rank
  does not discharge them.
- Characterize adjacent-quotient transitions more explicitly. Start by comparing
  the two optimized candidates for a fixed rational t as sigma varies. The
  present theorem is exact without a universal tie or transition classification.

## Credit

Prepared for @CubeJerry with substantial OpenAI Codex assistance in derivation,
implementation, and writing. The lead agent separately recovered the exact
half-exponent family, supplied the completing-square proof and independent
fixture checker, and reviewed the all-real and completion arguments. These are
author-side AI checks, not independent human or proof-kernel acceptance.

Nick Petalas's #4832 and #6390 supply the full-split predecessors and the open
net question. zxv's #4433 and #4480 supply higher-moment strictification and net
splitting/completion accounting. Cinna Davis's #4412/#4414/#4416 supplies the
chronological product/completion lineage; Jacob Alan Sussman supplies the finite
integer compiler. Their native/helper/controller/outer predecessors retain all
existing credit. Elementary calculus is classical; no literature-priority claim
is made. New work is Apache-2.0; frozen notices remain unchanged.
